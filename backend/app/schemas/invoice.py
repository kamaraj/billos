"""Invoice schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


class InvoiceItemCreate(BaseModel):
    """Invoice item creation schema."""
    product_id: str
    qty: float
    unit_price: Optional[float] = None  # If None, use product's selling price
    discount_percent: float = 0.0


class InvoiceCreate(BaseModel):
    """Invoice creation schema."""
    customer_id: Optional[str] = None  # Walk-in if None
    invoice_type: str = "SALE"
    is_gst_invoice: bool = False
    items: List[InvoiceItemCreate]
    discount_percent: float = 0.0
    discount_amount: float = 0.0
    notes: Optional[str] = None
    payment_mode: Optional[str] = None  # If provided, auto-create payment
    paid_amount: Optional[float] = None


class InvoiceItemResponse(BaseModel):
    """Invoice item response."""
    id: str
    product_id: str
    product_name: str
    hsn_code: Optional[str]
    qty: float
    unit: str
    unit_price: float
    discount_percent: float
    discount_amount: float
    gst_rate: float
    tax_amount: float
    subtotal: float
    total: float
    
    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    """Invoice response schema."""
    id: str
    tenant_id: str
    customer_id: Optional[str]
    customer_name: Optional[str] = None
    invoice_no: str
    invoice_date: date
    due_date: Optional[date]
    invoice_type: str
    is_gst_invoice: bool
    subtotal: float
    discount_amount: float
    tax_amount: float
    total_amount: float
    paid_amount: float
    balance_amount: float
    payment_status: str
    items: List[InvoiceItemResponse]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class InvoiceSummary(BaseModel):
    """Daily/period invoice summary."""
    total_sales: float
    total_invoices: int
    total_tax: float
    cash_collected: float
    outstanding: float


class PaymentCreate(BaseModel):
    """Payment creation schema."""
    invoice_id: Optional[str] = None
    customer_id: Optional[str] = None
    amount: float
    payment_mode: str = "CASH"
    reference_no: Optional[str] = None
    notes: Optional[str] = None


class PaymentResponse(BaseModel):
    """Payment response schema."""
    id: str
    invoice_id: Optional[str]
    customer_id: Optional[str]
    amount: float
    payment_mode: str
    payment_date: date
    reference_no: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
