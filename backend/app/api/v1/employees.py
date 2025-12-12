from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.db.base import get_db
from app.schemas.employee import FaceRegistrationResponse
from app.models.orm_models import Employee, FaceEmbedding
from app.ai.face_recog import get_face_embedding_from_image
import numpy as np

router = APIRouter()


class EmployeeCreateRequest(BaseModel):
    emp_code: str
    name: str
    role: Optional[str] = None


class EmployeeResponse(BaseModel):
    id: int
    emp_code: str
    name: str
    role: Optional[str] = None

    class Config:
        from_attributes = True


@router.post("/employee", response_model=EmployeeResponse)
def create_employee(
    employee: EmployeeCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new employee."""
    # Check if employee already exists
    existing = db.query(Employee).filter(Employee.emp_code == employee.emp_code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Employee with code {employee.emp_code} already exists")
    
    new_employee = Employee(
        emp_code=employee.emp_code,
        name=employee.name,
        role=employee.role
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    
    return EmployeeResponse.model_validate(new_employee)


@router.get("/employee", response_model=List[EmployeeResponse])
def list_employees(
    db: Session = Depends(get_db)
):
    """List all employees."""
    employees = db.query(Employee).all()
    return [EmployeeResponse.model_validate(emp) for emp in employees]


@router.get("/employee/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: str,
    db: Session = Depends(get_db)
):
    """Get employee by ID (emp_code)."""
    employee = db.query(Employee).filter(Employee.emp_code == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return EmployeeResponse.model_validate(employee)


@router.put("/employee/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: str,
    employee: EmployeeCreateRequest,
    db: Session = Depends(get_db)
):
    """Update employee information. Requires manager/admin role."""
    existing = db.query(Employee).filter(Employee.emp_code == employee_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check if new emp_code conflicts with another employee
    if employee.emp_code != employee_id:
        conflict = db.query(Employee).filter(Employee.emp_code == employee.emp_code).first()
        if conflict:
            raise HTTPException(status_code=400, detail=f"Employee code {employee.emp_code} already exists")
    
    existing.emp_code = employee.emp_code
    existing.name = employee.name
    existing.role = employee.role
    
    db.commit()
    db.refresh(existing)
    
    return EmployeeResponse.model_validate(existing)


@router.delete("/employee/{employee_id}", response_model=dict)
def delete_employee(
    employee_id: str,
    db: Session = Depends(get_db)
):
    """Delete an employee. Requires manager/admin role."""
    employee = db.query(Employee).filter(Employee.emp_code == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Delete will cascade to face_embeddings, schedules, and attendance_logs
    db.delete(employee)
    db.commit()
    
    return {"message": f"Employee {employee_id} deleted successfully"}


@router.post("/employee/register-face", response_model=FaceRegistrationResponse)
async def register_face(
    employee_id: str = Form(...),
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Register employee face with multiple images.
    Uses YOLO-face for detection and InsightFace for embedding extraction.
    """
    # Check if employee exists
    employee = db.query(Employee).filter(Employee.emp_code == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    embeddings_count = 0
    faces_detected = 0

    for image in images:
        # Read image
        image_bytes = await image.read()
        
        # Detect faces and get embeddings using real AI models
        face_boxes, embeddings = get_face_embedding_from_image(image_bytes)
        
        if not face_boxes:
            continue  # Skip images with no faces
        
        faces_detected += len(face_boxes)
        
        # Store each embedding in database
        for embedding in embeddings:
            # Validate embedding (should be 512 dimensions for buffalo_l model)
            if len(embedding) == 0 or np.all(embedding == 0):
                continue  # Skip invalid embeddings
            
            face_embedding = FaceEmbedding(
                employee_id=employee.id,
                embedding=embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
            )
            db.add(face_embedding)
            embeddings_count += 1

    if embeddings_count == 0:
        raise HTTPException(
            status_code=400, 
            detail=f"No valid faces detected in images. Detected {faces_detected} faces but no valid embeddings."
        )

    db.commit()

    return FaceRegistrationResponse(
        message=f"Face registered successfully. {embeddings_count} embeddings stored from {faces_detected} detected faces.",
        employee_id=employee_id,
        embeddings_count=embeddings_count
    )

