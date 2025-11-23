FastAPI backend for Bayanihan Exchange

Setup

1. Python 3.10+ recommended.
2. Create venv and install deps:
   - Windows PowerShell:
     - python -m venv .venv
     - .venv\\Scripts\\Activate.ps1
     - pip install -r Backend/requirements.txt
3. Configure DB URL (XAMPP MySQL): create `.env` at repo root or `Backend/app/.env` with:
   DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@127.0.0.1:3306/bayanihan_exchange
4. Run server:
   - uvicorn Backend.app.main:app --reload

Endpoints

- GET /health
- GET/POST /categories
- GET/POST /items
- GET/POST /trades
- GET/POST /messages

Notes

- Models align with `Backend/mysql/schema.sql`.
- If JSON columns are not supported (older MariaDB), change items.images to TEXT and store JSON string.



