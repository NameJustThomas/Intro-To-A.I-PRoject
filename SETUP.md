# Setup Guide - AI Attendance System

Complete guide for first-time setup and running the AI Attendance System.

## 📋 Table of Contents

- [Overview](#-overview)
- [Prerequisites](#-prerequisites)
- [First-Time Setup](#-first-time-setup)
- [Using the System](#-using-the-system)
- [Frontend Setup](#-frontend-setup)
- [Subsequent Runs](#-subsequent-runs-quick-start)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Quick Command Reference](#-quick-command-reference)
- [Verification Checklist](#-verification-checklist)

## 📋 Overview

### What This Project Does

AI-powered employee attendance system for takeaway coffee shops using:
- **Face Recognition** to identify employees when they check in
- **YOLO11** for face detection and people counting
- **InsightFace** for face embedding extraction and recognition
- **MiniFASNet** for anti-spoofing detection (prevents photo/video attacks)
- **Real-time attendance tracking** with location (camera) and timestamp
- **GPS location verification** to ensure employees are at the correct store

### Key Features

- ✅ **Employee Face Registration**: Register employees with multiple face images
- ✅ **Face Recognition Check-in**: Automated check-in using AI face recognition
- ✅ **Anti-Spoofing Detection**: Prevents photo/video attacks
- ✅ **GPS Location Verification**: Ensures employees are at correct store location
- ✅ **Attendance Logging**: Records with confidence scores and timestamps
- ✅ **Monthly Attendance Dashboard**: View attendance reports and analytics
- ✅ **Camera-based Location Tracking**: Multi-camera support with RTSP streaming
- ✅ **Performance Monitoring**: Automatic latency, memory, and CPU tracking

---

## 📦 Prerequisites

Before starting, ensure you have:

### Required Software

- ✅ **Docker Desktop** installed and running
  - Download from: https://www.docker.com/products/docker-desktop
  - Verify: `docker --version` and `docker compose version`
- ✅ **Docker Compose** (included with Docker Desktop)
- ✅ **Node.js 16+** and npm (for frontend development)
  - Download from: https://nodejs.org/
  - Verify: `node --version` and `npm --version`
- ✅ **Python 3.11+** (for running scripts locally)
  - Download from: https://www.python.org/downloads/
  - Verify: `python --version`

### System Requirements

- ✅ **At least 8GB RAM** (AI models require memory)
- ✅ **Internet connection** (for downloading models on first run)
- ✅ **10GB+ free disk space** (for Docker images and AI models)

### First-Time Model Download

- Models will download automatically on first use (5-10 minutes)
- Total download size: ~500MB (InsightFace buffalo_l model)
- YOLO models: ~40MB each
- MiniFASNet models: ~2MB each

---

## 🚀 First-Time Setup

### Step 1: Verify Docker is Running

1. Open **Docker Desktop**
2. Wait until it shows "Docker Desktop is running" (green icon)
3. Verify in terminal:
   ```powershell
   docker --version
   docker compose version
   ```
   
   **Expected output:**
   ```
   Docker version 24.0.x
   Docker Compose version v2.x.x
   ```

### Step 2: Navigate to Project Directory

```powershell
cd D:\Intro-To-A.I-PRoject
```

**Note:** Adjust the path to match your project location.

### Step 3: Start All Services

```powershell
cd infra
docker compose up --build -d
```

**What this does:**
- Builds the backend Docker image with all dependencies
- Starts PostgreSQL database (port 5432)
- Starts Redis cache (port 6379)
- Starts FastAPI backend (port 8000)
- Starts nginx reverse proxy (port 80)

**Expected output:**
```
[+] Running 4/4
 ✔ Container infra-postgres-1    Started
 ✔ Container infra-redis-1      Started
 ✔ Container infra-backend-1    Started
 ✔ Container infra-nginx-1      Started
```

**Service URLs:**
- Backend API: http://localhost:8000
- Backend Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Nginx: http://localhost:80

**Important Notes:**
- The `-d` flag runs services in the background
- Models will download automatically on first use (5-10 minutes)
- Wait 10-15 seconds for PostgreSQL to be ready before next step

### Step 4: Initialize the Database

Wait 10-15 seconds for PostgreSQL to be ready, then:

```powershell
cd D:\Intro-To-A.I-PRoject
$env:PYTHONPATH="D:\Intro-To-A.I-PRoject\backend"
python scripts/init_db.py
```

**Expected output:**
```
Running database migration...
Database initialized successfully!
```

**What this does:**
- Creates all database tables (stores, employees, cameras, attendance_logs, etc.)
- Sets up indexes and constraints
- Prepares database for use

**If you see errors:**
- Wait a bit longer (PostgreSQL may still be starting)
- Check Docker logs: `docker logs infra-postgres-1`

### Step 5: Import Sample Data (Optional but Recommended)

```powershell
python scripts/import_sample_data.py
```

**Expected output:**
```
Importing employees...
Added employee: E001 - Nguyen Van A
Added employee: E002 - Tran Thi B
...

Importing schedules...
Sample data import completed!
```

**What this does:**
- Creates sample employees (E001, E002, etc.)
- Creates sample schedules for testing
- Makes it easier to test the system

**CSV Files Location:**
- `scripts/sample_data/employees.csv`
- `scripts/sample_data/schedules.csv`

### Step 6: Create a Store and Camera

You need at least one store and camera for check-in to work:

```powershell
python scripts/create_store.py `
  --name "Main Store" `
  --address "123 Main St, City" `
  --camera_name "Camera 1" `
  --location "Entrance" `
  --rtsp_url "rtsp://camera-url"  # Optional: for RTSP streaming
```

**Expected output:**
```
Store created: Main Store (ID: 1)
Camera created: Camera 1 (ID: 1)
```

**⚠️ Important:** Note the **Camera ID** - you'll need it for check-in!

**Alternative:** You can also create stores/cameras via API:
- POST `/api/v1/stores` - Create store
- POST `/api/v1/cameras` - Create camera

### Step 7: Verify Everything is Running

1. **Check Docker Containers:**
   ```powershell
   docker ps
   ```
   
   Should show 4 containers running:
   - `infra-postgres-1`
   - `infra-redis-1`
   - `infra-backend-1`
   - `infra-nginx-1`

2. **Test Backend API:**
   - Open browser: **http://localhost:8000/docs**
   - You should see the **FastAPI Swagger UI**
   - Test health endpoint: `GET /health` should return:
     ```json
     {"status": "ok"}
     ```

3. **Check Backend Logs:**
   ```powershell
   docker logs infra-backend-1 --tail 20
   ```
   
   Should show: `Application startup complete`

---

## 🎯 Using the System

### Register an Employee Face

Before employees can check in, you need to register their faces.

#### Using Swagger UI (Recommended for Testing)

1. Go to **http://localhost:8000/docs**
2. Find `POST /api/v1/employee/register-face`
3. Click "Try it out"
4. Enter `employee_id`: `E001` (or any employee code)
5. Upload **2-3 face images** (use "Choose Files" button)
6. Click "Execute"

**Expected response:**
```json
{
  "message": "Face registered successfully",
  "employee_id": "E001",
  "embeddings_count": 3
}
```

#### Using Frontend (Kiosk UI)

1. Start frontend (see [Frontend Setup](#-frontend-setup))
2. Navigate to employee registration page
3. Enter employee code
4. Upload multiple face images
5. Submit

**Tips for Best Results:**
- ✅ Use clear, front-facing photos
- ✅ Good lighting (avoid shadows)
- ✅ Multiple angles improve accuracy (front, slight left, slight right)
- ✅ Avoid sunglasses, masks, or heavy makeup
- ✅ Minimum 2 images, recommended 3-5 images

### Check In Using Face Recognition

#### Using Swagger UI

1. Go to **http://localhost:8000/docs**
2. Find `POST /api/v1/attendance/check-in`
3. Click "Try it out"
4. Enter `camera_id`: `1` (the camera ID from Step 6)
5. Upload a face image
6. (Optional) Enter GPS coordinates: `latitude` and `longitude`
7. Click "Execute"

**Expected response:**
```json
{
  "success": true,
  "employee": {
    "emp_code": "E001",
    "name": "Nguyen Van A"
  },
  "attendance": {
    "timestamp": "2025-12-16T10:30:00",
    "is_on_time": true,
    "confidence": 0.95
  },
  "performance_metrics": {
    "total_time_ms": 1200,
    "face_detection_ms": 150,
    "anti_spoofing_ms": 100,
    "face_recognition_ms": 200,
    ...
  }
}
```

#### Using Frontend (Kiosk UI)

1. Start frontend (see [Frontend Setup](#-frontend-setup))
2. Navigate to **http://localhost:3001**
3. Allow camera access when prompted
4. Position face in front of camera
5. Click "Check In" button
6. Wait for recognition (1-2 seconds)

### View Attendance Dashboard

#### Using API

1. Go to **http://localhost:8000/docs**
2. Find `GET /api/v1/dashboard/attendance-month`
3. Enter query parameters:
   - `year`: `2025`
   - `month`: `12`
   - `employee_id`: (optional, filter by employee)
4. Click "Execute"

#### Using Frontend Dashboard

1. Start frontend dashboard (see [Frontend Setup](#-frontend-setup))
2. Navigate to **http://localhost:3001/dashboard**
3. View monthly attendance reports
4. Filter by employee, date range, etc.

---

## 💻 Frontend Setup

### Kiosk UI (Check-in Interface)

**First Time:**
```powershell
cd frontend/kiosk_ui
npm install
npm start
```

**Subsequent Runs:**
```powershell
cd frontend/kiosk_ui
npm start
```

**Access:** http://localhost:3001

**Features:**
- Real-time camera feed
- Face detection visualization
- Check-in button
- Performance metrics display
- Error handling and feedback

### Dashboard (Reports Interface)

**First Time:**
```powershell
cd frontend/dashboard
npm install
npm start
```

**Subsequent Runs:**
```powershell
cd frontend/dashboard
npm start
```

**Access:** http://localhost:3002 (or configured port)

**Features:**
- Monthly attendance reports
- Employee statistics
- Attendance analytics
- Export functionality

---

## 🔄 Subsequent Runs (Quick Start)

After initial setup, you only need:

### Start Backend Services

```powershell
cd infra
docker compose up -d
```

Wait 10-15 seconds, then access: **http://localhost:8000/docs**

### Start Frontend

```powershell
cd frontend/kiosk_ui
npm start
```

Access: **http://localhost:3001**

### You DON'T Need To:

- ❌ Re-initialize database (already done)
- ❌ Re-import sample data (already done)
- ❌ Re-create store/camera (already done)
- ❌ Re-download models (cached in Docker image)

### Stop Services

```powershell
# Stop frontend: Press Ctrl+C in the terminal running npm start

# Stop Docker services:
cd infra
docker compose down
```

---

## 🔧 Configuration

### Adjust Face Recognition Threshold

Edit `backend/app/api/v1/attendance.py`:

```python
SIMILARITY_THRESHOLD = 0.6  # Range: 0.5-0.8
# Lower = more lenient (more false positives)
# Higher = more strict (more false negatives)
```

### Adjust GPS Location Validation Radius

Edit `backend/app/api/v1/attendance.py`:

```python
LOCATION_VALIDATION_RADIUS_METERS = 10.0  # 10 meters default
```

### Database Configuration

Edit `backend/app/core/config.py` or set environment variables:

```python
DATABASE_URL = "postgresql://user:password@localhost:5432/dbname"
REDIS_URL = "redis://localhost:6379"
```

### Enable/Disable Performance Monitoring

Performance monitoring is enabled by default. To disable:

Edit `backend/app/api/v1/attendance.py` and remove or comment out the `PerformanceMonitor` usage.

---

## 🐛 Troubleshooting

### Docker Containers Won't Start

**Symptoms:**
- `docker compose up` fails
- Containers exit immediately

**Solutions:**
1. Check Docker Desktop is running:
   ```powershell
   docker ps
   ```
2. Check ports are not in use:
   ```powershell
   netstat -ano | findstr :8000
   netstat -ano | findstr :5432
   ```
3. Stop conflicting services on those ports
4. Restart Docker Desktop
5. Try rebuilding:
   ```powershell
   cd infra
   docker compose down
   docker compose up --build -d
   ```

### Database Connection Error

**Symptoms:**
- `Error connecting to database`
- `Connection refused`

**Solutions:**
1. Wait 10-15 seconds after starting docker compose (PostgreSQL needs time to start)
2. Check PostgreSQL is healthy:
   ```powershell
   docker ps
   docker logs infra-postgres-1
   ```
3. Verify DATABASE_URL in `backend/app/core/config.py`
4. Check database is accessible:
   ```powershell
   docker exec -it infra-postgres-1 psql -U postgres -d attendance_db
   ```

### Models Not Downloading

**Symptoms:**
- `Model not found` errors
- Slow first check-in

**Solutions:**
1. Check internet connection
2. Models download on first use (5-10 minutes) - be patient
3. Check logs:
   ```powershell
   docker logs infra-backend-1 -f
   ```
4. Verify model directory exists:
   ```powershell
   docker exec -it infra-backend-1 ls -la /app/models/
   ```

### "No Face Detected" Error

**Symptoms:**
- Check-in fails with "No face detected"

**Solutions:**
1. Ensure image contains a clear, front-facing face
2. Check image format (JPG, PNG supported)
3. Try different lighting conditions
4. Ensure face is not too small in the image
5. Try different angle/position
6. Check image is not corrupted

### "Employee Not Recognized" Error

**Symptoms:**
- Check-in fails with "Employee not recognized"

**Solutions:**
1. Ensure employee face is registered first (see [Register an Employee Face](#register-an-employee-face))
2. Use multiple registration images (2-3 minimum, 5 recommended)
3. Check similarity threshold (may be too high):
   - Edit `backend/app/api/v1/attendance.py`
   - Lower `SIMILARITY_THRESHOLD` (try 0.5)
4. Ensure registration images are clear and similar to check-in image
5. Check employee code matches

### Out of Memory Errors

**Symptoms:**
- `CUDA out of memory`
- `MemoryError`
- System becomes slow

**Solutions:**
1. AI models require 8GB+ RAM - close other applications
2. If using GPU, reduce batch size or use CPU mode
3. Check Docker memory limit:
   - Docker Desktop → Settings → Resources → Memory
   - Increase to 8GB+ if available
4. Restart Docker containers:
   ```powershell
   cd infra
   docker compose restart
   ```

### Frontend Proxy Errors

**Symptoms:**
- `Proxy error: Could not proxy request`
- Frontend can't connect to backend

**Solutions:**
1. Ensure backend is running:
   ```powershell
   docker ps
   ```
2. Check backend is accessible:
   - Open http://localhost:8000/docs in browser
3. Verify frontend proxy configuration in `frontend/kiosk_ui/package.json`:
   ```json
   "proxy": "http://localhost:8000"
   ```
4. Restart frontend:
   ```powershell
   # Stop (Ctrl+C) and restart
   npm start
   ```

### Performance Issues

**Symptoms:**
- Slow check-in (takes > 5 seconds)
- High CPU usage

**Solutions:**
1. Check performance metrics in API response
2. Use GPU if available (faster inference)
3. Reduce image size (if uploading large images)
4. Check system resources:
   ```powershell
   docker stats
   ```

---

## 📝 Quick Command Reference

### Docker Commands

```powershell
# Start all services
cd infra
docker compose up -d

# Stop all services
docker compose down

# View logs
docker logs infra-backend-1 -f
docker logs infra-postgres-1 -f

# Restart services
docker compose restart

# Rebuild and start
docker compose up --build -d

# View running containers
docker ps

# Stop and remove all containers
docker compose down -v
```

### Database Commands

```powershell
# Initialize database (first time only)
$env:PYTHONPATH="D:\Intro-To-A.I-PRoject\backend"
python scripts/init_db.py

# Import sample data (first time only)
python scripts/import_sample_data.py

# Create employee
python scripts/create_employee.py --emp_code E003 --name "John Doe" --role "Manager"

# Create store
python scripts/create_store.py --name "Store" --address "Address" --camera_name "Cam1" --location "Loc"
```

### Frontend Commands

```powershell
# Install dependencies (first time only)
cd frontend/kiosk_ui
npm install

# Start development server
npm start

# Build for production
npm run build
```

---

## ✅ Verification Checklist

After setup, verify everything is working:

### Backend Services
- [ ] Docker containers running (`docker ps` shows 4 containers)
- [ ] Backend accessible at http://localhost:8000/docs
- [ ] Health endpoint returns `{"status": "ok"}`
- [ ] Database initialized (no errors in logs)
- [ ] Sample data imported (employees exist)

### Database
- [ ] Database tables created (check via API or logs)
- [ ] Sample employees exist (E001, E002, etc.)
- [ ] Store and camera created (check via API)

### AI Models
- [ ] Models downloaded (check backend logs)
- [ ] Face detection working (test via API)
- [ ] Face recognition working (register and check-in)

### Frontend (Optional)
- [ ] Frontend starts without errors
- [ ] Can access http://localhost:3001
- [ ] Camera access works (if using webcam)
- [ ] Check-in button works

### End-to-End Test
1. [ ] Register employee face via API
2. [ ] Check-in with registered employee via API
3. [ ] View attendance dashboard
4. [ ] Verify performance metrics in response

---

## 📚 Additional Documentation

- **[README.md](README.md)** - Project overview and quick start
- **[PROJECT_NOTES.md](PROJECT_NOTES.md)** - Implementation details and progress tracker
- **[docs/IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)** - Technical details about AI implementation
- **[docs/architecture.md](docs/architecture.md)** - System architecture documentation
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development guidelines
- **[scripts/README.md](scripts/README.md)** - Utility scripts documentation

---

## 🎉 Next Steps

After completing setup:

1. **Register Employees**: Use the API or frontend to register employee faces
2. **Test Check-in**: Try checking in with a registered employee
3. **View Dashboard**: Check attendance reports and analytics
4. **Configure Settings**: Adjust thresholds and settings as needed
5. **Deploy**: Follow deployment guide for production setup

**That's it!** Your AI Attendance System is ready to use! 🚀

---

**Need Help?** Check the [Troubleshooting](#-troubleshooting) section or review the logs:
```powershell
docker logs infra-backend-1 -f
```
