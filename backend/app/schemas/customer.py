"""Customer schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CustomerBase(BaseModel):
    """Base customer schema."""
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    gst_no: Optional[str] = None
    credit_limit: float = 0.0


class CustomerCreate(CustomerBase):
    """Create customer schema."""
    pass


class CustomerUpdate(BaseModel):
    """Update customer schema."""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    gst_no: Optional[str] = None
    credit_limit: Optional[float] = None
    is_credit_blocked: Optional[bool] = None
    risk_tag: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerResponse(CustomerBase):
    """Customer response schema."""
    id: str
    tenant_id: str
    current_balance: float
    is_credit_blocked: bool
    risk_tag: str
    late_payment_count: int
    total_purchases: float
    loyalty_points: int
    last_purchase_date: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class CustomerLedgerEntry(BaseModel):
    """Customer ledger entry."""
    date: datetime
    type: str  # INVOICE, PAYMENT
    reference: str
    debit: float
    credit: float
    balance: float


class OutstandingCustomer(BaseModel):
    """Outstanding customer for collection."""
    customer_id: str
    customer_name: str
    phone: Optional[str]
    due_amount: float
    days_overdue: int
    risk_tag: str
