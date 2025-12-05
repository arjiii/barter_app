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


from ..supabase_client import get_supabase_client

@router.post("/signup")
async def signup(payload: dict, db: Session = Depends(get_db)):
	try:
		# Validate password exists
		password = payload.get("password", "")
		if not password:
			raise HTTPException(status_code=400, detail="Password is required")
		
		email = payload["email"]
		
		# Check if already registered in Users
		existing_user = db.query(models.User.id).filter(models.User.email == email).first()
		if existing_user:
			raise HTTPException(status_code=400, detail="Email already registered")
		
		# Generate password hash for local storage
		password_hash = hash_password(password)
		
		verification_method = payload.get("verification_method", "email")
		
		# Check if pending signup exists
		pending = db.query(models.PendingSignup).filter(models.PendingSignup.email == email).first()
		
		if pending:
			# Update existing pending signup
			pending.name = payload["name"]
			pending.password_hash = password_hash
			pending.location = payload.get("location")
			pending.latitude = payload.get("latitude")
			pending.longitude = payload.get("longitude")
			pending.verification_method = verification_method
		else:
			# Create new pending signup
			pending = models.PendingSignup(
				id=str(uuid4()),
				name=payload["name"],
				email=email,
				password_hash=password_hash,
				location=payload.get("location"),
				latitude=payload.get("latitude"),
				longitude=payload.get("longitude"),
				verification_method=verification_method
			)
			db.add(pending)
		
		db.commit()
		
		if verification_method == 'email':
			# Use Supabase for OTP
			try:
				supabase = get_supabase_client()
				# sign_in_with_otp sends a magic link/code
				supabase.auth.sign_in_with_otp({"email": email})
				
				return {
					"message": "Verification code sent via Supabase. Please check your email.",
					"email": email,
					"method": "email"
				}
			except Exception as e:
				print(f"Failed to send Supabase OTP: {str(e)}")
				raise HTTPException(status_code=500, detail=f"Failed to send verification email: {str(e)}")
		else:
			return {
				"message": "Registration request submitted. Please wait for admin approval.",
				"email": email,
				"method": "admin"
			}
	except HTTPException:
		raise
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))
	except Exception as e:
		print(f"Signup error: {str(e)}")
		raise HTTPException(status_code=500, detail=f"An error occurred during registration: {str(e)}")


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
	# Include location, coordinates, and status in the query
	user = db.query(
		models.User.id,
		models.User.name,
		models.User.email,
		models.User.password_hash,
		models.User.role,
		models.User.location,
		models.User.latitude,
		models.User.longitude,
		models.User.is_verified,
		models.User.status
	).filter(models.User.email == form.username).first()
	
	if not user or not verify_password(form.password, user.password_hash):
		raise HTTPException(status_code=400, detail="Invalid credentials")
	
	if not user.is_verified:
		# This might happen for legacy users or if we keep is_verified=False logic
		raise HTTPException(status_code=400, detail="Please verify your email address before logging in.")
	
	# Check if user account is suspended
	if hasattr(user, 'status') and user.status == 'suspended':
		raise HTTPException(status_code=403, detail="Your account has been suspended. Please contact support for assistance.")

	token = create_access_token(user.id)
	return {
		"user": {
			"id": user.id, 
			"name": user.name, 
			"email": user.email, 
			"role": user.role,
			"location": getattr(user, "location", None),
			"latitude": getattr(user, "latitude", None),
			"longitude": getattr(user, "longitude", None)
		}, 
		"token": token
	}


@router.get("/me")
def me(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
	if not authorization or not authorization.lower().startswith("bearer "):
		raise HTTPException(status_code=401, detail="Missing token")
	token = authorization.split(" ", 1)[1]
	user_id = decode_token(token)
	if not user_id:
		raise HTTPException(status_code=401, detail="Invalid token")
	# Include location and coordinates in the query
	user = db.query(
		models.User.id,
		models.User.name,
		models.User.email,
		models.User.role,
		models.User.location,
		models.User.latitude,
		models.User.longitude
	).filter(models.User.id == user_id).first()
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	return {
		"id": user.id, 
		"name": user.name, 
		"email": user.email, 
		"role": user.role,
		"location": getattr(user, "location", None),
		"latitude": getattr(user, "latitude", None),
		"longitude": getattr(user, "longitude", None)
	}


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
    latitude = payload.get("latitude")
    longitude = payload.get("longitude")
    
    if not name or not isinstance(name, str) or not name.strip():
        raise HTTPException(status_code=400, detail="Name is required")
    
    # Update using SQL UPDATE - include location and coordinates if provided
    from sqlalchemy import update
    update_values = {"name": name.strip()}
    
    if location is not None:  # Allow empty string to clear location
        update_values["location"] = location.strip() if isinstance(location, str) else None
    
    if latitude is not None:
        update_values["latitude"] = latitude
    
    if longitude is not None:
        update_values["longitude"] = longitude
    
    stmt = update(models.User).where(models.User.id == user_row.id).values(**update_values)
    db.execute(stmt)
    db.commit()
    
    # Query back with location and coordinates included
    updated_user = db.query(
        models.User.id,
        models.User.name,
        models.User.email,
        models.User.location,
        models.User.latitude,
        models.User.longitude
    ).filter(models.User.id == user_row.id).first()
    
    return {
        "id": updated_user.id,
        "name": updated_user.name,
        "email": updated_user.email,
        "location": getattr(updated_user, "location", None),
        "latitude": getattr(updated_user, "latitude", None),
        "longitude": getattr(updated_user, "longitude", None)
    }


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
	"""Verify email address using Supabase OTP and create account"""
	email = payload.get("email", "").strip().lower()
	otp = payload.get("otp", "").strip()
	
	if not email or not otp:
		raise HTTPException(status_code=400, detail="Email and OTP are required")
	
	# Verify with Supabase
	try:
		supabase = get_supabase_client()
		# Verify the OTP
		res = supabase.auth.verify_otp({"email": email, "token": otp, "type": "email"})
		
		if not res.user:
			raise HTTPException(status_code=400, detail="Invalid OTP")
			
	except Exception as e:
		print(f"Supabase verification failed: {str(e)}")
		raise HTTPException(status_code=400, detail="Invalid verification code or code expired.")

	# If we get here, Supabase verified the email. Now create/update local user.
	
	# Check PendingSignup first
	pending = db.query(models.PendingSignup).filter(models.PendingSignup.email == email).first()
	
	if pending:
		# Create User
		user_id = str(uuid4())
		new_user = models.User(
			id=user_id,
			name=pending.name,
			email=pending.email,
			password_hash=pending.password_hash,
			role='user',
			is_verified=True,
			location=pending.location,
			latitude=pending.latitude,
			longitude=pending.longitude
		)
		db.add(new_user)
		
		# Delete pending
		db.delete(pending)
		db.commit()
		
		# Generate token
		token = create_access_token(user_id)
		
		return {
			"message": "Email verified and account created successfully",
			"token": token,
			"user": {
				"id": new_user.id,
				"name": new_user.name,
				"email": new_user.email,
				"role": new_user.role,
				"location": new_user.location,
				"latitude": new_user.latitude,
				"longitude": new_user.longitude
			}
		}

	# Fallback: Check existing Users (legacy flow or re-verification)
	user = db.query(
		models.User.id,
		models.User.name,
		models.User.email,
		models.User.is_verified,
		models.User.role,
		models.User.location,
		models.User.latitude,
		models.User.longitude
	).filter(models.User.email == email).first()
	
	if not user:
		raise HTTPException(status_code=400, detail="User not found. Please sign up again.")
	
	if user.is_verified:
		return {"message": "Email is already verified"}
		
	# Mark email as verified
	stmt = update(models.User).where(models.User.id == user.id).values(
		is_verified=True,
		otp_code=None,
		otp_expires_at=None
	)
	db.execute(stmt)
	db.commit()
	
	token = create_access_token(user.id)
	
	return {
		"message": "Email verified successfully",
		"token": token,
		"user": {
			"id": user.id,
			"name": user.name,
			"email": user.email,
			"role": user.role,
			"location": getattr(user, "location", None),
			"latitude": getattr(user, "latitude", None),
			"longitude": getattr(user, "longitude", None)
		}
	}


@router.post("/resend-verification")
async def resend_verification(payload: dict, db: Session = Depends(get_db)):
	"""Resend verification email using Supabase"""
	email = payload.get("email", "").strip().lower()
	
	if not email:
		raise HTTPException(status_code=400, detail="Email is required")
	
	try:
		supabase = get_supabase_client()
		supabase.auth.sign_in_with_otp({"email": email})
		return {"message": "Verification code sent."}
	except Exception as e:
		print(f"Failed to resend Supabase OTP: {str(e)}")
		raise HTTPException(status_code=500, detail="Failed to send verification email.")


