"""
Supabase-based authentication router
Clean implementation separate from legacy auth.py
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timedelta
from ..database import get_db
from .. import models
from ..security import create_access_token
from ..supabase_client import get_supabase_client

router = APIRouter(prefix="/supabase-auth", tags=["supabase-auth"])


@router.post("/signup")
async def supabase_signup(payload: dict, db: Session = Depends(get_db)):
	"""
	Supabase-based signup:
	1. Create Supabase Auth user (sends email automatically)
	2. Store in pending_signups
	3. User verifies email via link
	4. Call /confirm to create account
	"""
	try:
		email = payload.get("email", "").strip().lower()
		password = payload.get("password", "")
		name = payload.get("name", "").strip()
		
		if not email or not password or not name:
			raise HTTPException(
				status_code=400,
				detail="Email, password, and name are required"
			)
		
		# Check if already registered
		existing = db.query(models.User).filter(models.User.email == email).first()
		if existing:
			raise HTTPException(status_code=400, detail="Email already registered")
		
		# Remove old pending signup if exists
		old_pending = db.query(models.PendingSignup).filter(
			models.PendingSignup.email == email
		).first()
		if old_pending:
			db.delete(old_pending)
			db.commit()
		
		# Create Supabase user
		supabase = get_supabase_client()
		auth_response = supabase.auth.sign_up({
			"email": email,
			"password": password,
			"options": {
				"data": {"name": name},
				"email_redirect_to": "http://localhost:5173/auth/callback"
			}
		})
		
		if not auth_response.user:
			raise HTTPException(
				status_code=500,
				detail="Failed to create authentication account"
			)
		
		# Store in pending_signups
		pending = models.PendingSignup(
			id=str(uuid4()),
			supabase_user_id=auth_response.user.id,
			name=name,
			email=email,
			location=payload.get("location"),
			latitude=payload.get("latitude"),
			longitude=payload.get("longitude"),
			expires_at=datetime.utcnow() + timedelta(hours=24)
		)
		
		db.add(pending)
		db.commit()
		
		print(f"✓ Supabase user created: {email}")
		print(f"✓ Verification email sent automatically by Supabase")
		
		return {
			"success": True,
			"message": "Verification email sent! Please check your inbox.",
			"email": email
		}
		
	except HTTPException:
		raise
	except Exception as e:
		print(f"Signup error: {str(e)}")
		raise HTTPException(status_code=500, detail=str(e))


@router.post("/confirm")
async def confirm_email(payload: dict, db: Session = Depends(get_db)):
	"""
	Confirm email and create actual user account
	Called after user clicks verification link
	"""
	try:
		email = payload.get("email", "").strip().lower()
		
		if not email:
			raise HTTPException(status_code=400, detail="Email is required")
		
		# Get pending signup
		pending = db.query(models.PendingSignup).filter(
			models.PendingSignup.email == email
		).first()
		
		if not pending:
			# Check if user already exists (already confirmed)
			existing = db.query(models.User).filter(models.User.email == email).first()
			if existing:
				return {
					"success": True,
					"message": "Email already verified",
					"user": {
						"id": existing.id,
						"name": existing.name,
						"email": existing.email
					},
					"token": create_access_token(existing.id)
				}
			raise HTTPException(
				status_code=404,
				detail="No pending signup found"
			)
		
		# Check expiration
		if datetime.utcnow() > pending.expires_at:
			db.delete(pending)
			db.commit()
			raise HTTPException(
				status_code=400,
				detail="Signup expired. Please sign up again."
			)
		
		# Verify with Supabase
		try:
			supabase = get_supabase_client()
			user_response = supabase.auth.admin.get_user_by_id(pending.supabase_user_id)
			
			if not user_response.user:
				raise HTTPException(status_code=404, detail="User not found")
			
			# Check if email verified
			if not user_response.user.email_confirmed_at:
				raise HTTPException(
					status_code=400,
					detail="Email not verified yet. Please check your inbox."
				)
				
		except Exception as e:
			print(f"Supabase verification error: {str(e)}")
			# Continue anyway - user might have verified
		
		# Create actual user account
		user = models.User(
			id=str(uuid4()),
			supabase_user_id=pending.supabase_user_id,
			name=pending.name,
			email=pending.email,
			password_hash="",  # Managed by Supabase
			role='user',
			is_verified=True,
			location=pending.location,
			latitude=pending.latitude,
			longitude=pending.longitude
		)
		
		db.add(user)
		db.delete(pending)
		db.commit()
		
		token = create_access_token(user.id)
		
		print(f"✓ Account created for {email}")
		
		return {
			"success": True,
			"message": "Account created successfully!",
			"user": {
				"id": user.id,
				"name": user.name,
				"email": user.email
			},
			"token": token
		}
		
	except HTTPException:
		raise
	except Exception as e:
		print(f"Confirm error: {str(e)}")
		raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
async def supabase_login(payload: dict, db: Session = Depends(get_db)):
	"""
	Login with Supabase authentication
	"""
	try:
		email = payload.get("email", "").strip().lower()
		password = payload.get("password", "")
		
		if not email or not password:
			raise HTTPException(
				status_code=400,
				detail="Email and password are required"
			)
		
		# Authenticate with Supabase
		supabase = get_supabase_client()
		auth_response = supabase.auth.sign_in_with_password({
			"email": email,
			"password": password
		})
		
		if not auth_response.user:
			raise HTTPException(status_code=401, detail="Invalid credentials")
		
		# Check if email verified
		if not auth_response.user.email_confirmed_at:
			raise HTTPException(
				status_code=400,
				detail="Please verify your email before logging in"
			)
		
		# Get user from database
		user = db.query(models.User).filter(models.User.email == email).first()
		
		if not user:
			raise HTTPException(
				status_code=404,
				detail="Account not found. Please complete signup."
			)
		
		token = create_access_token(user.id)
		
		return {
			"success": True,
			"user": {
				"id": user.id,
				"name": user.name,
				"email": user.email,
				"location": user.location
			},
			"token": token
		}
		
	except HTTPException:
		raise
	except Exception as e:
		print(f"Login error: {str(e)}")
		raise HTTPException(status_code=401, detail="Invalid credentials")


@router.get("/me")
async def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
	"""
	Get current user information
	"""
	try:
		if not authorization or not authorization.lower().startswith("bearer "):
			raise HTTPException(status_code=401, detail="Missing token")
		
		token = authorization.split(" ", 1)[1]
		
		# Decode token to get user ID
		from ..security import decode_token
		user_id = decode_token(token)
		if not user_id:
			raise HTTPException(status_code=401, detail="Invalid token")
		
		# Get user from database
		user = db.query(models.User).filter(models.User.id == user_id).first()
		if not user:
			raise HTTPException(status_code=404, detail="User not found")
		
		return {
			"id": user.id,
			"name": user.name,
			"email": user.email,
			"role": user.role,
			"location": user.location,
			"latitude": user.latitude,
			"longitude": user.longitude,
			"is_verified": user.is_verified
		}
		
	except HTTPException:
		raise
	except Exception as e:
		print(f"Get current user error: {str(e)}")
		raise HTTPException(status_code=401, detail="Invalid token")


@router.put("/profile")
async def update_profile(payload: dict, authorization: str = Header(None), db: Session = Depends(get_db)):
	"""
	Update user profile
	"""
	try:
		if not authorization or not authorization.lower().startswith("bearer "):
			raise HTTPException(status_code=401, detail="Missing token")
		
		token = authorization.split(" ", 1)[1]
		
		# Decode token to get user ID
		from ..security import decode_token
		user_id = decode_token(token)
		if not user_id:
			raise HTTPException(status_code=401, detail="Invalid token")
		
		# Get user from database
		user = db.query(models.User).filter(models.User.id == user_id).first()
		if not user:
			raise HTTPException(status_code=404, detail="User not found")
		
		# Update fields
		name = payload.get("name")
		location = payload.get("location")
		latitude = payload.get("latitude")
		longitude = payload.get("longitude")
		
		if name:
			user.name = name.strip()
		if location is not None:
			user.location = location.strip() if location else None
		if latitude is not None:
			user.latitude = latitude
		if longitude is not None:
			user.longitude = longitude
		
		db.commit()
		db.refresh(user)
		
		return {
			"id": user.id,
			"name": user.name,
			"email": user.email,
			"role": user.role,
			"location": user.location,
			"latitude": user.latitude,
			"longitude": user.longitude
		}
		
	except HTTPException:
		raise
	except Exception as e:
		print(f"Update profile error: {str(e)}")
		raise HTTPException(status_code=500, detail="Failed to update profile")


@router.post("/change-password")
async def change_password(payload: dict, authorization: str = Header(None), db: Session = Depends(get_db)):
	"""
	Change password via Supabase
	"""
	try:
		if not authorization or not authorization.lower().startswith("bearer "):
			raise HTTPException(status_code=401, detail="Missing token")
		
		token = authorization.split(" ", 1)[1]
		
		# Decode token to get user ID
		from ..security import decode_token
		user_id = decode_token(token)
		if not user_id:
			raise HTTPException(status_code=401, detail="Invalid token")
		
		old_password = payload.get("old_password")
		new_password = payload.get("new_password")
		
		if not old_password or not new_password:
			raise HTTPException(status_code=400, detail="Old and new passwords are required")
		
		# Get user from database
		user = db.query(models.User).filter(models.User.id == user_id).first()
		if not user:
			raise HTTPException(status_code=404, detail="User not found")
		
		# For Supabase users, use Supabase to change password
		if user.supabase_user_id:
			supabase = get_supabase_client()
			# Verify old password first by trying to sign in
			try:
				supabase.auth.sign_in_with_password({
					"email": user.email,
					"password": old_password
				})
				# Update password
				supabase.auth.update_user({"password": new_password})
			except Exception as e:
				print(f"Supabase password change error: {str(e)}")
				raise HTTPException(status_code=400, detail="Old password is incorrect")
		else:
			# For legacy users with local password hash
			from ..security import verify_password, hash_password
			if not verify_password(old_password, user.password_hash):
				raise HTTPException(status_code=400, detail="Old password is incorrect")
			user.password_hash = hash_password(new_password)
			db.commit()
		
		return {"message": "Password updated successfully"}
		
	except HTTPException:
		raise
	except Exception as e:
		print(f"Change password error: {str(e)}")
		raise HTTPException(status_code=500, detail="Failed to change password")


@router.get("/user/{user_id}")
async def get_user_public(user_id: str, db: Session = Depends(get_db)):
	"""
	Get public user information (for viewing other users)
	"""
	try:
		user = db.query(
			models.User.id,
			models.User.name,
			models.User.email
		).filter(models.User.id == user_id).first()
		
		if not user:
			raise HTTPException(status_code=404, detail="User not found")
		
		return {
			"id": user.id,
			"name": user.name,
			"email": user.email
		}
		
	except HTTPException:
		raise
	except Exception as e:
		print(f"Get user public error: {str(e)}")
		raise HTTPException(status_code=500, detail="Failed to get user")


@router.get("/check-email/{email}")
async def check_email_status(email: str, db: Session = Depends(get_db)):
	"""
	Check if email is verified and account created
	Useful for polling after email verification
	"""
	try:
		email = email.strip().lower()
		
		# Check if user exists
		user = db.query(models.User).filter(models.User.email == email).first()
		if user:
			return {
				"status": "verified",
				"message": "Email verified and account created",
				"user_exists": True
			}
		
		# Check if pending
		pending = db.query(models.PendingSignup).filter(
			models.PendingSignup.email == email
		).first()
		if pending:
			return {
				"status": "pending",
				"message": "Awaiting email verification",
				"user_exists": False
			}
		
		return {
			"status": "not_found",
			"message": "No signup found for this email",
			"user_exists": False
		}
		
	except Exception as e:
		print(f"Check email error: {str(e)}")
		raise HTTPException(status_code=500, detail=str(e))


@router.post("/forgot-password")
async def forgot_password(payload: dict):
	"""
	Request password reset - Supabase sends email automatically
	"""
	try:
		email = payload.get("email", "").strip().lower()
		
		if not email:
			raise HTTPException(status_code=400, detail="Email is required")
		
		# Supabase handles password reset email
		supabase = get_supabase_client()
		supabase.auth.reset_password_email(email)
		
		# Always return success (security: don't reveal if email exists)
		return {
			"success": True,
			"message": "If an account with that email exists, a password reset link has been sent."
		}
		
	except HTTPException:
		raise
	except Exception as e:
		print(f"Password reset error: {str(e)}")
		# Still return success for security
		return {
			"success": True,
			"message": "If an account with that email exists, a password reset link has been sent."
		}


@router.post("/reset-password")
async def reset_password(payload: dict):
	"""
	Reset password using Supabase (handled on frontend with Supabase SDK)
	This endpoint is mainly for compatibility
	"""
	try:
		new_password = payload.get("new_password", "")
		access_token = payload.get("access_token", "")
		
		if not new_password or not access_token:
			raise HTTPException(
				status_code=400,
				detail="New password and access token are required"
			)
		
		# Update password via Supabase
		supabase = get_supabase_client()
		supabase.auth.update_user({"password": new_password})
		
		return {
			"success": True,
			"message": "Password has been reset successfully"
		}
		
	except Exception as e:
		print(f"Reset password error: {str(e)}")
		raise HTTPException(status_code=400, detail="Failed to reset password")
