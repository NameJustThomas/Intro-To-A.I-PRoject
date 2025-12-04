from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.base import get_db
from app.models.orm_models import Camera
from pydantic import BaseModel


class CameraResponse(BaseModel):
    id: int
    store_id: int
    name: str
    location: str
    rtsp_url: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


router = APIRouter()


@router.get("/cameras", response_model=List[CameraResponse])
def list_cameras(
    store_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List all cameras, optionally filtered by store_id."""
    query = db.query(Camera)
    
    if store_id:
        query = query.filter(Camera.store_id == store_id)
    
    cameras = query.all()
    return cameras


@router.get("/cameras/{camera_id}", response_model=CameraResponse)
def get_camera(camera_id: int, db: Session = Depends(get_db)):
    """Get camera by ID."""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera

