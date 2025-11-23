from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import uuid4
from ..database import get_db
from .. import models, schemas


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[schemas.Category])
def list_categories(db: Session = Depends(get_db)):
	return db.query(models.Category).order_by(models.Category.name).all()


@router.post("/", response_model=schemas.Category)
def create_category(payload: dict, db: Session = Depends(get_db)):
	obj = models.Category(
		id=str(uuid4()),
		name=payload.get("name"),
		description=payload.get("description"),
		icon=payload.get("icon"),
	)
	db.add(obj)
	db.commit()
	db.refresh(obj)
	return obj



