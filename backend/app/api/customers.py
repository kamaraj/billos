"""Customers API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_tenant_id
from app.models.customer import Customer
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse, OutstandingCustomer
)

router = APIRouter(prefix="/api/customers", tags=["Customers"])


@router.get("/", response_model=List[CustomerResponse])
async def list_customers(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    with_balance_only: bool = False,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """List all customers for the tenant."""
    query = db.query(Customer).filter(
        Customer.tenant_id == tenant_id,
        Customer.is_active == True
    )
    
    if search:
        query = query.filter(
            (Customer.name.ilike(f"%{search}%")) |
            (Customer.phone.ilike(f"%{search}%"))
        )
    
    if with_balance_only:
        query = query.filter(Customer.current_balance > 0)
    
    customers = query.offset(skip).limit(limit).all()
    return customers


@router.post("/", response_model=CustomerResponse)
async def create_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Create a new customer."""
    customer = Customer(
        tenant_id=tenant_id,
        name=data.name,
        phone=data.phone,
        email=data.email,
        address=data.address,
        gst_no=data.gst_no,
        credit_limit=data.credit_limit
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/outstanding", response_model=List[OutstandingCustomer])
async def get_outstanding_customers(
    min_days: int = 0,
    min_amount: float = 0,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Get customers with outstanding balance (for Credit Risk Agent)."""
    customers = db.query(Customer).filter(
        Customer.tenant_id == tenant_id,
        Customer.current_balance > min_amount,
        Customer.is_active == True
    ).all()
    
    result = []
    for c in customers:
        # Calculate days overdue from oldest unpaid invoice
        oldest_unpaid = db.query(Invoice).filter(
            Invoice.tenant_id == tenant_id,
            Invoice.customer_id == c.id,
            Invoice.balance_amount > 0
        ).order_by(Invoice.invoice_date.asc()).first()
        
        days_overdue = 0
        if oldest_unpaid:
            days_overdue = (datetime.now().date() - oldest_unpaid.invoice_date).days
        
        if days_overdue >= min_days:
            result.append(OutstandingCustomer(
                customer_id=c.id,
                customer_name=c.name,
                phone=c.phone,
                due_amount=c.current_balance,
                days_overdue=days_overdue,
                risk_tag=c.risk_tag
            ))
    
    return sorted(result, key=lambda x: x.days_overdue, reverse=True)


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Get a specific customer."""
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.tenant_id == tenant_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    data: CustomerUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Update a customer."""
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.tenant_id == tenant_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    customer.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/{customer_id}/ledger")
async def get_customer_ledger(
    customer_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Get customer transaction ledger."""
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.tenant_id == tenant_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get invoices and payments
    invoices = db.query(Invoice).filter(
        Invoice.tenant_id == tenant_id,
        Invoice.customer_id == customer_id
    ).order_by(Invoice.invoice_date.desc()).limit(50).all()
    
    payments = db.query(Payment).filter(
        Payment.tenant_id == tenant_id,
        Payment.customer_id == customer_id
    ).order_by(Payment.payment_date.desc()).limit(50).all()
    
    # Build ledger entries
    ledger = []
    
    for inv in invoices:
        ledger.append({
            "date": inv.invoice_date.isoformat(),
            "type": "INVOICE",
            "reference": inv.invoice_no,
            "debit": inv.total_amount,
            "credit": 0,
            "description": f"Invoice #{inv.invoice_no}"
        })
    
    for pay in payments:
        ledger.append({
            "date": pay.payment_date.isoformat(),
            "type": "PAYMENT",
            "reference": pay.reference_no or pay.id[:8],
            "debit": 0,
            "credit": pay.amount,
            "description": f"Payment via {pay.payment_mode}"
        })
    
    # Sort by date
    ledger.sort(key=lambda x: x["date"], reverse=True)
    
    return {
        "customer_id": customer_id,
        "customer_name": customer.name,
        "current_balance": customer.current_balance,
        "credit_limit": customer.credit_limit,
        "ledger": ledger
    }
