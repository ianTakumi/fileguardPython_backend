# 📌 FileGuard – Django Backend

This is the backend service for **FileGuard**, built with **Django** and **Django REST Framework**.

---

## 🚀 Requirements

- Python 3.10+
- pip (Python package manager)
- Virtual environment (`venv`)
- PostgreSQL (Supabase or local)

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/ianTakumi/fileguardPython_backend.git
cd fileguardPython_backend
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

Activate:

- **Windows (PowerShell / CMD):**

  ```bash
  venv\Scripts\activate
  ```

- **Linux / Mac:**

  ```bash
  source venv/bin/activate
  ```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup environment variables

Create a `.env` file inside `backend/` and add:

```env
DEBUG=True

# CLOUDINARY CONFIG
CLOUDINARY_NAME=dzydn2faa
CLOUDINARY_API_KEY=347892895557551
CLOUDINARY_API_SECRET=fn7p_ObO4IdccvQ-MkubjW-HW4A
CLOUDINARY_URL=cloudinary://347892895557551:fn7p_ObO4IdccvQ-MkubjW-HW4A@dzydn2faa

EMAIL_HOST_USER=fileguard.corp@gmail.com
EMAIL_HOST_PASSWORD=dhns xeef udmp vlrm

SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres.irnkkwywoqxvchtmooto
SUPABASE_DB_PASSWORD=lIANNEDELDACAN_245
SUPABASE_DB_HOST=aws-1-us-east-2.pooler.supabase.com
SUPABASE_URL=postgresql://postgres.irnkkwywoqxvchtmooto:postgres@aws-1-us-east-2.pooler.supabase.com:5432/postgres
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlybmtrd3l3b3F4dmNodG1vb3RvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg3OTg4ODIsImV4cCI6MjA3NDM3NDg4Mn0.srbROiMWJQe1IYDdRIaEOY3vdo_qaWdUAqHDHfE9wNc
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlybmtrd3l3b3F4dmNodG1vb3RvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODc5ODg4MiwiZXhwIjoyMDc0Mzc0ODgyfQ.rxGn9BSAIAycXG4IF20wzUuSJNbQEq_sDOZzedZascU
SUPABASE_PORT=5432
SUPABASE_POOL_MODE=session
SUPABASE_PROJECT_URL=https://irnkkwywoqxvchtmooto.supabase.co

PAYPAL_CLIENT_ID=AU1UXOnUYxbOmEsrADt5gjt4SdR2w9tUrzM6uE01Sev6s-0F41St5bSE5DcVpRY7iR4LqTuUXGc1YxEp
PAYPAL_CLIENT_SECRET=ELC4Y_-JvoxXEZSYe7ITwrJ82MN20FyvNnkLieyBkBp9VCIofduUvX3rrIIHPvGH6zTT6pXmiFd_Ftiz
PAYPAL_MODE=sandbox

FRONTEND_URL=http://localhost:5173
```

### 5. Start the development server

````bash
python manage.py runserver
```5

The server will be available at:
👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🧪 Running with start.bat (Windows only)

If you want to run it faster, use the provided `start.bat`:

```bat
@echo off
call venv\Scripts\activate
python manage.py runserver
pause
````

Just double-click `start.bat` to start the server.

---
