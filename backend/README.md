# BillOS Backend

## Quick Start

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Features

- **Authentication**: Phone + password login, JWT tokens
- **Products**: CRUD, stock management, low stock alerts
- **Customers**: CRM, credit/udhar tracking, outstanding management
- **Invoices**: GST/Non-GST billing, payment tracking
- **Dashboard**: Daily summary, cash position, trends

## Database

Using SQLite for development. To switch to MySQL:
1. Update `DATABASE_URL` in `.env`
2. Install `pymysql`: `pip install pymysql`
