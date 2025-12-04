"""
Script to import sample data from CSV files.
Creates employees and schedules from CSV files.
"""
import csv
import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.base import SessionLocal, engine
from app.models.orm_models import Base, Employee, Schedule

# Create tables
Base.metadata.create_all(bind=engine)


def import_employees(db: Session, csv_path: str):
    """Import employees from CSV file."""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check if employee already exists
            existing = db.query(Employee).filter(Employee.emp_code == row['emp_code']).first()
            if existing:
                print(f"Employee {row['emp_code']} already exists, skipping...")
                continue
            
            employee = Employee(
                emp_code=row['emp_code'],
                name=row['name'],
                role=row['role']
            )
            db.add(employee)
            print(f"Added employee: {row['emp_code']} - {row['name']}")
    
    db.commit()


def import_schedules(db: Session, csv_path: str):
    """Import schedules from CSV file."""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Find employee by emp_code
            employee = db.query(Employee).filter(Employee.emp_code == row['emp_code']).first()
            if not employee:
                print(f"Employee {row['emp_code']} not found, skipping schedule...")
                continue
            
            # Parse dates
            date = datetime.strptime(row['date'], '%Y-%m-%d').date()
            shift_start = datetime.strptime(row['shift_start'], '%Y-%m-%d %H:%M')
            shift_end = datetime.strptime(row['shift_end'], '%Y-%m-%d %H:%M')
            
            schedule = Schedule(
                employee_id=employee.id,
                date=date,
                shift_start=shift_start,
                shift_end=shift_end
            )
            db.add(schedule)
            print(f"Added schedule for {row['emp_code']} on {row['date']}")
    
    db.commit()


def main():
    """Main function to import all sample data."""
    db = SessionLocal()
    
    try:
        # Get script directory
        script_dir = Path(__file__).parent
        sample_data_dir = script_dir / 'sample_data'
        
        employees_csv = sample_data_dir / 'employees.csv'
        schedules_csv = sample_data_dir / 'schedules.csv'
        
        if not employees_csv.exists():
            print(f"Error: {employees_csv} not found")
            return
        
        if not schedules_csv.exists():
            print(f"Error: {schedules_csv} not found")
            return
        
        print("Importing employees...")
        import_employees(db, str(employees_csv))
        
        print("\nImporting schedules...")
        import_schedules(db, str(schedules_csv))
        
        print("\nSample data import completed!")
        
    except Exception as e:
        print(f"Error importing data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()

