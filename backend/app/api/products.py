"""Products API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_tenant_id
from app.models.product import Product, InventoryTransaction
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse,
    StockAdjustment, LowStockAlert
)

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("/", response_model=List[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None,
    low_stock_only: bool = False,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """List all products for the tenant."""
    query = db.query(Product).filter(
        Product.tenant_id == tenant_id,
        Product.is_active == True
    )
    
    if search:
        query = query.filter(
            (Product.name.ilike(f"%{search}%")) |
            (Product.sku.ilike(f"%{search}%"))
        )
    
    if category:
        query = query.filter(Product.category == category)
    
    if low_stock_only:
        query = query.filter(Product.current_stock <= Product.reorder_level)
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.post("/", response_model=ProductResponse)
async def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Create a new product."""
    product = Product(
        tenant_id=tenant_id,
        name=data.name,
        sku=data.sku,
        description=data.description,
        category=data.category,
        cost_price=data.cost_price,
        selling_price=data.selling_price,
        wholesale_price=data.wholesale_price,
        hsn_code=data.hsn_code,
        gst_rate=data.gst_rate,
        current_stock=data.initial_stock,
        reorder_level=data.reorder_level,
        min_order_qty=data.min_order_qty,
        unit=data.unit,
        lead_time_days=data.lead_time_days,
        safety_stock_days=data.safety_stock_days,
        has_expiry=data.has_expiry
    )
    db.add(product)
    
    # Create initial stock transaction if stock > 0
    if data.initial_stock > 0:
        txn = InventoryTransaction(
            tenant_id=tenant_id,
            product_id=product.id,
            txn_type="IN",
            qty=data.initial_stock,
            cost_price=data.cost_price,
            reference_type="INITIAL",
            notes="Initial stock"
        )
        db.add(txn)
    
    db.commit()
    db.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Get a specific product."""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.tenant_id == tenant_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Update a product."""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.tenant_id == tenant_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Soft delete a product."""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.tenant_id == tenant_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.is_active = False
    product.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Product deleted successfully"}


@router.post("/stock-adjustment")
async def adjust_stock(
    data: StockAdjustment,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Adjust stock (add or remove)."""
    product = db.query(Product).filter(
        Product.id == data.product_id,
        Product.tenant_id == tenant_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update stock
    if data.txn_type == "IN":
        product.current_stock += data.qty
    elif data.txn_type == "OUT":
        if product.current_stock < data.qty:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        product.current_stock -= data.qty
    else:  # ADJUSTMENT
        product.current_stock = data.qty
    
    # Create transaction record
    txn = InventoryTransaction(
        tenant_id=tenant_id,
        product_id=data.product_id,
        txn_type=data.txn_type,
        qty=data.qty,
        cost_price=data.cost_price,
        reference_type="MANUAL",
        notes=data.notes
    )
    db.add(txn)
    db.commit()
    
    return {
        "message": "Stock adjusted successfully",
        "new_stock": product.current_stock
    }


@router.get("/alerts/low-stock", response_model=List[LowStockAlert])
async def get_low_stock_alerts(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Get products with low stock."""
    products = db.query(Product).filter(
        Product.tenant_id == tenant_id,
        Product.is_active == True,
        Product.current_stock <= Product.reorder_level
    ).all()
    
    alerts = []
    for p in products:
        alerts.append(LowStockAlert(
            product_id=p.id,
            product_name=p.name,
            current_stock=p.current_stock,
            reorder_level=p.reorder_level,
            deficit=p.reorder_level - p.current_stock
        ))
    
    return alerts
