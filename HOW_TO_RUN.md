# How to Run the Project - Step by Step Guide

This guide will walk you through setting up and running the AI Attendance System from scratch.

## Prerequisites

Before starting, ensure you have:
- ✅ **Docker Desktop** installed and running
- ✅ **Docker Compose** (usually included with Docker Desktop)
- ✅ **Python 3.11+** (for running scripts locally, optional)
- ✅ **Git** (if cloning the repository)

## Step 1: Verify Docker is Running

1. Open Docker Desktop
2. Wait until Docker shows "Docker Desktop is running"
3. Verify in terminal:
   ```bash
   docker --version
   docker compose version
   ```

## Step 2: Navigate to Project Directory

```bash
cd D:\Intro-To-A.I-PRoject
```

## Step 3: Start All Services with Docker Compose

```bash
cd infra
docker compose up --build
```

**What this does:**
- Builds the backend Docker image
- Starts PostgreSQL database
- Starts Redis cache
- Starts FastAPI backend
- Starts nginx reverse proxy

**Expected output:**
- You'll see logs from all services
- Wait for messages like "Application startup complete"
- Services will be running on:
  - Backend: http://localhost:8000
  - PostgreSQL: localhost:5432
  - Redis: localhost:6379
  - Nginx: http://localhost:80

**Note:** Keep this terminal window open. Press `Ctrl+C` to stop all services.

## Step 4: Initialize the Database (New Terminal)

Open a **new terminal window** (keep the first one running):

```bash
# Navigate to project root
cd D:\Intro-To-A.I-PRoject

# Run database initialization script
python scripts/init_db.py
```

**Expected output:**
```
Running database migration...
Database initialized successfully!
```

**If you get an error:**
- Make sure PostgreSQL container is running (check Step 3)
- Wait a few seconds for PostgreSQL to be fully ready
- Check that DATABASE_URL is correct in `backend/app/core/config.py`

## Step 5: Import Sample Data (Optional but Recommended)

In the same terminal:

```bash
python scripts/import_sample_data.py
```

**Expected output:**
```
Importing employees...
Added employee: E001 - Nguyen Van A
Added employee: E002 - Tran Thi B

Importing schedules...
Added schedule for E001 on 2025-11-01
Added schedule for E002 on 2025-11-01

Sample data import completed!
```

## Step 6: Verify Backend is Running

1. Open your web browser
2. Go to: **http://localhost:8000/docs**
3. You should see the **FastAPI Swagger UI** with all API endpoints

**Test the health endpoint:**
- Click on `GET /health`
- Click "Try it out"
- Click "Execute"
- You should see: `{"status": "ok"}`

## Step 7: Test API Endpoints

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```
Expected: `{"status":"ok"}`

### Test 2: List Cameras
```bash
curl http://localhost:8000/api/v1/cameras
```
Expected: `[]` (empty array, no cameras yet)

### Test 3: Get Monthly Attendance
```bash
curl "http://localhost:8000/api/v1/dashboard/attendance-month?month=2025-11"
```
Expected: JSON with attendance summary

## Step 8: Run Frontend Dashboard (Optional)

If you want to run the React dashboard:

### 8.1 Install Node.js Dependencies

Open a **new terminal**:

```bash
cd D:\Intro-To-A.I-PRoject\frontend\dashboard
npm install
```

**Note:** Requires Node.js and npm installed. If not installed, skip this step.

### 8.2 Start Frontend Development Server

```bash
npm start
```

**Expected:**
- Browser opens automatically to http://localhost:3000
- Dashboard UI loads
- You can view attendance data

## Step 9: Create Test Data (Optional)

### Create an Employee

```bash
cd D:\Intro-To-A.I-PRoject
python scripts/create_employee.py --emp_code E003 --name "John Doe" --role "Manager"
```

### Create a Store with Camera

```bash
python scripts/create_store.py \
  --name "Main Store" \
  --address "123 Main St" \
  --camera_name "Camera 1" \
  --location "Entrance"
```

## Step 10: Stop Services

When you're done:

1. Go to the terminal running `docker compose up`
2. Press `Ctrl+C`
3. Wait for services to stop gracefully

**Or stop and remove containers:**
```bash
cd infra
docker compose down
```

**To remove everything including volumes:**
```bash
docker compose down -v
```

## Troubleshooting

### Problem: Docker containers won't start

**Solution:**
- Check Docker Desktop is running
- Restart Docker Desktop
- Check ports 8000, 5432, 6379, 80 are not in use:
  ```bash
  netstat -ano | findstr :8000
  ```

### Problem: Database connection error

**Solution:**
- Wait 10-15 seconds after starting docker compose
- Check PostgreSQL container is healthy:
  ```bash
  docker ps
  ```
- Verify DATABASE_URL in `backend/app/core/config.py`

### Problem: "Module not found" when running scripts

**Solution:**
- Install Python dependencies:
  ```bash
  cd backend
  pip install -r requirements.txt
  ```

### Problem: Port already in use

**Solution:**
- Change ports in `infra/docker-compose.yml`:
  ```yaml
  ports:
    - '8001:8000'  # Change 8000 to 8001
  ```

### Problem: Frontend won't connect to backend

**Solution:**
- Check backend is running on http://localhost:8000
- Update `frontend/dashboard/src/App.js`:
  ```javascript
  const API_BASE_URL = 'http://localhost:8000/api';
  ```

## Quick Command Reference

```bash
# Start everything
cd infra && docker compose up --build

# Initialize database
python scripts/init_db.py

# Import sample data
python scripts/import_sample_data.py

# Create employee
python scripts/create_employee.py --emp_code E001 --name "Name" --role "Role"

# Create store
python scripts/create_store.py --name "Store" --address "Address" --camera_name "Cam1" --location "Loc"

# Stop services
cd infra && docker compose down

# View logs
cd infra && docker compose logs -f

# Run tests
cd backend && pytest
```

## Verification Checklist

After following all steps, verify:

- [ ] Docker containers are running (`docker ps` shows 4 containers)
- [ ] Backend API accessible at http://localhost:8000/docs
- [ ] Health endpoint returns `{"status": "ok"}`
- [ ] Database initialized (no errors from init_db.py)
- [ ] Sample data imported (employees and schedules exist)
- [ ] Frontend dashboard loads (if running)

## Next Steps

Once everything is running:

1. **Explore the API:**
   - Visit http://localhost:8000/docs
   - Try different endpoints
   - Test face registration and check-in

2. **Read Documentation:**
   - `PROJECT_NOTES.md` - Implementation details
   - `CONTRIBUTING.md` - Development guidelines
   - `docs/architecture.md` - System architecture

3. **Start Development:**
   - Make code changes
   - Run tests: `cd backend && pytest`
   - Check code quality: `cd backend && black . && isort . && flake8 .`

## Need Help?

- Check `README.md` for quick reference
- Check `PROJECT_NOTES.md` for implementation details
- Check `DOCUMENTATION_GUIDE.md` for file guide
- Review error messages in terminal output

---

**That's it!** Your AI Attendance System should now be running. 🎉

