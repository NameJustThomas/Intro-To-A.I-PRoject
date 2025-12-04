from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from app.db.base import get_db
from app.models.orm_models import EnvironmentLog, Camera
from pydantic import BaseModel


class EnvironmentLogResponse(BaseModel):
    id: int
    camera_id: int
    timestamp: datetime
    people_count: int
    brightness: float

    class Config:
        from_attributes = True


router = APIRouter()


@router.get("/environment/logs", response_model=List[EnvironmentLogResponse])
def get_environment_logs(
    camera_id: Optional[int] = Query(None, description="Filter by camera ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs to return"),
    db: Session = Depends(get_db)
):
    """Get environment logs, optionally filtered by camera_id."""
    query = db.query(EnvironmentLog)
    
    if camera_id:
        # Verify camera exists
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        query = query.filter(EnvironmentLog.camera_id == camera_id)
    
    logs = query.order_by(desc(EnvironmentLog.timestamp)).limit(limit).all()
    return logs


@router.post("/environment/logs")
def create_environment_log(
    camera_id: int,
    people_count: int,
    brightness: float,
    db: Session = Depends(get_db)
):
    """Create a new environment log entry."""
    # Verify camera exists
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    env_log = EnvironmentLog(
        camera_id=camera_id,
        people_count=people_count,
        brightness=brightness
    )
    db.add(env_log)
    db.commit()
    db.refresh(env_log)
    
    return EnvironmentLogResponse.model_validate(env_log)

