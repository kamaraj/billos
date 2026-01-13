import sys
import os
import logging
from datetime import datetime, timedelta, date
import random

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
from app.models.product import Product
from app.models.customer import Customer
from app.models.invoice import Invoice, InvoiceItem
from app.core.auth import get_password_hash

def seed_qatar():
    logger.info("Initializing database for Qatar data...")
    init_db()
    db = SessionLocal()
    
    try:
        # 1. Create Tenant
        tenant_name = "Doha Hypermarket"
        tenant = db.query(Tenant).filter(Tenant.name == tenant_name).first()
        if not tenant:
            tenant = Tenant(
                name=tenant_name,
                business_type="Supermarket",
                address="West Bay, Doha, Qatar",
                phone="97444445555",
                email="info@dohahyper.qa",
                plan="BUSINESS",
                currency="QAR",
                is_gst_enabled=True 
            )
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
            logger.info(f"Created Tenant: {tenant.name}")
        else:
            logger.info(f"Using existing Tenant: {tenant.name}")
            if tenant.currency != "QAR":
                tenant.currency = "QAR"
                db.add(tenant)
                db.commit()

        # 2. Create Users
        users_data = [
            {"name": "Abdulla Al-Thani", "phone": "97411112222", "password": "pass", "role": "OWNER"},
            {"name": "Mohammed Ali", "phone": "97433334444", "password": "pass", "role": "MANAGER"},
            {"name": "Pareekutty", "phone": "97455556666", "password": "pass", "role": "CASHIER"}
        ]

        created_users = []
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
                logger.info(f"Created User: {u['name']}")
                created_users.append(u)
            else:
                created_users.append(u)

        # 3. Create Products
        products_data = [
            {"name": "Almarai Fresh Milk 2L", "price": 10.0, "stock": 50, "sku": "MILK2L", "cat": "Dairy"},
            {"name": "Baladna Yoghurt 1kg", "price": 6.5, "stock": 30, "sku": "YOG1KG", "cat": "Dairy"},
            {"name": "QFM Flour No.1 5kg", "price": 18.0, "stock": 100, "sku": "FLOUR5", "cat": "Staples"},
            {"name": "Basmati Rice 5kg", "price": 35.0, "stock": 40, "sku": "RICE5", "cat": "Staples"},
            {"name": "Arabic Bread (Khubz)", "price": 5.0, "stock": 50, "sku": "BREAD", "cat": "Bakery"},
            {"name": "Hummus 250g", "price": 8.0, "stock": 20, "sku": "HUMMUS", "cat": "Deli"},
            {"name": "Australian Lamb Chops", "price": 65.0, "stock": 15, "sku": "LAMB", "cat": "Meat", "unit": "KG"},
            {"name": "Qatari Dates 1kg", "price": 45.0, "stock": 60, "sku": "DATES", "cat": "Produce"}
        ]

        for p in products_data:
            prod = db.query(Product).filter(Product.name == p["name"], Product.tenant_id == tenant.id).first()
            if not prod:
                prod = Product(
                    tenant_id=tenant.id,
                    name=p["name"],
                    selling_price=p["price"],
                    cost_price=p["price"] * 0.7,
                    current_stock=p["stock"],
                    sku=p["sku"],
                    category=p["cat"],
                    unit=p.get("unit", "PCS"),
                    gst_rate=0.0
                )
                db.add(prod)
                logger.info(f"Created Product: {p['name']}")
        db.commit()

        # 4. Create Customers
        customers_data = [
            {"name": "Fatima Al-Sayed", "phone": "97466667777", "risk": "NORMAL", "balance": 0},
            {"name": "John Doe", "phone": "97455558888", "risk": "LOW_RISK", "balance": 0},
            {"name": "Majlis Catering", "phone": "97444449999", "risk": "NORMAL", "balance": 1500}
        ]
        
        for c in customers_data:
            cust = db.query(Customer).filter(Customer.phone == c["phone"], Customer.tenant_id == tenant.id).first()
            if not cust:
                cust = Customer(
                    tenant_id=tenant.id,
                    name=c["name"],
                    phone=c["phone"],
                    risk_tag=c["risk"],
                    credit_limit=5000.0,
                    current_balance=c["balance"]
                )
                db.add(cust)
                logger.info(f"Created Customer: {c['name']}")
        db.commit()
        
        # 5. Create Sales History (Invoices)
        logger.info("Seeding Invoices Sales History...")
        products_db = {p.name: p for p in db.query(Product).filter(Product.tenant_id == tenant.id).all()}
        customers_db = db.query(Customer).filter(Customer.tenant_id == tenant.id).all()
        
        # Define some scenarios
        scenarios = [
            {"items": ["Almarai Fresh Milk 2L", "Arabic Bread (Khubz)"], "cust": None},
            {"items": ["Australian Lamb Chops", "Basmati Rice 5kg"], "cust": "Fatima Al-Sayed"},
            {"items": ["Qatari Dates 1kg", "Hummus 250g"], "cust": "John Doe"},
            {"items": ["QFM Flour No.1 5kg", "Baladna Yoghurt 1kg"], "cust": "Majlis Catering"},
            {"items": ["Basmati Rice 5kg"], "cust": None},
        ]
        
        # Check if invoices already exist to avoid dupes
        existing_count = db.query(Invoice).filter(Invoice.tenant_id == tenant.id).count()
        if existing_count < 5:
            for day in range(7):
                # Add 1-3 invoices per day
                num_inv = random.randint(1, 3)
                for _ in range(num_inv):
                    scenario = random.choice(scenarios)
                    inv_date = date.today() - timedelta(days=day)
                    
                    cust = None
                    if scenario["cust"]:
                        cust = next((c for c in customers_db if c.name == scenario["cust"]), None)
                    
                    new_inv = Invoice(
                        tenant_id=tenant.id,
                        invoice_no=f"INV-{random.randint(10000, 99999)}",
                        invoice_date=inv_date,
                        customer_id=cust.id if cust else None,
                        invoice_type="SALE",
                        payment_status="PAID",
                        created_at=datetime.utcnow() - timedelta(days=day)
                    )
                    db.add(new_inv)
                    db.flush()
                    
                    subtotal = 0
                    for item_name in scenario["items"]:
                        if item_name in products_db:
                            prod = products_db[item_name]
                            qty = random.randint(1, 3)
                            amount = prod.selling_price * qty
                            
                            inv_item = InvoiceItem(
                                tenant_id=tenant.id,
                                invoice_id=new_inv.id,
                                product_id=prod.id,
                                product_name=prod.name,
                                qty=qty,
                                unit_price=prod.selling_price,
                                subtotal=amount,
                                total=amount,
                                tax_amount=0
                            )
                            db.add(inv_item)
                            subtotal += amount
                    
                    new_inv.subtotal = subtotal
                    new_inv.total_amount = subtotal
                    new_inv.paid_amount = subtotal
                    db.add(new_inv)
            
            db.commit()
            logger.info("Seeded invoices successfully.")
        else:
            logger.info("Invoices already populated.")

        return created_users

    except Exception as e:
        logger.error(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting Qatar Seed...")
    users = seed_qatar()
    print("----------------")
    print("DONE")
