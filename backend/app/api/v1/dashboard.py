from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import extract
from typing import Optional
from app.db.base import get_db
from app.schemas.attendance import MonthlyAttendanceResponse, AttendanceSummary
from app.models.orm_models import Employee, AttendanceLog, Store, Camera

router = APIRouter()


@router.get("/dashboard/attendance-month", response_model=MonthlyAttendanceResponse)
def get_monthly_attendance(
    month: str = Query(..., pattern=r'^\d{4}-\d{2}$'),
    store_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get monthly attendance summary.
    """
    # Parse month
    year, month_num = map(int, month.split('-'))
    
    # Query attendance logs for the month
    query = db.query(AttendanceLog).filter(
        extract('year', AttendanceLog.timestamp) == year,
        extract('month', AttendanceLog.timestamp) == month_num
    )
    
    if store_id:
        # Filter by store through camera
        query = query.join(AttendanceLog.camera).filter(Camera.store_id == int(store_id))
    
    logs = query.all()
    
    # Group by employee
    employee_stats = {}
    for log in logs:
        emp_id = log.employee.emp_code
        if emp_id not in employee_stats:
            employee_stats[emp_id] = {
                'employee_id': emp_id,
                'employee_name': log.employee.name,
                'present_days': 0,
                'dates': set()
            }
        
        # Count unique dates
        log_date = log.timestamp.date()
        if log_date not in employee_stats[emp_id]['dates']:
            employee_stats[emp_id]['dates'].add(log_date)
            employee_stats[emp_id]['present_days'] += 1
    
    # Get all employees for total count
    total_employees = db.query(Employee).count()
    
    # Build summary
    attendance_summary = [
        AttendanceSummary(
            employee_id=stats['employee_id'],
            employee_name=stats['employee_name'],
            total_days=30,  # Stub: should calculate from schedules
            present_days=stats['present_days']
        )
        for stats in employee_stats.values()
    ]
    
    return MonthlyAttendanceResponse(
        month=month,
        store_id=store_id,
        total_employees=total_employees,
        total_check_ins=len(logs),
        attendance_summary=attendance_summary
    )

