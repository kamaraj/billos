import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add backend directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

from app.core.database import SessionLocal, init_db
from app.models.tenant import Tenant
from app.models.user import User
from app.core.auth import get_password_hash

def seed_data():
    logger.info("Initializing database...")
    init_db()
    db = SessionLocal()
    
    try:
        # 1. Create Tenant
        tenant = db.query(Tenant).filter(Tenant.name == "Test Superstore").first()
        if not tenant:
            tenant = Tenant(
                name="Test Superstore",
                business_type="Retail",
                address="123 Market Street, Chennai",
                phone="9999999999",
                email="admin@teststore.com",
                plan="BUSINESS"
            )
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
            logger.info(f"Created Tenant: {tenant.name}")
        else:
            logger.info(f"Using existing Tenant: {tenant.name}")

        # 2. Create Users
        users_data = [
            {
                "name": "Kamaraj Admin",
                "phone": "9000000001", 
                "password": "pass", 
                "role": "OWNER"
            },
            {
                "name": "Store Manager",
                "phone": "9000000002",
                "password": "pass",
                "role": "MANAGER"
            },
            {
                "name": "Checkout Cashier",
                "phone": "9000000003",
                "password": "pass",
                "role": "CASHIER"
            }
        ]

        created = []
        for u in users_data:
            user = db.query(User).filter(User.phone == u["phone"]).first()
            if not user:
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
                db.refresh(user)
                logger.info(f"Created User: {u['name']} ({u['role']})")
                created.append(u)
            else:
                logger.info(f"User already exists: {u['name']}")
                # Password reset can be done here if needed, but skipping for now
                created.append(u)
        
        return created

    except Exception as e:
        logger.error(f"Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting seed process...")
    users = seed_data()
    print("\n--- CREDENTIALS ---")
    for u in users:
        print(f"Role: {u['role']:<10} | Name: {u['name']:<15} | Phone: {u['phone']} | Password: {u['password']}")
    print("-------------------")
