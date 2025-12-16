from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class PerformanceMetricsResponse(BaseModel):
    """Performance metrics for check-in operation."""
    total_time_ms: float
    image_upload_ms: float
    face_detection_ms: float
    anti_spoofing_ms: float
    face_recognition_ms: float
    database_matching_ms: float
    database_write_ms: float
    location_validation_ms: float
    num_faces_detected: int
    num_embeddings_searched: int
    confidence_score: float
    cpu_percent: float  # Normalized 0-100%
    cpu_cores: int  # Number of CPU cores
    ram_usage_mb: float
    ram_percent: float
    gpu_available: bool
    gpu_memory_mb: Optional[float] = None
    slow_detection_warning: bool = False  # True if face detection was slow (>5s)
    # Per-model memory usage (MB)
    face_detection_memory_mb: float = 0.0
    face_recognition_memory_mb: float = 0.0
    anti_spoofing_memory_mb: float = 0.0


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
    performance_metrics: Optional[PerformanceMetricsResponse] = None


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


class CheckInErrorResponse(BaseModel):
    """Error response with performance metrics for debugging."""
    detail: str
    error_type: str
    performance_metrics: Optional[PerformanceMetricsResponse] = None

