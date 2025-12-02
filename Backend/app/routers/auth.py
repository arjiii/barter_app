from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import update
from uuid import uuid4
from datetime import datetime, timedelta
from ..database import get_db
from .. import models
from ..security import hash_password, verify_password, create_access_token, decode_token
from ..email_service import send_password_reset_email, send_verification_email, generate_reset_token, generate_verification_token, generate_otp, send_otp_email


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
async def signup(payload: dict, db: Session = Depends(get_db)):
	try:
		# Validate password exists
		password = payload.get("password", "")
		if not password:
			raise HTTPException(status_code=400, detail="Password is required")
		
		# email uniqueness check - use explicit column selection
		existing = db.query(models.User.id).filter(models.User.email == payload["email"]).first()
		if existing:
			raise HTTPException(status_code=400, detail="Email already registered")
		
		# Generate OTP
		otp = generate_otp()
		otp_expires = datetime.utcnow() + timedelta(minutes=10)
		
		user = models.User(
			id=str(uuid4()),
			name=payload["name"],
			email=payload["email"],
			password_hash=hash_password(password),
			role='user',
			is_verified=False,
			otp_code=otp,
			otp_expires_at=otp_expires,
			location=payload.get("location"),
			latitude=payload.get("latitude"),
			longitude=payload.get("longitude")
		)
		db.add(user)
		db.commit()
		
		# Send OTP email
		try:
			await send_otp_email(payload["email"], otp, payload["name"])
		except Exception as e:
			print(f"Failed to send OTP email: {str(e)}")
			# Continue with signup even if email fails
		
		# Query the user back with explicit columns
		user_data = db.query(
			models.User.id,
			models.User.name,
			models.User.email
		).filter(models.User.id == user.id).first()
		token = create_access_token(user.id)
		return {
			"user": {"id": user_data.id, "name": user_data.name, "email": user_data.email},
			"token": token,
			"message": "Account created. Please check your email to verify your account."
		}
	except HTTPException:
		raise
	except ValueError as e:
		# Handle password validation errors
		raise HTTPException(status_code=400, detail=str(e))
	except Exception as e:
		# Log the error for debugging
		import traceback
		error_details = traceback.format_exc()
		print(f"Signup error: {str(e)}")
		print(f"Traceback: {error_details}")
		# Don't expose internal error details to client
		error_message = str(e)
		# Filter out bcrypt 72-byte limit errors if they somehow occur
		if "72" in error_message and "byte" in error_message.lower():
			error_message = "An error occurred during registration. Please try again."
		raise HTTPException(status_code=500, detail=error_message)


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
	# Include location in the query
	user = db.query(
		models.User.id,
		models.User.name,
		models.User.email,
		models.User.password_hash,
		models.User.location
	).filter(models.User.email == form.username).first()
	if not user or not verify_password(form.password, user.password_hash):
		raise HTTPException(status_code=400, detail="Invalid credentials")
	
	# Check if user is verified - use getattr to be safe if column wasn't loaded (though it's not in the query above, we should add it)
	# Re-query or check is_verified if we add it to the query
	user_verification = db.query(models.User.is_verified).filter(models.User.id == user.id).scalar()
	if not user_verification:
		raise HTTPException(status_code=400, detail="Please verify your email address before logging in.")

	token = create_access_token(user.id)
	return {"user": {"id": user.id, "name": user.name, "email": user.email, "location": getattr(user, "location", None)}, "token": token}


@router.get("/me")
def me(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
	if not authorization or not authorization.lower().startswith("bearer "):
		raise HTTPException(status_code=401, detail="Missing token")
	token = authorization.split(" ", 1)[1]
	user_id = decode_token(token)
	if not user_id:
		raise HTTPException(status_code=401, detail="Invalid token")
	# Include location in the query
	user = db.query(
		models.User.id,
		models.User.name,
		models.User.email,
		models.User.location
	).filter(models.User.id == user_id).first()
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	return {"id": user.id, "name": user.name, "email": user.email, "location": getattr(user, "location", None)}


def _require_user_from_token(authorization: str | None, db: Session):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    # Use explicit column selection to avoid loading location if it doesn't exist
    user = db.query(
        models.User.id,
        models.User.name,
        models.User.email,
        models.User.password_hash
    ).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/profile")
def update_profile(payload: dict, authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    user_row = _require_user_from_token(authorization, db)
    name = payload.get("name")
    location = payload.get("location")
    if not name or not isinstance(name, str) or not name.strip():
        raise HTTPException(status_code=400, detail="Name is required")
    # Update using SQL UPDATE - include location if provided
    from sqlalchemy import update
    update_values = {"name": name.strip()}
    if location is not None:  # Allow empty string to clear location
        update_values["location"] = location.strip() if isinstance(location, str) else None
    stmt = update(models.User).where(models.User.id == user_row.id).values(**update_values)
    db.execute(stmt)
    db.commit()
    # Query back with location included
    updated_user = db.query(
        models.User.id,
        models.User.name,
        models.User.email,
        models.User.location
    ).filter(models.User.id == user_row.id).first()
    return {"id": updated_user.id, "name": updated_user.name, "email": updated_user.email, "location": getattr(updated_user, "location", None)}


@router.post("/change-password")
def change_password(payload: dict, authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    user_row = _require_user_from_token(authorization, db)
    old_password = payload.get("old_password")
    new_password = payload.get("new_password")
    if not old_password or not new_password:
        raise HTTPException(status_code=400, detail="Old and new passwords are required")
    
    if not verify_password(old_password, user_row.password_hash):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    # Update using SQL UPDATE to avoid loading full model with location column
    from sqlalchemy import update
    stmt = update(models.User).where(models.User.id == user_row.id).values(password_hash=hash_password(new_password))
    db.execute(stmt)
    db.commit()
    return {"message": "Password updated"}


@router.get("/user/{user_id}")
def get_user_public(user_id: str, db: Session = Depends(get_db)):
	# Use explicit column selection to avoid loading location if it doesn't exist
	user = db.query(
		models.User.id,
		models.User.name,
		models.User.email
	).filter(models.User.id == user_id).first()
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	return {"id": user.id, "name": user.name, "email": user.email}


@router.post("/forgot-password")
async def forgot_password(payload: dict, db: Session = Depends(get_db)):
	"""Request password reset - sends email with reset token"""
	email = payload.get("email", "").strip().lower()
	if not email:
		raise HTTPException(status_code=400, detail="Email is required")
	
	# Find user by email
	user = db.query(
		models.User.id,
		models.User.name,
		models.User.email
	).filter(models.User.email == email).first()
	
	# Always return success message (security: don't reveal if email exists)
	if user:
		# Generate reset token
		reset_token = generate_reset_token()
		reset_expires = datetime.utcnow() + timedelta(hours=1)
		
		# Update user with reset token
		stmt = update(models.User).where(models.User.id == user.id).values(
			password_reset_token=reset_token,
			password_reset_expires=reset_expires
		)
		db.execute(stmt)
		db.commit()
		
		# Send reset email
		try:
			await send_password_reset_email(user.email, reset_token, user.name)
		except Exception as e:
			print(f"Failed to send password reset email: {str(e)}")
			# Still return success for security
	
	return {"message": "If an account with that email exists, a password reset link has been sent."}


@router.post("/reset-password")
async def reset_password(payload: dict, db: Session = Depends(get_db)):
	"""Reset password using token from email"""
	token = payload.get("token", "").strip()
	new_password = payload.get("new_password", "")
	
	if not token or not new_password:
		raise HTTPException(status_code=400, detail="Token and new password are required")
	
	# Find user by reset token
	user = db.query(
		models.User.id,
		models.User.password_reset_token,
		models.User.password_reset_expires
	).filter(models.User.password_reset_token == token).first()
	
	if not user:
		raise HTTPException(status_code=400, detail="Invalid or expired reset token")
	
	# Check if token is expired
	if not user.password_reset_expires or user.password_reset_expires < datetime.utcnow():
		raise HTTPException(status_code=400, detail="Reset token has expired")
	
	# Update password and clear reset token
	stmt = update(models.User).where(models.User.id == user.id).values(
		password_hash=hash_password(new_password),
		password_reset_token=None,
		password_reset_expires=None
	)
	db.execute(stmt)
	db.commit()
	
	return {"message": "Password has been reset successfully"}


@router.post("/verify-email")
async def verify_email(payload: dict, db: Session = Depends(get_db)):
	"""Verify email address using OTP"""
	email = payload.get("email", "").strip().lower()
	otp = payload.get("otp", "").strip()
	
	if not email or not otp:
		raise HTTPException(status_code=400, detail="Email and OTP are required")
	
	# Find user by email
	user = db.query(
		models.User.id,
		models.User.otp_code,
		models.User.otp_expires_at,
		models.User.is_verified
	).filter(models.User.email == email).first()
	
	if not user:
		raise HTTPException(status_code=400, detail="Invalid email or OTP")
	
	if user.is_verified:
		return {"message": "Email is already verified"}
		
	# Check OTP
	if not user.otp_code or user.otp_code != otp:
		raise HTTPException(status_code=400, detail="Invalid OTP")
		
	# Check expiration
	if not user.otp_expires_at or user.otp_expires_at < datetime.utcnow():
		raise HTTPException(status_code=400, detail="OTP has expired")
	
	# Mark email as verified and clear OTP
	stmt = update(models.User).where(models.User.id == user.id).values(
		is_verified=True,
		otp_code=None,
		otp_expires_at=None
	)
	db.execute(stmt)
	db.commit()
	
	return {"message": "Email verified successfully"}


@router.post("/resend-verification")
async def resend_verification(payload: dict, db: Session = Depends(get_db)):
	"""Resend verification email"""
	email = payload.get("email", "").strip().lower()
	
	if not email:
		raise HTTPException(status_code=400, detail="Email is required")
	
	# Find user by email
	user = db.query(
		models.User.id,
		models.User.name,
		models.User.email,
		models.User.is_verified,
		models.User.email_verification_token
	).filter(models.User.email == email).first()
	
	if not user:
		# Don't reveal if email exists
		return {"message": "If an account with that email exists and is not verified, a verification email has been sent."}
	
	if user.is_verified:
		return {"message": "Email is already verified"}
	
	# Generate new OTP
	otp = generate_otp()
	otp_expires = datetime.utcnow() + timedelta(minutes=10)
	
	# Update user with new OTP
	stmt = update(models.User).where(models.User.id == user.id).values(
		otp_code=otp,
		otp_expires_at=otp_expires
	)
	db.execute(stmt)
	db.commit()
	
	# Send OTP email
	try:
		await send_otp_email(user.email, otp, user.name)
	except Exception as e:
		print(f"Failed to send OTP email: {str(e)}")
	
	return {"message": "If an account with that email exists and is not verified, a verification code has been sent."}


