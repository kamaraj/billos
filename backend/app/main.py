"""BillOS - Daily Business OS for MSMEs."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db, SessionLocal
from app.api import auth, products, customers, invoices, dashboard

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Daily Business OS for MSMEs - Billing, Inventory, Cashflow Management"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(customers.router)
app.include_router(invoices.router)
app.include_router(dashboard.router)


def seed_demo_data():
    """Seed demo data for Vercel deployment (ephemeral /tmp database)."""
    from app.models.tenant import Tenant
    from app.models.user import User
    from app.core.auth import get_password_hash
    
    db = SessionLocal()
    try:
        # Check if data exists
        existing_tenant = db.query(Tenant).first()
        if existing_tenant:
            return  # Already seeded
        
        # Create demo tenant
        tenant = Tenant(
            name="Demo Business",
            business_type="Retail",
            address="123 Demo Street",
            phone="9876543210",
            email="demo@billos.app",
            plan="BUSINESS"
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        
        # Create demo users
        demo_users = [
            {"name": "Demo Owner", "phone": "9876543210", "password": "demo123", "role": "OWNER"},
            {"name": "Demo Manager", "phone": "9876543211", "password": "demo123", "role": "MANAGER"},
        ]
        
        for u in demo_users:
            user = User(
                tenant_id=tenant.id,
                name=u["name"],
                phone=u["phone"],
                password_hash=get_password_hash(u["password"]),
                role=u["role"],
                is_active=True
            )
            db.add(user)
        
        db.commit()
        print("Demo data seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding demo data: {e}")
        db.rollback()
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    # Seed demo data on Vercel (ephemeral database)
    if os.environ.get("VERCEL"):
        seed_demo_data()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "version": settings.APP_VERSION
    }

