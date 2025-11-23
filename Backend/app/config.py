from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	# Example: mysql+pymysql://root:password@127.0.0.1:3306/bayanihan_exchange
	DATABASE_URL: str = "mysql+pymysql://root:@127.0.0.1:3306/bayanihan_exchange"
	CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174,http://localhost:3000,http://127.0.0.1:3000"
	SSL_CA_PATH: str | None = None
	# Optional: provide full PEM content via env (useful for Aiven). If set and
	# SSL_CA_PATH is empty, the backend will write this to a temp file and use it.
	SSL_CA_PEM: str | None = None

	class Config:
		env_file = ".env"


settings = Settings()



