from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/trades", tags=["trades"])


@router.get("/", response_model=list[schemas.Trade])
def list_trades(user_id: str | None = Query(default=None), db: Session = Depends(get_db)):
    q = db.query(models.Trade)
    if user_id:
        q = q.filter(
            (models.Trade.from_user_id == user_id)
            | (models.Trade.to_user_id == user_id)
        )
    return q.order_by(models.Trade.created_at.desc()).all()


@router.post("/", response_model=schemas.Trade)
def create_trade(payload: dict, db: Session = Depends(get_db)):
    obj = models.Trade(
        id=str(uuid4()),
        from_user_id=payload["from_user_id"],
        to_user_id=payload["to_user_id"],
        from_item_id=payload["from_item_id"],
        to_item_id=payload["to_item_id"],
        message=payload.get("message"),
        status=payload.get("status", "pending"),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{trade_id}", response_model=schemas.Trade)
def get_trade(trade_id: str, db: Session = Depends(get_db)):
    trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade


@router.patch("/{trade_id}", response_model=schemas.Trade)
def update_trade(trade_id: str, payload: dict, db: Session = Depends(get_db)):
    trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    # Update fields
    if "status" in payload:
        new_status = payload["status"]
        
        # If trade is accepted, automatically move to active status
        if new_status == "accepted":
            trade.status = "active"
        # If trade is marked as complete, ensure status is set to completed
        elif new_status == "completed":
            trade.status = "completed"
        else:
            trade.status = new_status

        # If trade accepted or active, mark items as pending
        if trade.status in ("active",):
            # Use SQL UPDATE to avoid loading full model with location column
            from sqlalchemy import update
            if trade.from_item_id:
                stmt = update(models.Item).where(models.Item.id == trade.from_item_id).values(status="pending")
                db.execute(stmt)
            if trade.to_item_id:
                stmt = update(models.Item).where(models.Item.id == trade.to_item_id).values(status="pending")
                db.execute(stmt)

        # If trade completed, mark items as traded
        if trade.status == "completed":
            # Use SQL UPDATE to avoid loading full model with location column
            from sqlalchemy import update
            if trade.from_item_id:
                stmt = update(models.Item).where(models.Item.id == trade.from_item_id).values(status="traded")
                db.execute(stmt)
            if trade.to_item_id:
                stmt = update(models.Item).where(models.Item.id == trade.to_item_id).values(status="traded")
                db.execute(stmt)

    if "message" in payload:
        trade.message = payload["message"]
    if "meeting_location" in payload:
        trade.meeting_location = payload["meeting_location"]
    if "meeting_time" in payload:
        trade.meeting_time = payload["meeting_time"]

    db.commit()
    db.refresh(trade)
    return trade


@router.post("/{trade_id}/ratings", response_model=schemas.Rating)
def create_rating(trade_id: str, payload: dict, db: Session = Depends(get_db)):
    trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    rating = models.Rating(
        id=str(uuid4()),
        trade_id=trade_id,
        from_user_id=payload["rater_user_id"],  # rater_user_id maps to from_user_id
        to_user_id=payload["ratee_user_id"],  # ratee_user_id maps to to_user_id
        rating=int(payload["score"]),  # score maps to rating
        comment=payload.get("feedback"),  # feedback maps to comment
    )
    db.add(rating)
    db.commit()
    db.refresh(rating)
    
    # Map database fields to schema fields for response
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
    # Map database fields to schema fields for response
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
    """Get all ratings received by a user (where to_user_id == user_id)"""
    ratings = db.query(models.Rating).filter(models.Rating.to_user_id == user_id).order_by(models.Rating.created_at.desc()).all()
    # Map database fields to schema fields for response
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


@router.delete("/{trade_id}")
def delete_trade(trade_id: str, db: Session = Depends(get_db)):
    trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    db.delete(trade)
    db.commit()
    return {"message": "Trade deleted successfully"}
