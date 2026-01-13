"""Invoice models for billing."""
from sqlalchemy import Column, String, DateTime, Float, Boolean, ForeignKey, Integer, Text, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
import uuid

from app.core.database import Base


class Invoice(Base):
    """Invoice/Bill model."""
    
    __tablename__ = "invoices"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=True)  # Walk-in = null
    
    # Invoice details
    invoice_no = Column(String(50), nullable=False)
    invoice_date = Column(Date, default=date.today)
    due_date = Column(Date, nullable=True)
    
    invoice_type = Column(String(20), default="SALE")  # SALE, RETURN, QUOTATION, PROFORMA
    is_gst_invoice = Column(Boolean, default=False)
    
    # Amounts
    subtotal = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    discount_percent = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)  # Total GST
    cgst_amount = Column(Float, default=0.0)
    sgst_amount = Column(Float, default=0.0)
    igst_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    
    # Payment status
    paid_amount = Column(Float, default=0.0)
    balance_amount = Column(Float, default=0.0)
    payment_status = Column(String(20), default="UNPAID")  # UNPAID, PARTIAL, PAID
    
    # Additional info
    notes = Column(Text, nullable=True)
    terms = Column(Text, nullable=True)
    
    # Sync status (for offline-first)
    is_synced = Column(Boolean, default=True)
    local_id = Column(String(36), nullable=True)  # Local device ID for offline sync
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(36), nullable=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="invoices")
    customer = relationship("Customer", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice")


class InvoiceItem(Base):
    """Invoice line items."""
    
    __tablename__ = "invoice_items"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    invoice_id = Column(String(36), ForeignKey("invoices.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    
    # Item details
    product_name = Column(String(255), nullable=False)  # Snapshot at invoice time
    hsn_code = Column(String(10), nullable=True)
    qty = Column(Float, nullable=False)
    unit = Column(String(20), default="PCS")
    
    # Pricing
    unit_price = Column(Float, nullable=False)
    discount_percent = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    
    # GST
    gst_rate = Column(Float, default=0.0)
    cgst_amount = Column(Float, default=0.0)
    sgst_amount = Column(Float, default=0.0)
    igst_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    
    # Totals
    subtotal = Column(Float, default=0.0)  # qty * unit_price - discount
    total = Column(Float, default=0.0)  # subtotal + tax
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product", back_populates="invoice_items")
