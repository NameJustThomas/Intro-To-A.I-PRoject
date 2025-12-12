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
    try:
        # Parse month
        year, month_num = map(int, month.split('-'))
        
        # Query attendance logs for the month with proper joins
        query = db.query(AttendanceLog).join(Employee).filter(
            extract('year', AttendanceLog.timestamp) == year,
            extract('month', AttendanceLog.timestamp) == month_num
        )
        
        if store_id:
            # Filter by store through camera
            query = query.join(Camera).filter(Camera.store_id == int(store_id))
        
        logs = query.all()
        
        # Group by employee
        employee_stats = {}
        for log in logs:
            # Ensure employee relationship is loaded
            if not log.employee:
                continue  # Skip logs without employee
            
            emp_id = log.employee.emp_code
            if emp_id not in employee_stats:
                employee_stats[emp_id] = {
                    'employee_id': emp_id,
                    'employee_name': log.employee.name or 'Unknown',
                    'employee_role': log.employee.role if log.employee.role else None,
                    'present_days': 0,
                    'late_days': 0,
                    'dates': set(),
                    'late_dates': set()
                }
            
            # Count unique dates
            log_date = log.timestamp.date()
            if log_date not in employee_stats[emp_id]['dates']:
                employee_stats[emp_id]['dates'].add(log_date)
                employee_stats[emp_id]['present_days'] += 1
                
                # Count late check-ins
                if log.is_on_time == 0:
                    if log_date not in employee_stats[emp_id]['late_dates']:
                        employee_stats[emp_id]['late_dates'].add(log_date)
                        employee_stats[emp_id]['late_days'] += 1
        
        # Get all employees for total count
        total_employees = db.query(Employee).count()
        
        # Build summary
        attendance_summary = [
            AttendanceSummary(
                employee_id=stats['employee_id'],
                employee_name=stats['employee_name'],
                employee_role=stats['employee_role'],
                total_days=30,  # Stub: should calculate from schedules
                present_days=stats['present_days'],
                late_days=stats['late_days']
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
    except Exception as e:
        # Log the error for debugging
        import traceback
        print(f"Error in get_monthly_attendance: {str(e)}")
        print(traceback.format_exc())
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Failed to fetch attendance data: {str(e)}")

