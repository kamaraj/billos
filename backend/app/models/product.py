"""Product and Inventory models."""
from sqlalchemy import Column, String, DateTime, Float, Boolean, ForeignKey, Integer, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Product(Base):
    """Product catalog model."""
    
    __tablename__ = "products"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    
    # Basic info
    name = Column(String(255), nullable=False)
    sku = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    
    # Pricing
    cost_price = Column(Float, default=0.0)
    selling_price = Column(Float, nullable=False)
    wholesale_price = Column(Float, nullable=True)
    
    # GST
    hsn_code = Column(String(10), nullable=True)
    gst_rate = Column(Float, default=18.0)
    
    # Stock
    current_stock = Column(Float, default=0.0)
    reorder_level = Column(Float, default=10.0)
    min_order_qty = Column(Integer, default=1)
    unit = Column(String(20), default="PCS")  # PCS, KG, LTR, etc.
    
    # Inventory intelligence (for agents)
    lead_time_days = Column(Integer, default=3)
    safety_stock_days = Column(Integer, default=3)
    last_sold_date = Column(DateTime, nullable=True)
    
    # Expiry tracking (for medical/food)
    has_expiry = Column(Boolean, default=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="products")
    invoice_items = relationship("InvoiceItem", back_populates="product")
    stock_transactions = relationship("InventoryTransaction", back_populates="product")
    batches = relationship("ProductBatch", back_populates="product")


class ProductBatch(Base):
    """Batch tracking with expiry dates (for medical/food)."""
    
    __tablename__ = "product_batches"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    
    batch_no = Column(String(50), nullable=False)
    qty = Column(Float, default=0.0)
    cost_price = Column(Float, default=0.0)
    expiry_date = Column(Date, nullable=True)
    manufacturing_date = Column(Date, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="batches")


class InventoryTransaction(Base):
    """Stock movement tracking."""
    
    __tablename__ = "inventory_transactions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    
    txn_type = Column(String(20), nullable=False)  # IN, OUT, ADJUSTMENT, SALE, RETURN
    qty = Column(Float, nullable=False)
    cost_price = Column(Float, nullable=True)
    reference_type = Column(String(50), nullable=True)  # INVOICE, PURCHASE, MANUAL
    reference_id = Column(String(36), nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(36), nullable=True)
    
    # Relationships
    product = relationship("Product", back_populates="stock_transactions")
