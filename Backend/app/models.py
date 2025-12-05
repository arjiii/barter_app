from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum, ForeignKey, Text, JSON, Float
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
	__tablename__ = "users"

	id = Column(String(36), primary_key=True)
	name = Column(String(255), nullable=False)
	email = Column(String(255), unique=True, nullable=False)
	password_hash = Column(String(255), nullable=False)
	is_verified = Column(Boolean, default=False)
	role = Column(Enum('user', 'admin', 'moderator', name='user_roles'), default='user')
	status = Column(String(20), default='active')  # 'active', 'suspended', 'banned'
	location = Column(String(255))  # City/Province location
	created_at = Column(DateTime, server_default=func.now())
	last_login_at = Column(DateTime)
	email_verification_token = Column(String(255), nullable=True)
	password_reset_token = Column(String(255), nullable=True)
	password_reset_expires = Column(DateTime, nullable=True)
	otp_code = Column(String(6), nullable=True)
	otp_expires_at = Column(DateTime, nullable=True)
	latitude = Column(Float, nullable=True)
	longitude = Column(Float, nullable=True)
	supabase_user_id = Column(String(255), nullable=True)  # Supabase Auth ID


class PendingSignup(Base):
	"""Temporary storage for signups pending email verification"""
	__tablename__ = "pending_signups"
	
	id = Column(String(36), primary_key=True)
	name = Column(String(255), nullable=False)
	email = Column(String(255), unique=True, nullable=False)
	password_hash = Column(String(255), nullable=False)
	location = Column(String(255), nullable=True)
	latitude = Column(Float, nullable=True)
	longitude = Column(Float, nullable=True)
	verification_method = Column(String(20), default='email')  # 'email' or 'admin'
	otp_code = Column(String(6), nullable=True)
	otp_expires_at = Column(DateTime, nullable=True)
	created_at = Column(DateTime, server_default=func.now())
	supabase_user_id = Column(String(255), nullable=True)  # Supabase Auth ID (optional)
	expires_at = Column(DateTime, nullable=True)  # Optional expiration time





class Category(Base):
	__tablename__ = "categories"

	id = Column(String(36), primary_key=True)
	name = Column(String(100), unique=True, nullable=False)
	description = Column(String(255))
	icon = Column(String(64))
	created_at = Column(DateTime, server_default=func.now())


class Item(Base):
	__tablename__ = "items"

	id = Column(String(36), primary_key=True)
	user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
	title = Column(String(255), nullable=False)
	description = Column(Text)
	category = Column(String(100))
	condition = Column(String(100))
	images = Column(JSON)
	specs = Column(JSON)  # Product specifications
	location = Column(String(255))  # City/Province location for the item
	latitude = Column(Float, nullable=True)
	longitude = Column(Float, nullable=True)
	status = Column(Enum('available', 'traded', 'removed', 'draft', 'pending', name='item_status'), default='available')
	views = Column(Integer, default=0)
	created_at = Column(DateTime, server_default=func.now())
	updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

	owner = relationship("User", backref="items")


class Trade(Base):
	__tablename__ = "trades"

	id = Column(String(36), primary_key=True)
	from_user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
	to_user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
	from_item_id = Column(String(36), ForeignKey('items.id', ondelete='CASCADE'), nullable=False)
	to_item_id = Column(String(36), ForeignKey('items.id', ondelete='CASCADE'), nullable=False)
	message = Column(Text)
	status = Column(Enum('pending', 'accepted', 'rejected', 'active', 'completed', 'cancelled', name='trade_status'), default='pending')
	expires_at = Column(DateTime)
	meeting_location = Column(String(255))
	meeting_time = Column(DateTime)
	created_at = Column(DateTime, server_default=func.now())
	updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

	initiator = relationship("User", foreign_keys=[from_user_id], backref="initiated_trades")
	receiver = relationship("User", foreign_keys=[to_user_id], backref="received_trades")
	from_item = relationship("Item", foreign_keys=[from_item_id])
	to_item = relationship("Item", foreign_keys=[to_item_id])


class Message(Base):
	__tablename__ = "messages"

	id = Column(String(36), primary_key=True)
	trade_id = Column(String(36), ForeignKey('trades.id', ondelete='CASCADE'), nullable=False)
	sender_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
	receiver_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
	content = Column(Text, nullable=False)
	is_read = Column(Boolean, default=False)
	created_at = Column(DateTime, server_default=func.now())



class Rating(Base):
    __tablename__ = "user_ratings"

    id = Column(String(36), primary_key=True)
    trade_id = Column(String(36), ForeignKey('trades.id', ondelete='CASCADE'), nullable=False)
    from_user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)  # rater
    to_user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)  # ratee
    rating = Column(Integer, nullable=False)  # score (1-5)
    comment = Column(Text)  # feedback
    created_at = Column(DateTime, server_default=func.now())



class SupportRequest(Base):
    __tablename__ = "support_requests"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"))
    type = Column(String(50))  # 'password_reset', 'account_issue', 'other'
    subject = Column(String(255))
    message = Column(Text)
    status = Column(String(20), default="pending")  # 'pending', 'resolved', 'rejected'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="support_requests")


class UserReport(Base):
    """User reports for reporting other users"""
    __tablename__ = "user_reports"

    id = Column(String(36), primary_key=True)
    reporter_id = Column(String(36), ForeignKey("users.id"))  # User who is reporting
    reported_user_id = Column(String(36), ForeignKey("users.id"))  # User being reported
    reason = Column(String(50))  # 'spam', 'inappropriate', 'scam', 'harassment', 'other'
    description = Column(Text)
    status = Column(String(20), default="pending")  # 'pending', 'reviewed', 'resolved'
    created_at = Column(DateTime, default=datetime.utcnow)

    reporter = relationship("User", foreign_keys=[reporter_id])
    reported_user = relationship("User", foreign_keys=[reported_user_id])


User.support_requests = relationship("SupportRequest", back_populates="user")

