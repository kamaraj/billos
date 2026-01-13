"""Dashboard API endpoints - Daily summary and cash position."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date, timedelta

from app.core.database import get_db
from app.core.auth import get_current_tenant_id
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.models.product import Product
from app.models.customer import Customer

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary")
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Get daily dashboard summary - the most important screen.
    Shows: Today's sales, cash collected, outstanding, low stock count.
    """
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # Today's sales
    today_sales = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.tenant_id == tenant_id,
        Invoice.invoice_date == today,
        Invoice.invoice_type == "SALE"
    ).scalar() or 0
    
    # Today's invoice count
    today_invoice_count = db.query(func.count(Invoice.id)).filter(
        Invoice.tenant_id == tenant_id,
        Invoice.invoice_date == today
    ).scalar() or 0
    
    # Today's cash collected (from payments table for accuracy)
    today_cash = db.query(func.sum(Payment.amount)).filter(
        Payment.tenant_id == tenant_id,
        Payment.payment_date == today
    ).scalar() or 0
    
    # Total outstanding
    total_outstanding = db.query(func.sum(Customer.current_balance)).filter(
        Customer.tenant_id == tenant_id,
        Customer.current_balance > 0
    ).scalar() or 0
    
    # Low stock count
    low_stock_count = db.query(func.count(Product.id)).filter(
        Product.tenant_id == tenant_id,
        Product.is_active == True,
        Product.current_stock <= Product.reorder_level
    ).scalar() or 0
    
    # Yesterday comparison
    yesterday_sales = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.tenant_id == tenant_id,
        Invoice.invoice_date == yesterday,
        Invoice.invoice_type == "SALE"
    ).scalar() or 0
    
    # 7-day average
    week_ago = today - timedelta(days=7)
    week_total = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.tenant_id == tenant_id,
        Invoice.invoice_date >= week_ago,
        Invoice.invoice_date < today,
        Invoice.invoice_type == "SALE"
    ).scalar() or 0
    avg_7day = week_total / 7 if week_total else 0
    
    # Customers with overdue > 14 days
    overdue_customers = db.query(func.count(Customer.id)).filter(
        Customer.tenant_id == tenant_id,
        Customer.current_balance > 0,
        Customer.risk_tag != "NORMAL"
    ).scalar() or 0
    
    return {
        "date": today.isoformat(),
        "today": {
            "sales": round(today_sales, 2),
            "invoice_count": today_invoice_count,
            "cash_collected": round(today_cash, 2)
        },
        "comparison": {
            "yesterday_sales": round(yesterday_sales, 2),
            "avg_7day_sales": round(avg_7day, 2),
            "vs_yesterday_pct": round((today_sales / yesterday_sales * 100) if yesterday_sales > 0 else 0, 1),
            "vs_avg_pct": round((today_sales / avg_7day * 100) if avg_7day > 0 else 0, 1)
        },
        "alerts": {
            "total_outstanding": round(total_outstanding, 2),
            "low_stock_items": low_stock_count,
            "overdue_customers": overdue_customers
        }
    }


@router.get("/cash-summary")
async def get_cash_summary(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Get cash flow summary by payment mode."""
    today = date.today()
    
    # Today's payments by mode
    payment_modes = ["CASH", "UPI", "CARD", "CHEQUE", "CREDIT"]
    by_mode = {}
    
    for mode in payment_modes:
        amount = db.query(func.sum(Payment.amount)).filter(
            Payment.tenant_id == tenant_id,
            Payment.payment_date == today,
            Payment.payment_mode == mode
        ).scalar() or 0
        by_mode[mode.lower()] = round(amount, 2)
    
    total_collected = sum(by_mode.values())
    
    return {
        "date": today.isoformat(),
        "total_collected": round(total_collected, 2),
        "by_payment_mode": by_mode
    }


@router.get("/trends")
async def get_sales_trends(
    days: int = 7,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Get sales trends for charts."""
    today = date.today()
    
    trends = []
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        
        sales = db.query(func.sum(Invoice.total_amount)).filter(
            Invoice.tenant_id == tenant_id,
            Invoice.invoice_date == d,
            Invoice.invoice_type == "SALE"
        ).scalar() or 0
        
        invoices = db.query(func.count(Invoice.id)).filter(
            Invoice.tenant_id == tenant_id,
            Invoice.invoice_date == d
        ).scalar() or 0
        
        trends.append({
            "date": d.isoformat(),
            "day": d.strftime("%a"),
            "sales": round(sales, 2),
            "invoices": invoices
        })
    
    return {"trends": trends}


@router.get("/top-products")
async def get_top_products(
    days: int = 30,
    limit: int = 10,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Get top selling products."""
    from app.models.invoice import InvoiceItem
    
    start_date = date.today() - timedelta(days=days)
    
    # Query top products by quantity sold
    results = db.query(
        InvoiceItem.product_id,
        InvoiceItem.product_name,
        func.sum(InvoiceItem.qty).label("qty_sold"),
        func.sum(InvoiceItem.total).label("revenue")
    ).join(Invoice).filter(
        InvoiceItem.tenant_id == tenant_id,
        Invoice.invoice_date >= start_date
    ).group_by(
        InvoiceItem.product_id,
        InvoiceItem.product_name
    ).order_by(
        func.sum(InvoiceItem.total).desc()
    ).limit(limit).all()
    
    return [{
        "product_id": r.product_id,
        "product_name": r.product_name,
        "qty_sold": round(r.qty_sold, 2),
        "revenue": round(r.revenue, 2)
    } for r in results]


@router.get("/top-customers")
async def get_top_customers(
    days: int = 30,
    limit: int = 10,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Get top customers by purchase value."""
    start_date = date.today() - timedelta(days=days)
    
    results = db.query(
        Invoice.customer_id,
        Customer.name,
        func.sum(Invoice.total_amount).label("total_purchases"),
        func.count(Invoice.id).label("invoice_count")
    ).join(Customer).filter(
        Invoice.tenant_id == tenant_id,
        Invoice.invoice_date >= start_date,
        Invoice.customer_id.isnot(None)
    ).group_by(
        Invoice.customer_id,
        Customer.name
    ).order_by(
        func.sum(Invoice.total_amount).desc()
    ).limit(limit).all()
    
    return [{
        "customer_id": r.customer_id,
        "customer_name": r.name,
        "total_purchases": round(r.total_purchases, 2),
        "invoice_count": r.invoice_count
    } for r in results]
