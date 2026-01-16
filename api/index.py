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
app = FastAPI(title="BillOS API", version="1.0.3")

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
        "today_sales": 15000,
        "pending_amount": 5000,
        "low_stock_count": 3,
        "total_customers": 25
    }

@app.get("/api/dashboard/summary")
async def dashboard_summary():
    return {
        "today": {
            "sales": 15000,
            "cash_collected": 12500,
            "invoice_count": 8
        },
        "comparison": {
            "vs_yesterday_pct": 115
        },
        "alerts": {
            "total_outstanding": 25000,
            "overdue_customers": 3,
            "low_stock_items": 5
        }
    }

@app.get("/api/dashboard/top-products")
async def dashboard_top_products(limit: int = 5):
    # Return as array (not object with items key)
    products = [
        {"product_id": 1, "product_name": "Chicken Biryani (Full)", "qty_sold": 45, "revenue": 11250},
        {"product_id": 2, "product_name": "Mutton Biryani (Full)", "qty_sold": 32, "revenue": 11200},
        {"product_id": 3, "product_name": "Paneer Butter Masala", "qty_sold": 28, "revenue": 7000},
        {"product_id": 4, "product_name": "Coca Cola 500ml", "qty_sold": 120, "revenue": 6000},
        {"product_id": 5, "product_name": "Shawarma Plate", "qty_sold": 55, "revenue": 8250},
    ]
    return products[:limit]

@app.get("/api/dashboard/trends")
async def dashboard_trends(days: int = 7):
    # Generate mock trend data with 'day' field for short day name
    import datetime
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    trends = []
    for i in range(days):
        date = datetime.date.today() - datetime.timedelta(days=days-1-i)
        trends.append({
            "date": date.isoformat(),
            "day": day_names[date.weekday()],
            "sales": 10000 + (i * 500),
            "orders": 10 + i
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
    return {
        "items": [
            {"id": 1, "name": "Chicken Biryani (Full)", "sku": "FD-001", "price": 250, "stock": 50, "category": "Main Course"},
            {"id": 2, "name": "Mutton Biryani (Full)", "sku": "FD-002", "price": 350, "stock": 40, "category": "Main Course"},
            {"id": 3, "name": "Paneer Butter Masala", "sku": "FD-003", "price": 250, "stock": 35, "category": "Curry"},
            {"id": 4, "name": "Butter Naan", "sku": "FD-004", "price": 40, "stock": 100, "category": "Breads"},
            {"id": 5, "name": "Coca Cola 500ml", "sku": "BV-001", "price": 50, "stock": 200, "category": "Beverages"},
            {"id": 6, "name": "Shawarma Plate", "sku": "FD-005", "price": 150, "stock": 60, "category": "Snacks"},
            {"id": 7, "name": "Fresh Lime Soda", "sku": "BV-002", "price": 40, "stock": 150, "category": "Beverages"},
        ],
        "total": 7
    }

@app.get("/api/customers")
async def get_customers():
    return {
        "items": [
            {"id": 1, "name": "Walk-in Customer", "phone": "9999999999", "email": "", "balance": 0},
            {"id": 2, "name": "Swiggy Partner", "phone": "8888888888", "email": "partners@swiggy.in", "balance": 0},
            {"id": 3, "name": "Zomato Partner", "phone": "7777777777", "email": "partners@zomato.com", "balance": 1500},
        ],
        "total": 3
    }

@app.get("/api/invoices")
async def get_invoices():
    # Make sure items is NOT empty initially to avoid empty state confusion
    return {
        "items": [
            {"id": 1, "invoice_no": "INV-1001", "customer": "Walk-in Customer", "total": 650, "status": "PAID", "date": "2026-01-16"},
            {"id": 2, "invoice_no": "INV-1002", "customer": "Swiggy Order", "total": 1200, "status": "PAID", "date": "2026-01-16"},
            {"id": 3, "invoice_no": "INV-1003", "customer": "Zomato Order", "total": 850, "status": "PENDING", "date": "2026-01-16"},
        ],
        "total": 3
    }

