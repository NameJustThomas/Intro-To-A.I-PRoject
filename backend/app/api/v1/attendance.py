from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.db.base import get_db
from app.schemas.attendance import CheckInResponse, CheckInHistoryItem
from app.models.orm_models import Employee, AttendanceLog, Camera, FaceEmbedding, Store, Schedule
from app.ai.face_recog import get_face_embedding_from_image
import numpy as np
import math

router = APIRouter()

# Similarity threshold for face matching (cosine similarity)
SIMILARITY_THRESHOLD = 0.6  # Adjust based on your needs (0.6-0.7 is typical)
# Minimum distance from store to validate location (in meters)
MIN_DISTANCE_FROM_STORE = 30.0  # 10 meters


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two GPS coordinates using Haversine formula.
    Returns distance in meters.
    """
    if not all([lat1, lon1, lat2, lon2]):
        return None
    
    # Earth radius in meters
    R = 6371000
    
    # Convert to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


@router.post("/attendance/check-in", response_model=CheckInResponse)
async def check_in(
    camera_id: str = Form(...),
    image: UploadFile = File(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Check in using face recognition.
    Uses YOLO-face for detection and InsightFace for embedding extraction.
    Matches against stored employee embeddings using cosine similarity.
    """
    # Verify camera exists
    camera = db.query(Camera).filter(Camera.id == int(camera_id)).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    # Read image
    image_bytes = await image.read()
    
    # Detect faces and get embeddings using real AI models
    face_boxes, embeddings = get_face_embedding_from_image(image_bytes)
    
    if not face_boxes or not embeddings:
        raise HTTPException(status_code=404, detail="No face detected in image")

    # Use the first detected face for matching
    face_embedding = embeddings[0]
    
    # Validate embedding
    if len(face_embedding) == 0 or np.all(face_embedding == 0):
        raise HTTPException(status_code=400, detail="Invalid face embedding extracted")
    
    # Match against stored embeddings using cosine similarity
    best_match = None
    best_confidence = 0.0
    
    all_embeddings = db.query(FaceEmbedding).all()
    for stored_embedding in all_embeddings:
        stored_vec = np.array(stored_embedding.embedding)
        
        # Skip invalid embeddings
        if len(stored_vec) == 0 or np.all(stored_vec == 0):
            continue
        
        # Calculate cosine similarity
        # Normalize vectors first
        face_norm = face_embedding / (np.linalg.norm(face_embedding) + 1e-8)
        stored_norm = stored_vec / (np.linalg.norm(stored_vec) + 1e-8)
        
        similarity = np.dot(face_norm, stored_norm)
        
        if similarity > best_confidence and similarity >= SIMILARITY_THRESHOLD:
            best_confidence = float(similarity)
            best_match = stored_embedding

    if not best_match:
        raise HTTPException(
            status_code=404, 
            detail=f"Employee not recognized. Best match confidence: {best_confidence:.3f} (threshold: {SIMILARITY_THRESHOLD})"
        )

    employee = db.query(Employee).filter(Employee.id == best_match.employee_id).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee associated with embedding not found")
    
    # Validate location if provided
    location_validated = 0  # 0 = not validated, 1 = valid, 2 = invalid
    distance_from_store = None
    
    if latitude and longitude:
        # Get store location from camera
        store = db.query(Store).filter(Store.id == camera.store_id).first()
        
        if store and store.latitude and store.longitude:
            # Calculate distance from store
            distance_from_store = calculate_distance(
                latitude, longitude,
                store.latitude, store.longitude
            )
            
            if distance_from_store is not None:
                # Validate if within 10 meters
                if distance_from_store <= MIN_DISTANCE_FROM_STORE:
                    location_validated = 1  # Valid
                else:
                    location_validated = 2  # Invalid (too far)
        else:
            # Store location not set, can't validate
            location_validated = 0
    
    # Store attendance log
    check_in_time = datetime.utcnow()
    
    # Validate check-in time (only for employees, not admin/manager)
    is_on_time = 1  # Default: on time
    if employee.role and employee.role.lower() not in ['admin', 'manager']:
        # Check if employee has a schedule for today
        check_in_date = check_in_time.date()
        schedule = db.query(Schedule).filter(
            Schedule.employee_id == employee.id,
            Schedule.date == check_in_date
        ).first()
        
        if schedule and schedule.shift_start:
            # Compare check-in time with shift start
            # Allow 15 minutes grace period
            from datetime import timedelta
            shift_start = schedule.shift_start
            grace_period = timedelta(minutes=15)
            late_threshold = shift_start + grace_period
            
            if check_in_time > late_threshold:
                is_on_time = 0  # Late
            else:
                is_on_time = 1  # On time
        # If no schedule, assume on time (flexible schedule)
    attendance_log = AttendanceLog(
        employee_id=employee.id,
        camera_id=camera.id,
        confidence=best_confidence,
        snapshot_url=None,  # In production, save snapshot and store URL
        latitude=latitude,
        longitude=longitude,
        location_validated=location_validated,
        distance_from_store=distance_from_store,
        is_on_time=is_on_time,
        timestamp=check_in_time
    )
    db.add(attendance_log)
    db.commit()

    return CheckInResponse(
        employee_id=employee.emp_code,
        employee_name=employee.name,
        timestamp=check_in_time,
        confidence=best_confidence,
        camera_id=camera_id,
        latitude=latitude,
        longitude=longitude,
        location_validated=location_validated == 1,
        distance_from_store=distance_from_store
    )


@router.get("/attendance/history", response_model=list[CheckInHistoryItem])
def get_check_in_history(
    employee_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get check-in history with employee details.
    """
    query = db.query(AttendanceLog).join(Employee).join(Camera).join(Store)
    
    if employee_id:
        query = query.filter(Employee.emp_code == employee_id)
    
    logs = query.order_by(AttendanceLog.timestamp.desc()).limit(limit).all()
    
    result = []
    for log in logs:
        result.append(CheckInHistoryItem(
            id=log.id,
            employee_id=log.employee.emp_code,
            employee_name=log.employee.name,
            employee_role=log.employee.role,
            timestamp=log.timestamp,
            camera_id=log.camera_id,
            camera_name=log.camera.name if log.camera else None,
            store_name=log.camera.store.name if log.camera and log.camera.store else None,
            confidence=log.confidence,
            latitude=log.latitude,
            longitude=log.longitude,
            location_validated=log.location_validated,
            distance_from_store=log.distance_from_store,
            is_on_time=log.is_on_time
        ))
    
    return result

