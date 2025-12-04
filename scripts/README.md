# Scripts Directory

This directory contains utility scripts for managing the AI Attendance System.

## Available Scripts

### Database Management

#### `init_db.py`
Initialize the database by running SQL migrations.

**Usage:**
```bash
python scripts/init_db.py
```

**Requirements:**
- Database must be running
- DATABASE_URL environment variable must be set (or use default from config)

---

#### `import_sample_data.py`
Import sample employees and schedules from CSV files.

**Usage:**
```bash
python scripts/import_sample_data.py
```

**Requirements:**
- Database must be initialized
- CSV files must exist in `scripts/sample_data/`:
  - `employees.csv`
  - `schedules.csv`

**CSV Format:**

`employees.csv`:
```csv
emp_code,name,role
E001,John Doe,Barista
E002,Jane Smith,Cashier
```

`schedules.csv`:
```csv
emp_code,date,shift_start,shift_end
E001,2025-11-01,2025-11-01 08:00,2025-11-01 16:00
E002,2025-11-01,2025-11-01 09:00,2025-11-01 17:00
```

---

### Data Management

#### `create_employee.py`
Create a new employee in the database.

**Usage:**
```bash
python scripts/create_employee.py --emp_code E003 --name "John Doe" --role "Manager"
```

**Arguments:**
- `--emp_code` (required): Unique employee code
- `--name` (required): Employee full name
- `--role` (required): Employee role/position

---

#### `create_store.py`
Create a new store with a camera in the database.

**Usage:**
```bash
python scripts/create_store.py \
  --name "Main Store" \
  --address "123 Main St" \
  --camera_name "Camera 1" \
  --location "Entrance" \
  --rtsp_url "rtsp://camera-url"  # optional
```

**Arguments:**
- `--name` (required): Store name
- `--address` (required): Store address
- `--camera_name` (required): Camera name/identifier
- `--location` (required): Camera location description
- `--rtsp_url` (optional): RTSP stream URL for the camera

---

## Environment Setup

All scripts require:
1. Python 3.11+
2. Database connection (via DATABASE_URL or default config)
3. Installed dependencies from `backend/requirements.txt`

To install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

## Notes

- Scripts use the same database configuration as the main application
- All scripts include error handling and rollback on failure
- Scripts can be run from the project root directory
- Make sure the database is running before executing scripts

