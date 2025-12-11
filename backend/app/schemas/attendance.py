from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CheckInResponse(BaseModel):
    employee_id: str
    employee_name: str
    timestamp: datetime
    confidence: float
    camera_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_validated: Optional[bool] = None
    distance_from_store: Optional[float] = None


class CheckInHistoryItem(BaseModel):
    id: int
    employee_id: str
    employee_name: str
    employee_role: Optional[str]
    timestamp: datetime
    camera_id: int
    camera_name: Optional[str]
    store_name: Optional[str]
    confidence: float
    latitude: Optional[float]
    longitude: Optional[float]
    location_validated: Optional[int]
    distance_from_store: Optional[float]
    is_on_time: Optional[int]

    class Config:
        from_attributes = True


class AttendanceSummary(BaseModel):
    employee_id: str
    employee_name: str
    employee_role: Optional[str] = None
    total_days: int
    present_days: int
    late_days: int = 0


class MonthlyAttendanceResponse(BaseModel):
    month: str
    store_id: Optional[str]
    total_employees: int
    total_check_ins: int
    attendance_summary: list[AttendanceSummary]

