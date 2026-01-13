"""Invoices API endpoints - Core billing functionality."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date, timedelta

from app.core.database import get_db
from app.core.auth import get_current_tenant_id
from app.models.invoice import Invoice, InvoiceItem
from app.models.product import Product, InventoryTransaction
from app.models.customer import Customer
from app.models.payment import Payment
from app.schemas.invoice import (
    InvoiceCreate, InvoiceResponse, InvoiceSummary,
    PaymentCreate, PaymentResponse
)

router = APIRouter(prefix="/api/invoices", tags=["Invoices"])


def generate_invoice_number(db: Session, tenant_id: str) -> str:
    """Generate next invoice number."""
    today = date.today()
    prefix = f"INV{today.strftime('%y%m')}"
    
    # Get count of invoices this month
    count = db.query(func.count(Invoice.id)).filter(
        Invoice.tenant_id == tenant_id,
        Invoice.invoice_no.like(f"{prefix}%")
    ).scalar()
    
    return f"{prefix}{(count + 1):04d}"


@router.get("/", response_model=List[InvoiceResponse])
async def list_invoices(
    skip: int = 0,
    limit: int = 50,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    customer_id: Optional[str] = None,
    payment_status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """List invoices with filters."""
    query = db.query(Invoice).filter(Invoice.tenant_id == tenant_id)
    
    if from_date:
        query = query.filter(Invoice.invoice_date >= from_date)
    if to_date:
        query = query.filter(Invoice.invoice_date <= to_date)
    if customer_id:
        query = query.filter(Invoice.customer_id == customer_id)
    if payment_status:
        query = query.filter(Invoice.payment_status == payment_status)
    
    invoices = query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()
    
    # Add customer names
    result = []
    for inv in invoices:
        inv_dict = inv.__dict__.copy()
        if inv.customer:
            inv_dict["customer_name"] = inv.customer.name
        result.append(InvoiceResponse(**inv_dict, items=[]))
    
    return result


@router.post("/", response_model=InvoiceResponse)
async def create_invoice(
    data: InvoiceCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Create a new invoice - main billing endpoint."""
    
    # Validate customer if provided
    customer = None
    if data.customer_id:
        customer = db.query(Customer).filter(
            Customer.id == data.customer_id,
            Customer.tenant_id == tenant_id
        ).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Check credit limit for credit sales
        if data.payment_mode == "CREDIT":
            available_credit = customer.credit_limit - customer.current_balance
            # We'll check after calculating total
    
    # Create invoice
    invoice = Invoice(
        tenant_id=tenant_id,
        customer_id=data.customer_id,
        invoice_no=generate_invoice_number(db, tenant_id),
        invoice_date=date.today(),
        due_date=date.today() + timedelta(days=30) if data.customer_id else None,
        invoice_type=data.invoice_type,
        is_gst_invoice=data.is_gst_invoice,
        discount_percent=data.discount_percent,
        notes=data.notes
    )
    db.add(invoice)
    db.flush()  # Get invoice ID
    
    # Process items
    subtotal = 0.0
    total_tax = 0.0
    total_cgst = 0.0
    total_sgst = 0.0
    
    for item_data in data.items:
        # Get product
        product = db.query(Product).filter(
            Product.id == item_data.product_id,
            Product.tenant_id == tenant_id
        ).first()
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item_data.product_id} not found")
        
        # Check stock
        if product.current_stock < item_data.qty:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product.name}. Available: {product.current_stock}"
            )
        
        # Calculate prices
        unit_price = item_data.unit_price or product.selling_price
        item_subtotal = unit_price * item_data.qty
        item_discount = item_subtotal * (item_data.discount_percent / 100)
        item_taxable = item_subtotal - item_discount
        
        # GST calculation
        gst_rate = product.gst_rate if data.is_gst_invoice else 0
        item_tax = item_taxable * (gst_rate / 100)
        half_tax = item_tax / 2  # Split into CGST and SGST
        
        item_total = item_taxable + item_tax
        
        # Create invoice item
        inv_item = InvoiceItem(
            tenant_id=tenant_id,
            invoice_id=invoice.id,
            product_id=product.id,
            product_name=product.name,
            hsn_code=product.hsn_code,
            qty=item_data.qty,
            unit=product.unit,
            unit_price=unit_price,
            discount_percent=item_data.discount_percent,
            discount_amount=item_discount,
            gst_rate=gst_rate,
            cgst_amount=half_tax,
            sgst_amount=half_tax,
            igst_amount=0,  # For inter-state, would use IGST instead
            tax_amount=item_tax,
            subtotal=item_taxable,
            total=item_total
        )
        db.add(inv_item)
        
        # Deduct stock
        product.current_stock -= item_data.qty
        product.last_sold_date = datetime.utcnow()
        
        # Create inventory transaction
        inv_txn = InventoryTransaction(
            tenant_id=tenant_id,
            product_id=product.id,
            txn_type="SALE",
            qty=-item_data.qty,
            reference_type="INVOICE",
            reference_id=invoice.id
        )
        db.add(inv_txn)
        
        # Accumulate totals
        subtotal += item_taxable
        total_tax += item_tax
        total_cgst += half_tax
        total_sgst += half_tax
    
    # Apply invoice-level discount
    invoice_discount = data.discount_amount or (subtotal * data.discount_percent / 100)
    
    # Final totals
    invoice.subtotal = subtotal
    invoice.discount_amount = invoice_discount
    invoice.tax_amount = total_tax
    invoice.cgst_amount = total_cgst
    invoice.sgst_amount = total_sgst
    invoice.total_amount = subtotal - invoice_discount + total_tax
    invoice.balance_amount = invoice.total_amount
    
    # Check credit limit
    if customer and data.payment_mode == "CREDIT":
        available_credit = customer.credit_limit - customer.current_balance
        if invoice.total_amount > available_credit:
            raise HTTPException(
                status_code=400,
                detail=f"Exceeds credit limit. Available: ₹{available_credit:.2f}"
            )
    
    # Handle payment if provided
    if data.paid_amount and data.paid_amount > 0:
        payment = Payment(
            tenant_id=tenant_id,
            customer_id=data.customer_id,
            invoice_id=invoice.id,
            amount=min(data.paid_amount, invoice.total_amount),
            payment_mode=data.payment_mode or "CASH"
        )
        db.add(payment)
        
        invoice.paid_amount = payment.amount
        invoice.balance_amount = invoice.total_amount - payment.amount
        
        if invoice.balance_amount <= 0:
            invoice.payment_status = "PAID"
        elif invoice.paid_amount > 0:
            invoice.payment_status = "PARTIAL"
    
    # Update customer balance if credit sale
    if customer and invoice.balance_amount > 0:
        customer.current_balance += invoice.balance_amount
        customer.total_purchases += invoice.total_amount
        customer.last_purchase_date = datetime.utcnow()
    
    db.commit()
    db.refresh(invoice)
    
    # Build response
    invoice_response = InvoiceResponse(
        id=invoice.id,
        tenant_id=invoice.tenant_id,
        customer_id=invoice.customer_id,
        customer_name=customer.name if customer else None,
        invoice_no=invoice.invoice_no,
        invoice_date=invoice.invoice_date,
        due_date=invoice.due_date,
        invoice_type=invoice.invoice_type,
        is_gst_invoice=invoice.is_gst_invoice,
        subtotal=invoice.subtotal,
        discount_amount=invoice.discount_amount,
        tax_amount=invoice.tax_amount,
        total_amount=invoice.total_amount,
        paid_amount=invoice.paid_amount,
        balance_amount=invoice.balance_amount,
        payment_status=invoice.payment_status,
        items=[],  # Will be populated below
        notes=invoice.notes,
        created_at=invoice.created_at
    )
    
    return invoice_response


@router.get("/summary")
async def get_invoice_summary(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
) -> InvoiceSummary:
    """Get sales summary for dashboard."""
    if not from_date:
        from_date = date.today()
    if not to_date:
        to_date = date.today()
    
    # Total sales
    total_sales = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.tenant_id == tenant_id,
        Invoice.invoice_date >= from_date,
        Invoice.invoice_date <= to_date,
        Invoice.invoice_type == "SALE"
    ).scalar() or 0
    
    # Total invoices
    total_invoices = db.query(func.count(Invoice.id)).filter(
        Invoice.tenant_id == tenant_id,
        Invoice.invoice_date >= from_date,
        Invoice.invoice_date <= to_date
    ).scalar() or 0
    
    # Total tax
    total_tax = db.query(func.sum(Invoice.tax_amount)).filter(
        Invoice.tenant_id == tenant_id,
        Invoice.invoice_date >= from_date,
        Invoice.invoice_date <= to_date
    ).scalar() or 0
    
    # Cash collected
    cash_collected = db.query(func.sum(Invoice.paid_amount)).filter(
        Invoice.tenant_id == tenant_id,
        Invoice.invoice_date >= from_date,
        Invoice.invoice_date <= to_date
    ).scalar() or 0
    
    # Outstanding
    outstanding = db.query(func.sum(Invoice.balance_amount)).filter(
        Invoice.tenant_id == tenant_id,
        Invoice.balance_amount > 0
    ).scalar() or 0
    
    return InvoiceSummary(
        total_sales=total_sales,
        total_invoices=total_invoices,
        total_tax=total_tax,
        cash_collected=cash_collected,
        outstanding=outstanding
    )


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Get invoice details."""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.tenant_id == tenant_id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return invoice


@router.post("/payments", response_model=PaymentResponse)
async def record_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Record a payment against an invoice or customer."""
    
    invoice = None
    customer = None
    
    if data.invoice_id:
        invoice = db.query(Invoice).filter(
            Invoice.id == data.invoice_id,
            Invoice.tenant_id == tenant_id
        ).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        customer = invoice.customer
    elif data.customer_id:
        customer = db.query(Customer).filter(
            Customer.id == data.customer_id,
            Customer.tenant_id == tenant_id
        ).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
    
    # Create payment
    payment = Payment(
        tenant_id=tenant_id,
        customer_id=data.customer_id or (invoice.customer_id if invoice else None),
        invoice_id=data.invoice_id,
        amount=data.amount,
        payment_mode=data.payment_mode,
        reference_no=data.reference_no,
        notes=data.notes
    )
    db.add(payment)
    
    # Update invoice if provided
    if invoice:
        invoice.paid_amount += data.amount
        invoice.balance_amount = invoice.total_amount - invoice.paid_amount
        
        if invoice.balance_amount <= 0:
            invoice.payment_status = "PAID"
            invoice.balance_amount = 0
        else:
            invoice.payment_status = "PARTIAL"
    
    # Update customer balance
    if customer:
        customer.current_balance -= data.amount
        if customer.current_balance < 0:
            customer.current_balance = 0
    
    db.commit()
    db.refresh(payment)
    
    return payment
