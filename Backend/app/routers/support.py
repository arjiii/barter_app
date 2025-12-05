from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
from ..database import get_db
from .. import models, schemas
from ..security import decode_token

router = APIRouter(prefix="/support", tags=["support"])

def get_current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/requests", response_model=schemas.SupportRequest)
def create_support_request(request: schemas.SupportRequestCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_request = models.SupportRequest(
        id=str(uuid4()),
        user_id=current_user.id,
        type=request.type,
        subject=request.subject,
        message=request.message,
        status="pending"
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

@router.get("/requests", response_model=list[schemas.SupportRequest])
def get_user_requests(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.SupportRequest).filter(models.SupportRequest.user_id == current_user.id).order_by(models.SupportRequest.created_at.desc()).all()
