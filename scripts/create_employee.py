"""
Helper script to create an employee in the database.
Usage: python scripts/create_employee.py --emp_code E003 --name "John Doe" --role "Manager"
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.models.orm_models import Employee


def create_employee(emp_code: str, name: str, role: str):
    """Create a new employee in the database."""
    db = SessionLocal()
    try:
        # Check if employee already exists
        existing = db.query(Employee).filter(Employee.emp_code == emp_code).first()
        if existing:
            print(f"Employee with code {emp_code} already exists!")
            return False

        employee = Employee(emp_code=emp_code, name=name, role=role)
        db.add(employee)
        db.commit()
        db.refresh(employee)
        
        print(f"Employee created successfully:")
        print(f"  ID: {employee.id}")
        print(f"  Code: {employee.emp_code}")
        print(f"  Name: {employee.name}")
        print(f"  Role: {employee.role}")
        return True
        
    except Exception as e:
        print(f"Error creating employee: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description='Create a new employee')
    parser.add_argument('--emp_code', required=True, help='Employee code')
    parser.add_argument('--name', required=True, help='Employee name')
    parser.add_argument('--role', required=True, help='Employee role')
    
    args = parser.parse_args()
    
    success = create_employee(args.emp_code, args.name, args.role)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

