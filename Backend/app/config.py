from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
	# Example: mysql+pymysql://root:password@127.0.0.1:3306/bayanihan_exchange
	DATABASE_URL: str = "mysql+pymysql://root:@127.0.0.1:3306/bayanihan_exchange"
	# Default CORS origins for development; override in production
	CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174,http://localhost:3000,http://127.0.0.1:3000"
	SSL_CA_PATH: str | None = None
	# Optional: provide full PEM content via env (useful for Aiven). If set and
	# SSL_CA_PATH is empty, the backend will write this to a temp file and use it.
	SSL_CA_PEM: str | None = None
	SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
	
	# Email configuration
	MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
	MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
	MAIL_FROM: str = os.getenv("MAIL_FROM", "noreply@bayanihanexchange.com")
	MAIL_PORT: int = int(os.getenv("MAIL_PORT", "587"))
	MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
	MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "Bayanihan Exchange")
	MAIL_STARTTLS: bool = True
	MAIL_SSL_TLS: bool = False
	USE_CREDENTIALS: bool = True
	VALIDATE_CERTS: bool = True
	
	# Frontend URL for email links
	FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
	
	# Supabase configuration
	SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
	SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")


	class Config:
		env_file = ".env"


settings = Settings()



