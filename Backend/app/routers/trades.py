from fastapi import APIRouter, Depends, Query, HTTPException, status
# Trigger reload
from sqlalchemy.orm import Session
from uuid import uuid4
from ..database import get_db
from .. import models, schemas
from ..dependencies import get_current_user
from datetime import datetime, timezone
from sqlalchemy import or_

router = APIRouter(prefix="/trades", tags=["trades"])


@router.get("/", response_model=list[schemas.Trade])
def list_trades(
    user_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    List trades. 
    If user_id is provided, filter by that user.
    If not provided, only admin can see all trades (or restrict to current user).
    For now, we'll restrict to current user if they are not admin.
    """
    q = db.query(models.Trade)
    
    # Security: If not admin, force filter by current user
    if current_user.role != 'admin':
        # Users can only see their own trades
        q = q.filter(
            or_(
                models.Trade.from_user_id == current_user.id,
                models.Trade.to_user_id == current_user.id
            )
        )
    elif user_id:
        # Admin can filter by specific user
        q = q.filter(
            or_(
                models.Trade.from_user_id == user_id,
                models.Trade.to_user_id == user_id
            )
        )
        
    trades = q.order_by(models.Trade.created_at.desc()).all()
    for t in trades:
        if t.created_at and t.created_at.tzinfo is None:
            t.created_at = t.created_at.replace(tzinfo=timezone.utc)
        if t.updated_at and t.updated_at.tzinfo is None:
            t.updated_at = t.updated_at.replace(tzinfo=timezone.utc)
    return trades


@router.post("/", response_model=schemas.Trade)
def create_trade(
    payload: schemas.TradeCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Validate items exist
    from_item = db.query(models.Item).filter(models.Item.id == payload.from_item_id).first()
    to_item = db.query(models.Item).filter(models.Item.id == payload.to_item_id).first()
    
    if not from_item or not to_item:
        raise HTTPException(status_code=404, detail="One or more items not found")
        
    # Validate ownership
    if from_item.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="You do not own the item you are offering")
    
    if to_item.user_id != payload.to_user_id:
        raise HTTPException(status_code=400, detail="Target user does not own the requested item")

    obj = models.Trade(
        id=str(uuid4()),
        from_user_id=current_user.id,
        to_user_id=payload.to_user_id,
        from_item_id=payload.from_item_id,
        to_item_id=payload.to_item_id,
        message=payload.message,
        meeting_location=payload.meeting_location,
        meeting_time=payload.meeting_time,
        status="pending",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{trade_id}", response_model=schemas.Trade)
def get_trade(
    trade_id: str, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
        
    # Authorization: Only participants or admin can view
    if current_user.role != 'admin':
        if trade.from_user_id != current_user.id and trade.to_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this trade")
            

    
    if trade.created_at and trade.created_at.tzinfo is None:
        trade.created_at = trade.created_at.replace(tzinfo=timezone.utc)
    if trade.updated_at and trade.updated_at.tzinfo is None:
        trade.updated_at = trade.updated_at.replace(tzinfo=timezone.utc)
            
    return trade


from ..services.blockchain import write_trade_to_blockchain, write_rating_to_blockchain
from ..database import SessionLocal

def record_trade_bg(trade_id: str, buyer_email: str, seller_email: str, item_title: str):
    try:
        tx_hash = write_trade_to_blockchain(trade_id, buyer_email, seller_email, item_title, 0)
        print(f"Trade recorded on blockchain. Hash: {tx_hash}")
        
        # Update DB with hash
        db = SessionLocal()
        try:
            trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()
            if trade:
                trade.blockchain_tx_hash = tx_hash
                db.commit()
        finally:
            db.close()
    except Exception as e:
        print(f"Error in background trade record: {e}")

def record_rating_bg(rating_id: str, user_email: str, rating_val: int, comment: str):
    try:
        tx_hash = write_rating_to_blockchain(user_email, rating_val, comment)
        print(f"Rating recorded on blockchain. Hash: {tx_hash}")
        
        # Update DB with hash
        db = SessionLocal()
        try:
            rating_obj = db.query(models.Rating).filter(models.Rating.id == rating_id).first()
            if rating_obj:
                rating_obj.blockchain_tx_hash = tx_hash
                db.commit()
        finally:
            db.close()
    except Exception as e:
        print(f"Error in background rating record: {e}")

# ... imports ...

from fastapi import BackgroundTasks

# ... imports ...

@router.patch("/{trade_id}", response_model=schemas.Trade)
def update_trade(
    trade_id: str, 
    payload: schemas.TradeUpdate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    # Authorization: Only participants or admin can update
    if current_user.role != 'admin':
        if trade.from_user_id != current_user.id and trade.to_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this trade")

    update_data = payload.model_dump(exclude_unset=True)
    
    # Special handling for status changes
    if "status" in update_data:
        new_status = update_data["status"]
        
        # Logic for status transitions
        if new_status == "accepted":
            trade.status = "active"
        elif new_status == "completed":
            trade.status = "completed"
            
            # --- Blockchain Integration: Record Trade ---
            try:
                # Fetch details
                from_user = db.query(models.User).filter(models.User.id == trade.from_user_id).first()
                to_user = db.query(models.User).filter(models.User.id == trade.to_user_id).first()
                from_item = db.query(models.Item).filter(models.Item.id == trade.from_item_id).first()
                to_item = db.query(models.Item).filter(models.Item.id == trade.to_item_id).first()
                
                item_title = f"{from_item.title} <-> {to_item.title}" if (from_item and to_item) else (from_item.title if from_item else "Unknown Item")
                
                if from_user and to_user:
                    background_tasks.add_task(
                        record_trade_bg,
                        trade_id=trade.id,
                        buyer_email=to_user.email,
                        seller_email=from_user.email,
                        item_title=item_title
                    )
            except Exception as e:
                print(f"Failed to queue trade for blockchain: {e}")
            # ---------------------------------------------

        else:
            trade.status = new_status

        # Side effects for items
        if trade.status == "active":
            # Mark items as pending
            from sqlalchemy import update
            if trade.from_item_id:
                db.execute(update(models.Item).where(models.Item.id == trade.from_item_id).values(status="pending"))
            if trade.to_item_id:
                db.execute(update(models.Item).where(models.Item.id == trade.to_item_id).values(status="pending"))
 
        if trade.status == "completed":
            # Mark items as traded
            from sqlalchemy import update
            if trade.from_item_id:
                db.execute(update(models.Item).where(models.Item.id == trade.from_item_id).values(status="traded"))
            if trade.to_item_id:
                db.execute(update(models.Item).where(models.Item.id == trade.to_item_id).values(status="traded"))
                
        # Remove status from generic update loop to avoid double set if we modified it above
        if "status" in update_data:
            del update_data["status"]

    # Update other fields
    for field, value in update_data.items():
        setattr(trade, field, value)

    db.commit()
    db.refresh(trade)
    return trade


@router.delete("/{trade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trade(
    trade_id: str, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    # Authorization: Only participants or admin can delete
    if current_user.role != 'admin':
        if trade.from_user_id != current_user.id and trade.to_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this trade")

    db.delete(trade)
    db.commit()
    return None


@router.post("/{trade_id}/ratings", response_model=schemas.Rating)
def create_rating(
    trade_id: str, 
    payload: dict, # TODO: Create RatingCreate schema for strict 1-to-1
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
        
    # Verify user was part of the trade
    if current_user.id not in [trade.from_user_id, trade.to_user_id]:
        raise HTTPException(status_code=403, detail="You were not part of this trade")

    rating = models.Rating(
        id=str(uuid4()),
        trade_id=trade_id,
        from_user_id=current_user.id, # Force rater to be current user
        to_user_id=payload["ratee_user_id"],
        rating=int(payload["score"]),

        comment=payload.get("feedback"),
        created_at=datetime.now(timezone.utc),
    )
    db.add(rating)
    db.commit()
    db.refresh(rating)
    
    # --- Blockchain Integration: Record Rating ---
    try:
        ratee = db.query(models.User).filter(models.User.id == rating.to_user_id).first()
        if ratee:
            background_tasks.add_task(
                record_rating_bg,
                rating_id=rating.id,
                user_email=ratee.email,
                rating_val=rating.rating,
                comment=rating.comment or ""
            )
    except Exception as e:
        print(f"Failed to queue rating for blockchain: {e}")
    # ---------------------------------------------
    
    return {
        "id": rating.id,
        "trade_id": rating.trade_id,
        "rater_user_id": rating.from_user_id,
        "ratee_user_id": rating.to_user_id,
        "score": rating.rating,
        "feedback": rating.comment,
        "created_at": rating.created_at
    }


@router.get("/{trade_id}/ratings", response_model=list[schemas.Rating])
def list_ratings(trade_id: str, db: Session = Depends(get_db)):
    ratings = db.query(models.Rating).filter(models.Rating.trade_id == trade_id).all()
    return [
        {
            "id": r.id,
            "trade_id": r.trade_id,
            "rater_user_id": r.from_user_id,
            "ratee_user_id": r.to_user_id,
            "score": r.rating,
            "feedback": r.comment,
            "created_at": r.created_at
        }
        for r in ratings
    ]


@router.get("/ratings/user/{user_id}", response_model=list[schemas.Rating])
def get_user_ratings(user_id: str, db: Session = Depends(get_db)):
    """Get all ratings received by a user"""
    ratings = db.query(models.Rating).filter(models.Rating.to_user_id == user_id).order_by(models.Rating.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "trade_id": r.trade_id,
            "rater_user_id": r.from_user_id,
            "ratee_user_id": r.to_user_id,
            "score": r.rating,
            "feedback": r.comment,
            "created_at": r.created_at
        }
        for r in ratings
    ]
