"""Tenant model for multi-tenancy support."""
from sqlalchemy import Column, String, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Tenant(Base):
    """Multi-tenant organization model."""
    
    __tablename__ = "tenants"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    business_type = Column(String(100))  # kirana, medical, wholesale, etc.
    gst_no = Column(String(15), nullable=True)
    address = Column(String(500))
    phone = Column(String(15))
    email = Column(String(255))
    plan = Column(Enum("FREE", "STARTER", "PRO", "BUSINESS", name="plan_type"), default="FREE")
    is_gst_enabled = Column(Boolean, default=False)
    currency = Column(String(3), default="INR")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="tenant")
    customers = relationship("Customer", back_populates="tenant")
    products = relationship("Product", back_populates="tenant")
    invoices = relationship("Invoice", back_populates="tenant")
