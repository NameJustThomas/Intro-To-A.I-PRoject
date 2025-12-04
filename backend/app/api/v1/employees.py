from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.base import get_db
from app.schemas.employee import FaceRegistrationResponse
from app.models.orm_models import Employee, FaceEmbedding
from app.ai.face_recog import get_embedding, detect_faces
import numpy as np

router = APIRouter()


@router.post("/employee/register-face", response_model=FaceRegistrationResponse)
async def register_face(
    employee_id: str,
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Register employee face with multiple images.
    Accepts multiple images, stores employee and embeddings (stub vector) in DB.
    """
    # Check if employee exists
    employee = db.query(Employee).filter(Employee.emp_code == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    embeddings_count = 0

    for image in images:
        # Read image
        image_bytes = await image.read()
        
        # Stub: Detect faces and get embeddings
        # In production, this would use actual face recognition models
        faces = detect_faces(image_bytes)
        
        for face_img in faces:
            # Get embedding (stub - returns dummy vector)
            embedding = get_embedding(face_img)
            
            # Store embedding in database
            face_embedding = FaceEmbedding(
                employee_id=employee.id,
                embedding=embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
            )
            db.add(face_embedding)
            embeddings_count += 1

    db.commit()

    return FaceRegistrationResponse(
        message="Face registered successfully",
        employee_id=employee_id,
        embeddings_count=embeddings_count
    )

