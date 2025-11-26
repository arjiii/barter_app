from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func
from uuid import uuid4
from datetime import datetime
from ..database import get_db
from .. import models, schemas
from ..websocket_manager import trade_ws_manager


router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/", response_model=list[schemas.Message])
def list_messages(trade_id: str = Query(...), db: Session = Depends(get_db)):
	return (
        db.query(models.Message)
        .where(models.Message.trade_id == trade_id)
        .order_by(models.Message.created_at.asc())
        .all()
    )


@router.get("/conversations")
def list_conversations(user_id: str = Query(...), db: Session = Depends(get_db)):
	# Find trades where user participates
	trades = (
        db.query(models.Trade)
        .filter(or_(models.Trade.from_user_id == user_id, models.Trade.to_user_id == user_id))
        .order_by(desc(models.Trade.updated_at))
        .all()
    )

	# Preload referenced items to avoid N+1 queries
	item_ids = {t.from_item_id for t in trades if t.from_item_id} | {t.to_item_id for t in trades if t.to_item_id}
	item_map = {}
	if item_ids:
		for item in db.query(models.Item.id, models.Item.title).filter(models.Item.id.in_(item_ids)).all():
			item_map[item.id] = item.title

	convs = []
	for t in trades:
		other_id = t.to_user_id if t.from_user_id == user_id else t.from_user_id
		other = (
            db.query(models.User.id, models.User.name)
            .filter(models.User.id == other_id)
            .first()
        )
		if not other:
			continue

		# last message
		last_msg = (
            db.query(models.Message)
            .filter(models.Message.trade_id == t.id)
            .order_by(desc(models.Message.created_at))
            .first()
        )

		# unread messages for current user
		unread_count = (
            db.query(models.Message)
            .filter(
                models.Message.trade_id == t.id,
                models.Message.receiver_id == user_id,
                models.Message.is_read == False,  # noqa: E712
            )
            .count()
        )

		trade_item_title = None
		if user_id == t.from_user_id:
			trade_item_title = item_map.get(t.from_item_id) or item_map.get(t.to_item_id)
		else:
			trade_item_title = item_map.get(t.to_item_id) or item_map.get(t.from_item_id)

		last_msg_time = ''
		if last_msg:
			if last_msg.created_at:
				last_msg_time = last_msg.created_at.isoformat()
			else:
				# Fallback to trade timestamps so list ordering still works
				last_msg_time = t.updated_at.isoformat() if t.updated_at else ''

		convs.append({
			"tradeId": t.id,
			"otherUser": {"id": other.id, "name": other.name},
			"tradeItemTitle": trade_item_title or '',
			"lastMessage": last_msg.content if last_msg else '',
			"lastMessageTime": last_msg_time,
			"unreadCount": unread_count,
		})
	return convs


@router.post("/", response_model=schemas.Message)
def create_message(payload: dict, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
	obj = models.Message(
		id=str(uuid4()),
		trade_id=payload["trade_id"],
		sender_id=payload["sender_id"],
		receiver_id=payload["receiver_id"],
		content=payload["content"],
		is_read=payload.get("is_read", False),
		created_at=datetime.utcnow(),
	)
	db.add(obj)
	# Update trade updated_at to surface conversation
	trade = db.query(models.Trade).filter(models.Trade.id == payload["trade_id"]).first()
	if trade:
		trade.updated_at = func.now()
	db.commit()
	db.refresh(obj)

	payload = {
		"type": "message",
		"message": {
			"id": obj.id,
			"tradeId": obj.trade_id,
			"senderId": obj.sender_id,
			"receiverId": obj.receiver_id,
			"content": obj.content,
			"isRead": obj.is_read,
			"createdAt": obj.created_at.isoformat() if obj.created_at else datetime.utcnow().isoformat()
		}
	}
	background_tasks.add_task(trade_ws_manager.broadcast_message, obj.trade_id, payload)
	return obj



