from fastapi import APIRouter, Depends, Query, HTTPException, status
import json
import math
from sqlalchemy.orm import Session
from uuid import uuid4
from ..database import get_db
from .. import models, schemas
from ..dependencies import get_current_user
from datetime import datetime, timezone


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
        "specs": item.specs,
        "location": getattr(item, "location", None),
        "latitude": getattr(item, "latitude", None),
        "longitude": getattr(item, "longitude", None),
        "status": item.status,
        "views": item.views,
        "created_at": item.created_at.replace(tzinfo=timezone.utc) if item.created_at and item.created_at.tzinfo is None else item.created_at,
        "updated_at": item.updated_at.replace(tzinfo=timezone.utc) if item.updated_at and item.updated_at.tzinfo is None else item.updated_at,
    }

    if owner_id:
        data["owner_id"] = owner_id
        data["owner_name"] = owner_name
        data["owner"] = {"id": owner_id, "name": owner_name}
    return data


@router.get("/", response_model=list[schemas.Item])
def list_items(
	user_id: str | None = Query(default=None),
	status: str | None = Query(default=None),
	category: str | None = Query(default=None),
	limit: int = Query(default=100, ge=1, le=500),
	offset: int = Query(default=0, ge=0),
	user_lat: float | None = Query(default=None),
	user_lon: float | None = Query(default=None),
	db: Session = Depends(get_db),
):
    def calculate_distance(lat1, lon1, lat2, lon2):
        if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
            return float('inf')
        try:
            R = 6371  # Earth radius in km
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c
        except Exception:
            return float('inf')
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

        # If user location is provided, fetch all (or more) items to sort by distance in Python
        # This is a trade-off for DB-agnostic distance sorting without PostGIS/MySQL extensions
        if user_lat is not None and user_lon is not None:
             # Fetch more items to allow for sorting, but still limit to avoid OOM
            rows = q.all()
            
            # Sort by distance
            rows.sort(key=lambda x: calculate_distance(user_lat, user_lon, x[0].latitude, x[0].longitude))
            
            # Apply pagination after sorting
            start = offset
            end = offset + limit
            rows = rows[start:end]
        else:
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
def create_item(
    payload: schemas.ItemCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        obj = models.Item(
            id=str(uuid4()),
            user_id=current_user.id, # Enforce current user as owner
            title=payload.title,
            description=payload.description,
            category=payload.category,
            condition=payload.condition,
            images=payload.images,
            specs=payload.specs,
            location=payload.location,
            latitude=payload.latitude,
            longitude=payload.longitude,
            status=payload.status or "available",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        
        # Return with owner info
        return _serialize_item(obj, current_user.name, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get("/{item_id}", response_model=schemas.Item)
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
def update_item(
    item_id: str, 
    payload: schemas.ItemUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    obj = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    # Authorization check
    if obj.user_id != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this item")

    update_data = payload.model_dump(exclude_unset=True)
    update_data['updated_at'] = datetime.now(timezone.utc)
    for field, value in update_data.items():
        setattr(obj, field, value)

    db.commit()
    db.refresh(obj)
    
    # Fetch owner info for response
    owner = db.query(models.User).filter(models.User.id == obj.user_id).first()
    return _serialize_item(obj, owner.name if owner else None, obj.user_id)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: str, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    obj = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        
    # Authorization check
    if obj.user_id != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this item")
        
    db.delete(obj)
    db.commit()
    return None

