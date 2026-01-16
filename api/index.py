"""
Vercel Serverless Function Entry Point for BillOS API.
Self-contained API for Vercel deployment.
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import hashlib

# Simple in-memory database for demo
DEMO_USERS = {
    "9876543210": {"name": "Demo Owner", "password_hash": hashlib.sha256("demo123".encode()).hexdigest(), "role": "OWNER"},
    "9876543211": {"name": "Demo Manager", "password_hash": hashlib.sha256("demo123".encode()).hexdigest(), "role": "MANAGER"},
    "97455556666": {"name": "Test User", "password_hash": hashlib.sha256("pass".encode()).hexdigest(), "role": "OWNER"},
    "1234567890": {"name": "Quick Login", "password_hash": hashlib.sha256("1234".encode()).hexdigest(), "role": "OWNER"},
}

# FastAPI app
app = FastAPI(title="BillOS API", version="1.0.4")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas
class UserLogin(BaseModel):
    phone: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int = 1
    tenant_id: int = 1
    user_name: str
    role: str

# Routes
@app.get("/api/")
async def root():
    return {"app": "BillOS", "version": "1.0.0", "status": "running"}

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "database": "demo-mode",
        "version": "1.0.1",
        "updated": "2026-01-16T14:50:00"
    }

@app.post("/api/auth/login", response_model=Token)
async def login(data: UserLogin):
    user = DEMO_USERS.get(data.phone)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid phone or password")
    
    password_hash = hashlib.sha256(data.password.encode()).hexdigest()
    if user["password_hash"] != password_hash:
        raise HTTPException(status_code=401, detail="Invalid phone or password")
    
    # Simple token (demo only - not secure for production)
    import time
    token = hashlib.sha256(f"{data.phone}{time.time()}".encode()).hexdigest()
    
    return Token(
        access_token=token,
        user_name=user["name"],
        role=user["role"]
    )

@app.get("/api/dashboard/stats")
async def dashboard_stats():
    return {
        "today_sales": 42500,
        "pending_amount": 5600,
        "low_stock_count": 3,
        "total_customers": 6
    }

@app.get("/api/dashboard/summary")
async def dashboard_summary():
    return {
        "today": {
            "sales": 42500,
            "cash_collected": 38000,
            "invoice_count": 24
        },
        "comparison": {
            "vs_yesterday_pct": 125
        },
        "alerts": {
            "total_outstanding": 5600,
            "overdue_customers": 1,
            "low_stock_items": 3
        }
    }

@app.get("/api/dashboard/top-products")
async def dashboard_top_products(limit: int = 5):
    # Return as array (not object with items key)
    products = [
        {"product_id": 1, "product_name": "Chicken Biryani (Full)", "qty_sold": 145, "revenue": 36250},
        {"product_id": 5, "product_name": "Coca Cola 500ml", "qty_sold": 120, "revenue": 6000},
        {"product_id": 12, "product_name": "Butter Naan", "qty_sold": 95, "revenue": 3800},
        {"product_id": 3, "product_name": "Paneer Butter Masala", "qty_sold": 80, "revenue": 20000},
        {"product_id": 7, "product_name": "Chicken 65", "qty_sold": 75, "revenue": 13500},
        {"product_id": 18, "product_name": "Lime Soda", "qty_sold": 60, "revenue": 2400},
    ]
    return products[:limit]

@app.get("/api/dashboard/trends")
async def dashboard_trends(days: int = 7):
    # Generate mock trend data with 'day' field for short day name
    import datetime
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    trends = []
    base_sales = [12000, 11500, 13000, 14500, 18000, 22000, 19500] 
    for i in range(days):
        date = datetime.date.today() - datetime.timedelta(days=days-1-i)
        day_idx = date.weekday() # 0=Mon
        trends.append({
            "date": date.isoformat(),
            "day": day_names[day_idx],
            "sales": base_sales[day_idx],
            "orders": int(base_sales[day_idx] / 350) # Avg order value 350
        })
    return {"trends": trends}

@app.get("/api/auth/me")
async def get_current_user():
    # Demo user - in production this would validate the token
    return {
        "id": 1,
        "name": "Demo Owner",
        "phone": "9876543210",
        "role": "OWNER",
        "tenant_id": 1
    }

@app.get("/api/products")
async def get_products():
    items = [
        # Starters
        {"id": 7, "name": "Chicken 65", "sku": "ST-001", "price": 180, "stock": 40, "category": "Starters", "cost_price": 80},
        {"id": 8, "name": "Gobi Manchurian", "sku": "ST-002", "price": 140, "stock": 35, "category": "Starters", "cost_price": 50},
        {"id": 9, "name": "Paneer Tikka", "sku": "ST-003", "price": 190, "stock": 25, "category": "Starters", "cost_price": 90},
        
        # Main Course - Biryani/Rice
        {"id": 1, "name": "Chicken Biryani (Full)", "sku": "MC-001", "price": 250, "stock": 50, "category": "Main Course", "cost_price": 120},
        {"id": 2, "name": "Mutton Biryani (Full)", "sku": "MC-002", "price": 350, "stock": 40, "category": "Main Course", "cost_price": 180},
        {"id": 10, "name": "Veg Biryani", "sku": "MC-003", "price": 180, "stock": 30, "category": "Main Course", "cost_price": 70},
        {"id": 11, "name": "Chicken Fried Rice", "sku": "MC-004", "price": 200, "stock": 45, "category": "Main Course", "cost_price": 80},

        # Curries
        {"id": 3, "name": "Paneer Butter Masala", "sku": "CU-001", "price": 250, "stock": 35, "category": "Curry", "cost_price": 100},
        {"id": 14, "name": "Butter Chicken", "sku": "CU-002", "price": 280, "stock": 40, "category": "Curry", "cost_price": 120},
        {"id": 15, "name": "Dal Fry", "sku": "CU-003", "price": 160, "stock": 50, "category": "Curry", "cost_price": 50},

        # Breads
        {"id": 4, "name": "Butter Naan", "sku": "BR-001", "price": 40, "stock": 100, "category": "Breads", "cost_price": 10},
        {"id": 12, "name": "Tandoori Roti", "sku": "BR-002", "price": 30, "stock": 100, "category": "Breads", "cost_price": 8},
        {"id": 13, "name": "Kerala Parotta", "sku": "BR-003", "price": 25, "stock": 100, "category": "Breads", "cost_price": 5},

        # Beverages
        {"id": 5, "name": "Coca Cola 500ml", "sku": "BV-001", "price": 50, "stock": 200, "category": "Beverages", "cost_price": 35},
        {"id": 18, "name": "Fresh Lime Soda", "sku": "BV-002", "price": 60, "stock": 150, "category": "Beverages", "cost_price": 15},
        {"id": 19, "name": "Mango Lassi", "sku": "BV-003", "price": 80, "stock": 40, "category": "Beverages", "cost_price": 30},
        {"id": 20, "name": "Cold Coffee", "sku": "BV-004", "price": 100, "stock": 40, "category": "Beverages", "cost_price": 35},
        {"id": 21, "name": "Masala Tea", "sku": "BV-005", "price": 30, "stock": 500, "category": "Beverages", "cost_price": 5},

        # Desserts
        {"id": 22, "name": "Gulab Jamun (2pcs)", "sku": "DS-001", "price": 80, "stock": 50, "category": "Desserts", "cost_price": 25},
        {"id": 23, "name": "Vanilla Ice Cream", "sku": "DS-002", "price": 60, "stock": 50, "category": "Desserts", "cost_price": 20},
        
        # Shawarma
        {"id": 6, "name": "Chicken Shawarma Plate", "sku": "SN-001", "price": 150, "stock": 60, "category": "Quick Bites", "cost_price": 70},
    ]
    return {
        "items": items,
        "total": len(items)
    }

@app.get("/api/customers")
async def get_customers():
    items = [
        {"id": 1, "name": "Walk-in Customer", "phone": "", "email": "", "balance": 0, "credit_limit": 0, "total_purchases": 50000, "risk_tag": "NORMAL"},
        {"id": 2, "name": "Swiggy Partner", "phone": "8888888888", "email": "partners@swiggy.in", "balance": 0, "credit_limit": 100000, "total_purchases": 125000, "risk_tag": "NORMAL"},
        {"id": 3, "name": "Zomato Partner", "phone": "7777777777", "email": "partners@zomato.com", "balance": 4500, "credit_limit": 100000, "total_purchases": 98000, "risk_tag": "NORMAL"},
        {"id": 4, "name": "TechPark Office", "phone": "9988776655", "email": "admin@techpark.com", "balance": 12500, "credit_limit": 50000, "total_purchases": 45000, "risk_tag": "NORMAL"},
        {"id": 5, "name": "Rahul Sharma", "phone": "9876543212", "email": "rahul@gmail.com", "balance": 0, "credit_limit": 5000, "total_purchases": 8500, "risk_tag": "NORMAL"},
        {"id": 6, "name": "Priya Patel", "phone": "9876543213", "email": "priya@yahoo.com", "balance": 500, "credit_limit": 2000, "total_purchases": 3200, "risk_tag": "HIGH_RISK"},
    ]
    return {
        "items": items,
        "total": len(items)
    }

@app.get("/api/invoices")
async def get_invoices():
    # Make sure items is NOT empty initially to avoid empty state confusion
    items = [
        {"id": 10, "invoice_no": "INV-1010", "customer": "Walk-in Customer", "total": 450, "status": "PAID", "date": "2026-01-16", "paid_amount": 450, "balance_amount": 0},
        {"id": 9, "invoice_no": "INV-1009", "customer": "Walk-in Customer", "total": 120, "status": "PAID", "date": "2026-01-16", "paid_amount": 120, "balance_amount": 0},
        {"id": 8, "invoice_no": "INV-1008", "customer": "Swiggy Partner", "total": 1250, "status": "PAID", "date": "2026-01-16", "paid_amount": 1250, "balance_amount": 0},
        {"id": 7, "invoice_no": "INV-1007", "customer": "TechPark Office", "total": 3500, "status": "PENDING", "date": "2026-01-15", "paid_amount": 0, "balance_amount": 3500},
        {"id": 6, "invoice_no": "INV-1006", "customer": "Rahul Sharma", "total": 850, "status": "PAID", "date": "2026-01-15", "paid_amount": 850, "balance_amount": 0},
        {"id": 5, "invoice_no": "INV-1005", "customer": "Zomato Partner", "total": 2100, "status": "PENDING", "date": "2026-01-15", "paid_amount": 0, "balance_amount": 2100},
        {"id": 4, "invoice_no": "INV-1004", "customer": "Walk-in Customer", "total": 250, "status": "PAID", "date": "2026-01-14", "paid_amount": 250, "balance_amount": 0},
        {"id": 3, "invoice_no": "INV-1003", "customer": "TechPark Office", "total": 4200, "status": "PAID", "date": "2026-01-14", "paid_amount": 4200, "balance_amount": 0},
        {"id": 2, "invoice_no": "INV-1002", "customer": "Priya Patel", "total": 500, "status": "PARTIAL", "date": "2026-01-14", "paid_amount": 200, "balance_amount": 300},
        {"id": 1, "invoice_no": "INV-1001", "customer": "Walk-in Customer", "total": 1800, "status": "PAID", "date": "2026-01-13", "paid_amount": 1800, "balance_amount": 0},
    ]
    return {
        "items": items,
        "total": len(items)
    }


@app.get("/api/invoices/summary")
async def get_invoices_summary():
    return {
        "total_sales": 14920,
        "total_invoices": 10,
        "cash_collected": 9320,
        "outstanding": 5600,
        "total_tax": 745
    }

@app.get("/api/invoices/{invoice_id}")
async def get_invoice_detail(invoice_id: int):
    # Generic mock items for detail view
    mock_items = [
        {"product_name": "Chicken Biryani (Full)", "qty": 2, "unit_price": 250, "total": 500},
        {"product_name": "Coca Cola 500ml", "qty": 2, "unit_price": 50, "total": 100}
    ]
    
    return {
        "id": invoice_id,
        "invoice_no": f"INV-10{invoice_id:02d}",
        "invoice_date": "2026-01-16",
        "customer_name": "Walk-in Customer", 
        "total_amount": 600,
        "subtotal": 600,
        "tax_amount": 0,
        "paid_amount": 600,
        "balance_amount": 0,
        "payment_status": "PAID",
        "payment_mode": "CASH",
        "items": mock_items
    }
