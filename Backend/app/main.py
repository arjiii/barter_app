from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .config import settings
from .database import Base, engine, get_db
from . import models
from .routers import categories, items, trades, messages, auth, realtime

app = FastAPI(title="Bayanihan Exchange API")

app.add_middleware(
    CORSMiddleware,
    # Explicit, safe list of dev origins; avoid '*' with credentials
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(',')],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/health")
def health():
	return {"status": "ok"}


@app.get("/debug/db-info")
def debug_db_info():
	"""Debug endpoint to check database connection and user data"""
	from sqlalchemy import text
	from urllib.parse import urlparse
	
	# Get database URL info (masked for security)
	db_url = settings.DATABASE_URL
	parsed = urlparse(db_url.replace("mysql+pymysql://", "mysql://"))
	db_name = parsed.path.lstrip("/") if parsed.path else "unknown"
	masked_url = f"{parsed.scheme}://{parsed.hostname}:{parsed.port}/{db_name}"
	
	# Try to get database info
	current_db = "Not connected"
	user_count = "Not available"
	user_list = []
	
	try:
		db = next(get_db())
		# Get current database name from MySQL
		try:
			result = db.execute(text("SELECT DATABASE() as db_name"))
			current_db = result.scalar() or "Not selected"
		except Exception as e:
			current_db = f"Error: {str(e)}"
		
		# Count users
		try:
			user_count = db.query(models.User).count()
			users = db.query(
				models.User.id,
				models.User.name,
				models.User.email,
				models.User.created_at
			).limit(10).all()
			user_list = [
				{
					"id": u.id,
					"name": u.name,
					"email": u.email,
					"created_at": str(u.created_at) if u.created_at else None
				}
				for u in users
			]
		except Exception as e:
			user_count = f"Error: {str(e)}"
			user_list = []
		finally:
			db.close()
	except Exception as e:
		current_db = f"Connection error: {str(e)}"
		user_count = f"Connection error: {str(e)}"
	
	return {
		"database_url_masked": masked_url,
		"database_name_from_url": db_name,
		"current_database": current_db,
		"table_name": "users",
		"user_count": user_count,
		"users": user_list
	}

# Create tables (expects schema already present; harmless if exists)
Base.metadata.create_all(bind=engine)

# Routers
app.include_router(categories.router)
app.include_router(items.router)
app.include_router(trades.router)
app.include_router(messages.router)
app.include_router(auth.router)
app.include_router(realtime.router)



