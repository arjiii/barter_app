from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
from .. import models
from ..database import get_db
from ..security import decode_token

router = APIRouter(prefix="/reports", tags=["reports"])


def get_current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization.split(" ", 1)[1]
    user_id = decode_token(token)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user



class ReportUserRequest(BaseModel):
    reported_user_id: str
    reason: str  # 'spam', 'inappropriate', 'scam', 'harassment', 'other'
    description: str


@router.post("/user")
def report_user(
    report: ReportUserRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Report another user"""
    # Check if reported user exists
    reported_user = db.query(models.User).filter(models.User.id == report.reported_user_id).first()
    if not reported_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent self-reporting
    if current_user.id == report.reported_user_id:
        raise HTTPException(status_code=400, detail="You cannot report yourself")
    
    # Create report
    user_report = models.UserReport(
        id=str(uuid.uuid4()),
        reporter_id=current_user.id,
        reported_user_id=report.reported_user_id,
        reason=report.reason,
        description=report.description,
        status="pending"
    )
    
    db.add(user_report)
    db.commit()
    
    return {"message": "User reported successfully", "report_id": user_report.id}


@router.get("/my-reports")
def get_my_reports(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get reports made by current user"""
    reports = db.query(models.UserReport).filter(
        models.UserReport.reporter_id == current_user.id
    ).all()
    
    return [
        {
            "id": report.id,
            "reported_user_id": report.reported_user_id,
            "reason": report.reason,
            "description": report.description,
            "status": report.status,
            "created_at": report.created_at.isoformat() if report.created_at else None
        }
        for report in reports
    ]
