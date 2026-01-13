# BillOS - Daily Business OS for MSMEs

A smart, AI-assisted billing and business management system for Indian micro & small merchants.

## 🎯 Features (MVP)

### Core Modules
- **Quick Billing** - Create invoices in < 15 seconds
- **Inventory Management** - Stock tracking with low-stock alerts
- **Customer CRM** - Credit/Udhar tracking with risk tagging
- **GST Support** - GST/Non-GST invoices with auto tax calculation
- **Cash Summary** - Daily cash position and outstanding tracking

### Coming Soon (Phase 2)
- **Daily Decision Agent** - AI-powered daily business advice
- **Credit Risk Agent** - Autonomous credit risk detection
- **Inventory Autopilot** - Predictive reorder recommendations
- **WhatsApp Integration** - Invoice sharing via WhatsApp
- **Offline-First** - Full app usable offline with sync

## 🏗️ Tech Stack

### Backend
- **FastAPI** - High-performance Python API
- **SQLAlchemy** - ORM with SQLite (upgradeable to MySQL)
- **Redis** - Caching and session management (optional)
- **APScheduler** - Agent scheduling

### Frontend
- **React 18** - Modern React with hooks
- **Vite** - Fast development build tool
- **React Router** - Client-side routing
- **Lucide Icons** - Beautiful icon system

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Access the App
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
miniERP/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Config, auth, database
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── main.py        # FastAPI app
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── context/       # React context
│   │   ├── pages/         # Page components
│   │   ├── utils/         # API client
│   │   ├── App.jsx        # Main app
│   │   └── index.css      # Global styles
│   └── package.json
│
└── README.md
```

## 💰 Monetization Plans

| Plan | Price | Features |
|------|-------|----------|
| Free | ₹0 | Basic billing, 50 invoices/month |
| Starter | ₹199/mo | Inventory + Cash tracking |
| Pro | ₹499/mo | GST + AI Insights |
| Business | ₹999/mo | Multi-user, Multi-branch |

## 📊 Target Users

1. **Kirana Store Owners** - High volume, simple products
2. **Medical/Pharmacy Shops** - Batch & expiry tracking
3. **Small Wholesalers** - Credit cycles, bulk billing
4. **Hardware/Electrical** - SKU management
5. **Textile/Garments** - Multi-price lists

## 🔐 Default Login

After registration, you can login with:
- Phone: Your registered phone number
- Password: Your chosen password

## 📝 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new business
- `POST /api/auth/login` - Login

### Products
- `GET /api/products/` - List products
- `POST /api/products/` - Create product
- `GET /api/products/alerts/low-stock` - Low stock alerts

### Customers
- `GET /api/customers/` - List customers
- `POST /api/customers/` - Create customer
- `GET /api/customers/outstanding` - Outstanding customers

### Invoices
- `GET /api/invoices/` - List invoices
- `POST /api/invoices/` - Create invoice
- `GET /api/invoices/summary` - Sales summary
- `POST /api/invoices/payments` - Record payment

### Dashboard
- `GET /api/dashboard/summary` - Daily summary
- `GET /api/dashboard/cash-summary` - Cash by payment mode
- `GET /api/dashboard/trends` - Sales trends
- `GET /api/dashboard/top-products` - Top selling products

## 🎯 North Star Metrics

1. **Invoices per merchant per day** - Primary usage metric
2. **DAU/MAU ratio** - Daily engagement
3. **Time to invoice** - Speed of billing
4. **Paid conversion %** - Monetization health

## 📜 License

MIT License - Built for MSME growth in India.
