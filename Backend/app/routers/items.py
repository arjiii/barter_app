from fastapi import APIRouter, Depends, Query, HTTPException, status
import json
from sqlalchemy.orm import Session
from uuid import uuid4
from ..database import get_db
from .. import models, schemas


router = APIRouter(prefix="/items", tags=["items"])


def _serialize_item(item: models.Item, owner_name: str | None = None, owner_id: str | None = None) -> dict:
    """Normalize DB row into a consistent response shape."""
    images_value = item.images
    if isinstance(images_value, str):
        try:
            images_value = json.loads(images_value)
        except Exception:
            images_value = []
    if images_value is None:
        images_value = []

    data = {
        "id": item.id,
        "user_id": item.user_id,
        "title": item.title,
        "description": item.description,
        "category": item.category,
        "condition": item.condition,
        "images": images_value,
        "location": getattr(item, "location", None),
        "status": item.status,
        "views": item.views,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }

    if owner_id:
        data["owner_id"] = owner_id
        data["owner_name"] = owner_name
        data["owner"] = {"id": owner_id, "name": owner_name}
    return data


@router.get("/")
def list_items(
	user_id: str | None = Query(default=None),
	status: str | None = Query(default=None),
	category: str | None = Query(default=None),
	limit: int = Query(default=100, ge=1, le=500),
	offset: int = Query(default=0, ge=0),
	db: Session = Depends(get_db),
):
    try:
        q = db.query(
            models.Item,
            models.User.name.label("owner_name"),
            models.User.id.label("owner_id"),
        ).join(models.User, models.Item.user_id == models.User.id)

        if user_id:
            q = q.filter(models.Item.user_id == user_id)
        if status:
            q = q.filter(models.Item.status == status)
        if category and category != 'all':
            q = q.filter(models.Item.category == category)

        try:
            # Preferred: newest first
            rows = (
                q.order_by(models.Item.created_at.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )
        except Exception as inner:
            # MySQL "Out of sort memory" – retry without ORDER BY so at least items show
            if "Out of sort memory" in str(inner):
                rows = (
                    q.order_by(None)
                    .limit(limit)
                    .offset(offset)
                    .all()
                )
            else:
                raise

        return [_serialize_item(item, owner_name, owner_id) for item, owner_name, owner_id in rows]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to list items: {e}")


@router.post("/", response_model=schemas.Item)
def create_item(payload: dict, db: Session = Depends(get_db)):
	obj = models.Item(
		id=str(uuid4()),
		user_id=payload["user_id"],
		title=payload["title"],
		description=payload.get("description"),
		category=payload.get("category"),
		condition=payload.get("condition"),
		images=payload.get("images"),
		location=payload.get("location"),
		status=payload.get("status", "available"),
	)
	db.add(obj)
	db.commit()
	db.refresh(obj)
	return obj


@router.get("/{item_id}")
def get_item(item_id: str, db: Session = Depends(get_db)):
    row = (
        db.query(
            models.Item,
            models.User.name.label("owner_name"),
            models.User.id.label("owner_id"),
        )
        .join(models.User, models.Item.user_id == models.User.id)
        .filter(models.Item.id == item_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    item, owner_name, owner_id = row
    return _serialize_item(item, owner_name, owner_id)


@router.patch("/{item_id}", response_model=schemas.Item)
def update_item(item_id: str, payload: dict, db: Session = Depends(get_db)):
    obj = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    allowed_fields = {"title", "description", "category", "condition", "images", "status", "location"}
    for field in allowed_fields:
        if field in payload:
            setattr(obj, field, payload[field])

    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: str, db: Session = Depends(get_db)):
    obj = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    db.delete(obj)
    db.commit()
    return {"message": "Item deleted"}

