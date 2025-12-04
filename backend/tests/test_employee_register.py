"""
Unit tests for employee face registration endpoint.
"""
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.base import SessionLocal, engine
from app.models.orm_models import Base, Employee, FaceEmbedding
import io
from PIL import Image

# Create test database
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def create_test_employee(db: Session, emp_code: str = "E001", name: str = "Test Employee"):
    """Helper to create a test employee."""
    employee = Employee(emp_code=emp_code, name=name, role="Test")
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def create_test_image() -> bytes:
    """Helper to create a test image."""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


def test_register_face_employee_not_found():
    """Test registering face for non-existent employee."""
    response = client.post(
        "/api/v1/employee/register-face",
        data={"employee_id": "E999"},
        files={"images": ("test.png", create_test_image(), "image/png")}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_register_face_success():
    """Test successful face registration."""
    # Setup: Create employee in database
    db = SessionLocal()
    try:
        employee = create_test_employee(db, "E002", "Test Employee 2")
        
        # Test registration
        response = client.post(
            "/api/v1/employee/register-face",
            data={"employee_id": employee.emp_code},
            files={"images": ("test.png", create_test_image(), "image/png")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["employee_id"] == employee.emp_code
        assert data["embeddings_count"] > 0
        
        # Verify embedding was stored
        embeddings = db.query(FaceEmbedding).filter(
            FaceEmbedding.employee_id == employee.id
        ).all()
        assert len(embeddings) > 0
        
    finally:
        # Cleanup
        db.query(FaceEmbedding).filter(FaceEmbedding.employee_id == employee.id).delete()
        db.query(Employee).filter(Employee.id == employee.id).delete()
        db.commit()
        db.close()

