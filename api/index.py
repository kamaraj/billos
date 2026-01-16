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
}

# FastAPI app
app = FastAPI(title="BillOS API", version="1.0.0")

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
    return {"status": "healthy", "database": "demo-mode", "version": "1.0.0"}

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

@app.get("/api/products")
async def get_products():
    return {
        "items": [
            {"id": 1, "name": "Demo Product 1", "price": 100, "stock": 50},
            {"id": 2, "name": "Demo Product 2", "price": 200, "stock": 30},
        ],
        "total": 2
    }

@app.get("/api/customers")
async def get_customers():
    return {
        "items": [
            {"id": 1, "name": "Demo Customer", "phone": "9999999999", "balance": 0},
        ],
        "total": 1
    }

@app.get("/api/invoices")
async def get_invoices():
    return {"items": [], "total": 0}
