from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, field_serializer
from app.db.base import get_db
from app.models.orm_models import Store

router = APIRouter()


class StoreResponse(BaseModel):
    id: int
    name: Optional[str]
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: Optional[str]

    class Config:
        from_attributes = True


class StoreUpdateRequest(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@router.get("/stores", response_model=List[StoreResponse])
def list_stores(
    db: Session = Depends(get_db)
):
    """List all stores."""
    stores = db.query(Store).all()
    result = []
    for store in stores:
        store_dict = {
            'id': store.id,
            'name': store.name,
            'address': store.address,
            'latitude': store.latitude,
            'longitude': store.longitude,
            'created_at': store.created_at.isoformat() if store.created_at else None
        }
        result.append(StoreResponse(**store_dict))
    return result


@router.get("/stores/{store_id}", response_model=StoreResponse)
def get_store(
    store_id: int,
    db: Session = Depends(get_db)
):
    """Get store by ID."""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    store_dict = {
        'id': store.id,
        'name': store.name,
        'address': store.address,
        'latitude': store.latitude,
        'longitude': store.longitude,
        'created_at': store.created_at.isoformat() if store.created_at else None
    }
    return StoreResponse(**store_dict)


@router.put("/stores/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: int,
    store_data: StoreUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update store information. Requires manager/admin role."""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    if store_data.name is not None:
        store.name = store_data.name
    if store_data.address is not None:
        store.address = store_data.address
    if store_data.latitude is not None:
        store.latitude = store_data.latitude
    if store_data.longitude is not None:
        store.longitude = store_data.longitude
    
    db.commit()
    db.refresh(store)
    
    store_dict = {
        'id': store.id,
        'name': store.name,
        'address': store.address,
        'latitude': store.latitude,
        'longitude': store.longitude,
        'created_at': store.created_at.isoformat() if store.created_at else None
    }
    return StoreResponse(**store_dict)

