from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EmployeeBase(BaseModel):
    emp_code: str
    name: str
    role: str


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeResponse(EmployeeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class FaceRegistrationResponse(BaseModel):
    message: str
    employee_id: str
    embeddings_count: int

