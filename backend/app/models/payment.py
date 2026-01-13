"""Payment models for cash and credit tracking."""
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
import uuid

from app.core.database import Base


class Payment(Base):
    """Payment records for invoices."""
    
    __tablename__ = "payments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=True)
    invoice_id = Column(String(36), ForeignKey("invoices.id"), nullable=True)
    
    # Payment details
    payment_date = Column(Date, default=date.today)
    amount = Column(Float, nullable=False)
    payment_mode = Column(String(20), default="CASH")  # CASH, UPI, CARD, CHEQUE, CREDIT
    
    # Reference
    reference_no = Column(String(100), nullable=True)  # UPI txn id, cheque no, etc.
    notes = Column(Text, nullable=True)
    
    # For credit payments tracking
    is_credit_payment = Column(String(1), default="N")  # Y = payment against credit/udhar
    days_overdue = Column(Float, default=0)  # Calculated at payment time
    
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(36), nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="payments")
    invoice = relationship("Invoice", back_populates="payments")
