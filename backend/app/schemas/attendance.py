from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CheckInResponse(BaseModel):
    employee_id: str
    employee_name: str
    timestamp: datetime
    confidence: float
    camera_id: str


class AttendanceSummary(BaseModel):
    employee_id: str
    employee_name: str
    total_days: int
    present_days: int


class MonthlyAttendanceResponse(BaseModel):
    month: str
    store_id: Optional[str]
    total_employees: int
    total_check_ins: int
    attendance_summary: list[AttendanceSummary]

