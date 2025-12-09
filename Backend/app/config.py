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
	
	# Frontend URL (used for redirect links in emails sent by Supabase)
	FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
	
	# Supabase configuration
	SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
	SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")

	# Blockchain (Sepolia) configuration
	sepolia_rpc_url: str | None = None
	backend_wallet_private_key: str | None = None
	contract_address: str | None = None


	class Config:
		env_file = ".env"
		extra = "allow"  # tolerate other env vars that may be present


settings = Settings()



