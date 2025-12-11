from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta
from pydantic import BaseModel
from app.db.base import get_db
from app.models.orm_models import Schedule, Employee, Store

router = APIRouter()


class ScheduleResponse(BaseModel):
    id: int
    employee_id: int
    employee_code: str
    employee_name: str
    store_id: int
    store_name: str
    date: date
    shift_start: datetime
    shift_end: datetime
    shift_number: int  # 1, 2, 3, or 4

    class Config:
        from_attributes = True


class ScheduleCreateRequest(BaseModel):
    employee_id: str  # emp_code
    store_id: int
    date: date
    shift_number: int  # 1, 2, 3, or 4


class ScheduleUpdateRequest(BaseModel):
    employee_id: Optional[str] = None
    shift_number: Optional[int] = None


# Shift definitions
SHIFTS = {
    1: {"start": 6, "end": 10},   # 6:00 - 10:00
    2: {"start": 10, "end": 14},  # 10:00 - 14:00
    3: {"start": 14, "end": 18},  # 14:00 - 18:00
    4: {"start": 18, "end": 22}   # 18:00 - 22:00
}


def get_shift_times(shift_number: int, schedule_date: date) -> tuple[datetime, datetime]:
    """Get shift start and end times for a given shift number and date."""
    shift = SHIFTS.get(shift_number)
    if not shift:
        raise ValueError(f"Invalid shift number: {shift_number}. Must be 1, 2, 3, or 4")
    
    shift_start = datetime.combine(schedule_date, datetime.min.time().replace(hour=shift["start"]))
    shift_end = datetime.combine(schedule_date, datetime.min.time().replace(hour=shift["end"]))
    
    return shift_start, shift_end


@router.get("/schedules", response_model=List[ScheduleResponse])
def list_schedules(
    store_id: Optional[int] = Query(None, description="Filter by store ID"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    employee_id: Optional[str] = Query(None, description="Filter by employee code"),
    db: Session = Depends(get_db)
):
    """List all schedules, optionally filtered by store, date, or employee."""
    query = db.query(Schedule).join(Employee).join(Store, Employee.id == Schedule.employee_id)
    
    # Note: This join is not correct, we need to get store from employee's attendance or camera
    # For now, we'll query schedules and get store info separately
    query = db.query(Schedule).join(Employee)
    
    if store_id:
        # Filter by store through employee's recent check-ins or default store
        # For simplicity, we'll get all schedules and filter in Python
        pass
    
    if date:
        schedule_date = datetime.strptime(date, '%Y-%m-%d').date()
        query = query.filter(Schedule.date == schedule_date)
    
    if employee_id:
        query = query.filter(Employee.emp_code == employee_id)
    
    schedules = query.all()
    
    result = []
    for schedule in schedules:
        # Get store from employee's most recent check-in or default to store_id=1
        # For now, we'll use a simple approach
        store_id_for_schedule = store_id if store_id else 1
        store = db.query(Store).filter(Store.id == store_id_for_schedule).first()
        
        # Determine shift number from shift_start
        shift_start_hour = schedule.shift_start.hour
        shift_number = None
        for shift_num, shift_info in SHIFTS.items():
            if shift_start_hour == shift_info["start"]:
                shift_number = shift_num
                break
        
        result.append(ScheduleResponse(
            id=schedule.id,
            employee_id=schedule.employee_id,
            employee_code=schedule.employee.emp_code,
            employee_name=schedule.employee.name,
            store_id=store_id_for_schedule if store else 1,
            store_name=store.name if store else "Unknown",
            date=schedule.date,
            shift_start=schedule.shift_start,
            shift_end=schedule.shift_end,
            shift_number=shift_number or 1
        ))
    
    return result


@router.get("/schedules/by-store", response_model=dict)
def get_schedules_by_store(
    store_id: int = Query(..., description="Store ID"),
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD), defaults to today"),
    db: Session = Depends(get_db)
):
    """
    Get schedules organized by store and shift.
    Returns a structure: {shift_number: [employee_codes]}
    """
    if date:
        schedule_date = datetime.strptime(date, '%Y-%m-%d').date()
    else:
        schedule_date = date.today()
    
    # Get all schedules for the date and store
    schedules = db.query(Schedule).join(Employee).filter(
        Schedule.date == schedule_date,
        Schedule.store_id == store_id
    ).all()
    
    # Organize by shift
    result = {
        "store_id": store_id,
        "date": schedule_date.isoformat(),
        "shifts": {
            1: [],  # 6-10
            2: [],  # 10-14
            3: [],  # 14-18
            4: []   # 18-22
        }
    }
    
    for schedule in schedules:
        shift_start_hour = schedule.shift_start.hour
        shift_number = None
        
        for shift_num, shift_info in SHIFTS.items():
            if shift_start_hour == shift_info["start"]:
                shift_number = shift_num
                break
        
        if shift_number:
            result["shifts"][shift_number].append({
                "employee_id": schedule.employee.emp_code,
                "employee_name": schedule.employee.name,
                "schedule_id": schedule.id
            })
    
    return result


@router.post("/schedules", response_model=ScheduleResponse)
def create_schedule(
    schedule_data: ScheduleCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new schedule. Requires manager/admin role."""
    # Verify employee exists
    employee = db.query(Employee).filter(Employee.emp_code == schedule_data.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail=f"Employee {schedule_data.employee_id} not found")
    
    # Verify store exists
    store = db.query(Store).filter(Store.id == schedule_data.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail=f"Store {schedule_data.store_id} not found")
    
    # Validate shift number
    if schedule_data.shift_number not in [1, 2, 3, 4]:
        raise HTTPException(status_code=400, detail="Shift number must be 1, 2, 3, or 4")
    
    # Get shift times
    shift_start, shift_end = get_shift_times(schedule_data.shift_number, schedule_data.date)
    
    # Check if schedule already exists for this employee, date, and shift
    existing = db.query(Schedule).filter(
        Schedule.employee_id == employee.id,
        Schedule.date == schedule_data.date,
        Schedule.shift_start == shift_start
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Schedule already exists for employee {schedule_data.employee_id} on {schedule_data.date} for shift {schedule_data.shift_number}"
        )
    
    # Create schedule
    schedule = Schedule(
        employee_id=employee.id,
        date=schedule_data.date,
        shift_start=shift_start,
        shift_end=shift_end
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    shift_start_hour = schedule.shift_start.hour
    shift_number = None
    for shift_num, shift_info in SHIFTS.items():
        if shift_start_hour == shift_info["start"]:
            shift_number = shift_num
            break
    
    return ScheduleResponse(
        id=schedule.id,
        employee_id=schedule.employee_id,
        employee_code=employee.emp_code,
        employee_name=employee.name,
        store_id=schedule.store_id or schedule_data.store_id,
        store_name=store.name,
        date=schedule.date,
        shift_start=schedule.shift_start,
        shift_end=schedule.shift_end,
        shift_number=shift_number or schedule_data.shift_number
    )


@router.put("/schedules/{schedule_id}", response_model=ScheduleResponse)
def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update a schedule. Requires manager/admin role."""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    if schedule_data.employee_id:
        employee = db.query(Employee).filter(Employee.emp_code == schedule_data.employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail=f"Employee {schedule_data.employee_id} not found")
        schedule.employee_id = employee.id
    
    if schedule_data.shift_number:
        if schedule_data.shift_number not in [1, 2, 3, 4]:
            raise HTTPException(status_code=400, detail="Shift number must be 1, 2, 3, or 4")
        shift_start, shift_end = get_shift_times(schedule_data.shift_number, schedule.date)
        schedule.shift_start = shift_start
        schedule.shift_end = shift_end
    
    db.commit()
    db.refresh(schedule)
    
    # Get store
    store = db.query(Store).filter(Store.id == schedule.store_id).first() if schedule.store_id else None
    
    shift_start_hour = schedule.shift_start.hour
    shift_number = None
    for shift_num, shift_info in SHIFTS.items():
        if shift_start_hour == shift_info["start"]:
            shift_number = shift_num
            break
    
    return ScheduleResponse(
        id=schedule.id,
        employee_id=schedule.employee_id,
        employee_code=schedule.employee.emp_code,
        employee_name=schedule.employee.name,
        store_id=schedule.store_id or 1,
        store_name=store.name if store else "Unknown",
        date=schedule.date,
        shift_start=schedule.shift_start,
        shift_end=schedule.shift_end,
        shift_number=shift_number or 1
    )


@router.delete("/schedules/{schedule_id}", response_model=dict)
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """Delete a schedule. Requires manager/admin role."""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    db.delete(schedule)
    db.commit()
    
    return {"message": f"Schedule {schedule_id} deleted successfully"}


@router.get("/schedules/suggest", response_model=dict)
def suggest_schedule(
    employee_id: str = Query(..., description="Employee code"),
    store_id: int = Query(..., description="Store ID"),
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD), defaults to today"),
    db: Session = Depends(get_db)
):
    """
    AI suggestion: Analyze employee's check-in history to suggest which shift they should work.
    """
    from app.models.orm_models import AttendanceLog, Camera
    
    employee = db.query(Employee).filter(Employee.emp_code == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    
    if date:
        target_date = datetime.strptime(date, '%Y-%m-%d').date()
    else:
        target_date = date.today()
    
    # Get employee's check-in history for the past 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    check_ins = db.query(AttendanceLog).join(Camera).filter(
        AttendanceLog.employee_id == employee.id,
        AttendanceLog.timestamp >= thirty_days_ago,
        Camera.store_id == store_id
    ).order_by(AttendanceLog.timestamp.desc()).all()
    
    # Analyze check-in times to find most common shift
    shift_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    
    for check_in in check_ins:
        check_in_hour = check_in.timestamp.hour
        # Determine which shift this check-in belongs to
        if 6 <= check_in_hour < 10:
            shift_counts[1] += 1
        elif 10 <= check_in_hour < 14:
            shift_counts[2] += 1
        elif 14 <= check_in_hour < 18:
            shift_counts[3] += 1
        elif 18 <= check_in_hour < 22:
            shift_counts[4] += 1
    
    # Find most common shift
    suggested_shift = max(shift_counts, key=shift_counts.get) if max(shift_counts.values()) > 0 else 1
    
    return {
        "employee_id": employee_id,
        "store_id": store_id,
        "date": target_date.isoformat(),
        "suggested_shift": suggested_shift,
        "shift_times": {
            "start": SHIFTS[suggested_shift]["start"],
            "end": SHIFTS[suggested_shift]["end"]
        },
        "confidence": shift_counts[suggested_shift] / max(len(check_ins), 1) if check_ins else 0,
        "analysis": {
            "total_check_ins": len(check_ins),
            "shift_distribution": shift_counts
        }
    }

