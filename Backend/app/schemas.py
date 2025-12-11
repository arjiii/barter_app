from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Category(BaseModel):
	id: str
	name: str
	description: Optional[str] = None
	icon: Optional[str] = None
	created_at: Optional[datetime] = None

	class Config:
		from_attributes = True


class ItemBase(BaseModel):
	title: str
	description: Optional[str] = None
	category: Optional[str] = None
	condition: Optional[str] = None
	images: Optional[list] = None
	specs: Optional[dict] = None
	location: Optional[str] = None
	latitude: Optional[float] = None
	longitude: Optional[float] = None
	status: Optional[str] = "available"

class ItemCreate(ItemBase):
	pass

class ItemUpdate(BaseModel):
	title: Optional[str] = None
	description: Optional[str] = None
	category: Optional[str] = None
	condition: Optional[str] = None
	images: Optional[list] = None
	specs: Optional[dict] = None
	location: Optional[str] = None
	latitude: Optional[float] = None
	longitude: Optional[float] = None
	status: Optional[str] = None

class Item(ItemBase):
	id: str
	user_id: str
	views: int = 0
	created_at: Optional[datetime] = None
	updated_at: Optional[datetime] = None
	owner_name: Optional[str] = None
	owner_id: Optional[str] = None

	class Config:
		from_attributes = True


class TradeBase(BaseModel):
	from_item_id: str
	to_item_id: str
	message: Optional[str] = None
	meeting_location: Optional[str] = None
	meeting_time: Optional[datetime] = None

class TradeCreate(TradeBase):
	to_user_id: str

class TradeUpdate(BaseModel):
	message: Optional[str] = None
	status: Optional[str] = None
	meeting_location: Optional[str] = None
	meeting_time: Optional[datetime] = None

class Trade(TradeBase):
	id: str
	from_user_id: str
	to_user_id: str
	status: str
	expires_at: Optional[datetime] = None
	created_at: Optional[datetime] = None
	updated_at: Optional[datetime] = None

	class Config:
		from_attributes = True


class MessageBase(BaseModel):
	trade_id: str
	content: str

class MessageCreate(MessageBase):
	receiver_id: str

class Message(MessageBase):
	id: str
	sender_id: str
	receiver_id: str
	is_read: bool = False
	created_at: Optional[datetime] = None

	class Config:
		from_attributes = True


class Rating(BaseModel):
    id: str
    trade_id: str
    rater_user_id: str
    ratee_user_id: str
    score: int
    feedback: Optional[str] = None
    created_at: Optional[datetime] = None
    transaction_hash: Optional[str] = None

    class Config:
        from_attributes = True



class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "user"

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    is_verified: Optional[bool] = None

class User(UserBase):
    id: str
    role: str
    is_verified: bool
    location: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SupportRequestBase(BaseModel):
    type: str
    subject: str
    message: str

class SupportRequestCreate(SupportRequestBase):
    pass

class SupportRequest(SupportRequestBase):
    id: str
    user_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    user: Optional[User] = None

    class Config:
        from_attributes = True
