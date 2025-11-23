from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
import hashlib

SECRET_KEY = "change-me"  # put in .env for production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

# Argon2 is the preferred algorithm moving forward.
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Legacy context used to verify existing bcrypt hashes in the database.
legacy_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
	"""
	Hash the provided password using Argon2 (preferred algorithm).
	Argon2 does not suffer from the 72-byte limitation, so we don't need to
	truncate or pre-hash the password anymore.
	"""
	return pwd_context.hash(password)


def _legacy_sha256_input(password: str) -> str:
	"""
	Recreate the legacy password processing pipeline:
	1. Truncate to 72 bytes (bcrypt limit)
	2. Encode to UTF-8
	3. SHA-256 hexdigest (produces 64-character string)
	This matches how passwords were hashed previously, ensuring existing
	users can still sign in.
	"""
	password_bytes = password.encode('utf-8')
	if len(password_bytes) > 72:
		password_bytes = password_bytes[:72]
		password = password_bytes.decode('utf-8', errors='ignore')
	return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(plain_password: str, password_hash: str) -> bool:
	"""
	Verify password for both new Argon2 hashes and legacy bcrypt hashes.
	"""
	try:
		# Preferred path: Argon2 hashes start with "$argon2"
		if password_hash.startswith("$argon2"):
			return pwd_context.verify(plain_password, password_hash)

		# Fallback for legacy bcrypt hashes (prefixed with "$2")
		legacy_input = _legacy_sha256_input(plain_password)
		return legacy_context.verify(legacy_input, password_hash)
	except Exception:
		return False


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
	expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
	to_encode = {"sub": subject, "exp": expire}
	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt


def decode_token(token: str) -> str | None:
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		return payload.get("sub")
	except JWTError:
		return None


