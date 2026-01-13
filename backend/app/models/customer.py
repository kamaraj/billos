"""Customer model for CRM and credit tracking."""
from sqlalchemy import Column, String, DateTime, Float, Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Customer(Base):
    """Customer model with credit/udhar tracking."""
    
    __tablename__ = "customers"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(15))
    email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    gst_no = Column(String(15), nullable=True)
    
    # Credit/Udhar management
    credit_limit = Column(Float, default=0.0)
    current_balance = Column(Float, default=0.0)  # Positive = customer owes us
    is_credit_blocked = Column(Boolean, default=False)
    
    # Risk tagging
    risk_tag = Column(String(20), default="NORMAL")  # NORMAL, HIGH_RISK, BLOCKED
    late_payment_count = Column(Integer, default=0)
    
    # Loyalty
    total_purchases = Column(Float, default=0.0)
    loyalty_points = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True)
    last_purchase_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="customers")
    invoices = relationship("Invoice", back_populates="customer")
    payments = relationship("Payment", back_populates="customer")
