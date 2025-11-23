from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os, tempfile
from .config import settings

# Optional SSL CA support for Aiven / other managed MySQL services.
# Provide either:
# - SSL_CA_PATH: path to a CA certificate file
# - SSL_CA_PEM: full PEM content (the backend will write it to a temp file)
connect_args = {}
ssl_ca = settings.SSL_CA_PATH

# If no path provided but PEM content is available, write it to a temp file
if not ssl_ca and getattr(settings, "SSL_CA_PEM", None):
    pem_content = settings.SSL_CA_PEM.strip()
    if pem_content:
        tmp = tempfile.NamedTemporaryFile("w", delete=False, suffix="-aiven-ca.pem")
        tmp.write(pem_content)
        tmp.flush()
        tmp.close()
        ssl_ca = tmp.name

if ssl_ca:
    # If a relative path was provided, resolve it relative to the Backend directory
    if not os.path.isabs(ssl_ca) and not os.path.exists(ssl_ca):
        app_dir = os.path.dirname(__file__)
        backend_dir = os.path.dirname(app_dir)
        candidate = os.path.join(backend_dir, ssl_ca)
        if os.path.exists(candidate):
            ssl_ca = candidate
    # pymysql accepts an "ssl" dict with a "ca" key
    connect_args = {"ssl": {"ca": ssl_ca, "check_hostname": True}}

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, connect_args=connect_args if connect_args else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
	pass


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()



