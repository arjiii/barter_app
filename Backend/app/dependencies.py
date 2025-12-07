from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from .database import get_db
from . import models
from .security import decode_token

def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Dependency to get the current authenticated user from the Bearer token.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.split(" ", 1)[1]
    user_id = decode_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user
