from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.base import get_db
from app.schemas.attendance import CheckInResponse
from app.models.orm_models import Employee, AttendanceLog, Camera, FaceEmbedding
from app.ai.face_recog import detect_faces, get_embedding
import numpy as np

router = APIRouter()


@router.post("/attendance/check-in", response_model=CheckInResponse)
async def check_in(
    camera_id: str,
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Check in image/frame.
    Accepts image, runs face detection + matching (stub algorithm), stores attendance_log.
    """
    # Verify camera exists
    camera = db.query(Camera).filter(Camera.id == int(camera_id)).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    # Read image
    image_bytes = await image.read()
    
    # Stub: Detect faces
    faces = detect_faces(image_bytes)
    
    if not faces:
        raise HTTPException(status_code=404, detail="No face detected in image")

    # Stub: Get embedding from first detected face
    face_embedding = get_embedding(faces[0])
    
    # Stub: Match against stored embeddings
    # In production, this would use proper similarity matching
    best_match = None
    best_confidence = 0.0
    
    all_embeddings = db.query(FaceEmbedding).all()
    for stored_embedding in all_embeddings:
        # Stub similarity calculation (cosine similarity)
        stored_vec = np.array(stored_embedding.embedding)
        similarity = np.dot(face_embedding, stored_vec) / (
            np.linalg.norm(face_embedding) * np.linalg.norm(stored_vec)
        )
        
        if similarity > best_confidence and similarity > 0.7:  # Threshold
            best_confidence = similarity
            best_match = stored_embedding

    if not best_match:
        raise HTTPException(status_code=404, detail="Employee not recognized")

    employee = db.query(Employee).filter(Employee.id == best_match.employee_id).first()
    
    # Store attendance log
    attendance_log = AttendanceLog(
        employee_id=employee.id,
        camera_id=camera.id,
        confidence=float(best_confidence),
        snapshot_url=None  # In production, save snapshot and store URL
    )
    db.add(attendance_log)
    db.commit()

    return CheckInResponse(
        employee_id=employee.emp_code,
        employee_name=employee.name,
        timestamp=datetime.utcnow(),
        confidence=float(best_confidence),
        camera_id=camera_id
    )

