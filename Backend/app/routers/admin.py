from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..security import decode_token

router = APIRouter(prefix="/admin", tags=["admin"])

def get_current_admin_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return user

@router.get("/stats")
def get_stats(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    user_count = db.query(models.User).count()
    item_count = db.query(models.Item).count()
    trade_count = db.query(models.Trade).count()
    return {
        "users": user_count,
        "items": item_count,
        "trades": trade_count
    }

@router.get("/users")
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.delete("/users/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}

@router.get("/items")
def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    items = db.query(models.Item).offset(skip).limit(limit).all()
    return items

@router.delete("/items/{item_id}")
def delete_item(item_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"message": "Item deleted"}

@router.get("/trades")
def list_trades(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    trades = db.query(models.Trade).offset(skip).limit(limit).all()
    return trades
