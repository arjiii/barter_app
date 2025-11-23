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


class Item(BaseModel):
	id: str
	user_id: str
	title: str
	description: Optional[str] = None
	category: Optional[str] = None
	condition: Optional[str] = None
	images: Optional[list] = None
	location: Optional[str] = None
	status: str
	views: int = 0
	created_at: Optional[datetime] = None
	updated_at: Optional[datetime] = None

	class Config:
		from_attributes = True


class Trade(BaseModel):
	id: str
	from_user_id: str
	to_user_id: str
	from_item_id: str
	to_item_id: str
	message: Optional[str] = None
	status: str
	expires_at: Optional[datetime] = None
	meeting_location: Optional[str] = None
	meeting_time: Optional[datetime] = None
	created_at: Optional[datetime] = None
	updated_at: Optional[datetime] = None

	class Config:
		from_attributes = True


class Message(BaseModel):
	id: str
	trade_id: str
	sender_id: str
	receiver_id: str
	content: str
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

    class Config:
        from_attributes = True


