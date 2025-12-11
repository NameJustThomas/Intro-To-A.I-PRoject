from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from app.db.base import get_db
from app.models.orm_models import EnvironmentLog, Camera
from app.ai.people_count import count_people
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
async def create_environment_log(
    camera_id: int,
    image: Optional[UploadFile] = File(None, description="Image to count people from"),
    people_count: Optional[int] = Query(None, description="Manual people count (if image not provided)"),
    brightness: Optional[float] = Query(None, description="Manual brightness value"),
    db: Session = Depends(get_db)
):
    """
    Create a new environment log entry.
    If image is provided, automatically counts people and calculates brightness.
    Otherwise, uses provided people_count and brightness values.
    """
    # Verify camera exists
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # If image provided, use AI to count people and calculate brightness
    if image:
        try:
            image_bytes = await image.read()
            
            # Count people using AI
            detected_count = count_people(image_bytes)
            people_count = detected_count
            
            # Calculate brightness (simple average of grayscale)
            import cv2
            import numpy as np
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                brightness = float(np.mean(img)) / 255.0  # Normalize to 0-1
            else:
                brightness = 0.5  # Default if image decode fails
                
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")
    else:
        # Use provided values or defaults
        if people_count is None:
            people_count = 0
        if brightness is None:
            brightness = 0.5
    
    env_log = EnvironmentLog(
        camera_id=camera_id,
        people_count=people_count,
        brightness=brightness
    )
    db.add(env_log)
    db.commit()
    db.refresh(env_log)
    
    return EnvironmentLogResponse.model_validate(env_log)

