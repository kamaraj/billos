"""Product and Inventory schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


class ProductBase(BaseModel):
    """Base product schema."""
    name: str
    sku: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    cost_price: float = 0.0
    selling_price: float
    wholesale_price: Optional[float] = None
    hsn_code: Optional[str] = None
    gst_rate: float = 18.0
    reorder_level: float = 10.0
    min_order_qty: int = 1
    unit: str = "PCS"
    lead_time_days: int = 3
    safety_stock_days: int = 3
    has_expiry: bool = False


class ProductCreate(ProductBase):
    """Create product schema."""
    initial_stock: float = 0.0


class ProductUpdate(BaseModel):
    """Update product schema."""
    name: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    wholesale_price: Optional[float] = None
    hsn_code: Optional[str] = None
    gst_rate: Optional[float] = None
    reorder_level: Optional[float] = None
    min_order_qty: Optional[int] = None
    unit: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Product response schema."""
    id: str
    tenant_id: str
    current_stock: float
    last_sold_date: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class StockAdjustment(BaseModel):
    """Stock adjustment request."""
    product_id: str
    qty: float
    txn_type: str = "IN"  # IN, OUT, ADJUSTMENT
    cost_price: Optional[float] = None
    notes: Optional[str] = None


class LowStockAlert(BaseModel):
    """Low stock alert response."""
    product_id: str
    product_name: str
    current_stock: float
    reorder_level: float
    deficit: float
