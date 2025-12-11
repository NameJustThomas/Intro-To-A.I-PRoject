# Setup Guide - AI Attendance System

Complete guide for first-time setup and running the AI Attendance System.

## 📋 What This Project Does

AI-powered employee attendance system for takeaway coffee shops using:
- **Face Recognition** to identify employees when they check in
- **YOLO11** for face detection and people counting
- **InsightFace** for face embedding extraction and recognition
- **Real-time attendance tracking** with location (camera) and timestamp

### Key Features
- ✅ Employee face registration with multiple images
- ✅ Face recognition-based check-in
- ✅ Attendance logging with confidence scores
- ✅ Monthly attendance dashboard
- ✅ Camera-based location tracking

---

## 📦 Prerequisites

Before starting, ensure you have:
- ✅ **Docker Desktop** installed and running
- ✅ **Docker Compose** (included with Docker Desktop)
- ✅ **Python 3.11+** (for running scripts locally)
- ✅ **At least 8GB RAM** (AI models require memory)
- ✅ **Internet connection** (for downloading models on first run)

---

## 🚀 First-Time Setup

### Step 1: Verify Docker is Running

1. Open **Docker Desktop**
2. Wait until it shows "Docker Desktop is running"
3. Verify in terminal:
   ```powershell
   docker --version
   docker compose version
   ```

### Step 2: Navigate to Project Directory

```powershell
cd D:\Intro-To-A.I-PRoject
```

### Step 3: Start All Services

```powershell
cd infra
docker compose up --build -d
```

**What this does:**
- Builds the backend Docker image with all dependencies
- Starts PostgreSQL database
- Starts Redis cache
- Starts FastAPI backend
- Starts nginx reverse proxy

**Expected output:**
- Services will be running on:
  - Backend: http://localhost:8000
  - PostgreSQL: localhost:5432
  - Redis: localhost:6379
  - Nginx: http://localhost:80

**Note:** The `-d` flag runs services in the background. Models will download automatically on first use (5-10 minutes).

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

### Step 5: Import Sample Data (Optional but Recommended)

```powershell
python scripts/import_sample_data.py
```

**Expected output:**
```
Importing employees...
Added employee: E001 - Nguyen Van A
Added employee: E002 - Tran Thi B
Sample data import completed!
```

### Step 6: Create a Store and Camera

```powershell
python scripts/create_store.py --name "Main Store" --address "123 Main St" --camera_name "Camera 1" --location "Entrance"
```

**Note the Camera ID** - you'll need it for check-in!

### Step 7: Verify Everything is Running

1. Open browser: **http://localhost:8000/docs**
2. You should see the **FastAPI Swagger UI**
3. Test health endpoint: `GET /health` should return `{"status": "ok"}`

---

## 🎯 Using the System

### Register an Employee Face

**Using Swagger UI:**
1. Go to http://localhost:8000/docs
2. Find `POST /api/v1/employee/register-face`
3. Enter `employee_id`: `E001`
4. Upload 2-3 face images
5. Click "Execute"

**Tips:**
- Use clear, front-facing photos
- Good lighting
- Multiple angles improve accuracy

### Check In Using Face Recognition

**Using Swagger UI:**
1. Go to http://localhost:8000/docs
2. Find `POST /api/v1/attendance/check-in`
3. Enter `camera_id`: `1`
4. Upload a face image
5. Click "Execute"

### View Attendance Dashboard

Visit: http://localhost:8000/docs → `GET /api/v1/dashboard/attendance-month`

---

## 🔄 Subsequent Runs (Quick Start)

After initial setup, you only need:

```powershell
cd D:\Intro-To-A.I-PRoject\infra
docker compose up -d
```

Wait 10-15 seconds, then access: http://localhost:8000/docs

**You DON'T need to:**
- ❌ Re-initialize database
- ❌ Re-import sample data
- ❌ Re-create store/camera

---

## 🔧 Configuration

### Adjust Face Recognition Threshold

Edit `backend/app/api/v1/attendance.py`:
```python
SIMILARITY_THRESHOLD = 0.6  # 0.5-0.8 recommended
```

### Database Configuration

Edit `backend/app/core/config.py` or set environment variables.

---

## 🐛 Troubleshooting

### Docker containers won't start
- Check Docker Desktop is running
- Check ports are not in use: `netstat -ano | findstr :8000`

### Database connection error
- Wait 10-15 seconds after starting docker compose
- Check PostgreSQL is healthy: `docker ps`

### Models not downloading
- Check internet connection
- Models download on first use (5-10 minutes)
- Check logs: `docker logs infra-backend-1`

### "No face detected"
- Ensure image contains a clear face
- Check image format (JPG, PNG supported)
- Try different lighting/angle

### "Employee not recognized"
- Ensure employee face is registered first
- Use multiple registration images (2-3 minimum)
- Check similarity threshold (may be too high)

### Out of memory errors
- AI models require 8GB+ RAM
- Close other applications

---

## 📝 Quick Command Reference

```powershell
# Start services
cd infra
docker compose up -d

# Stop services
docker compose down

# View logs
docker logs infra-backend-1 -f

# Initialize database (first time only)
$env:PYTHONPATH="D:\Intro-To-A.I-PRoject\backend"
python scripts/init_db.py

# Import sample data (first time only)
python scripts/import_sample_data.py

# Create store (first time only)
python scripts/create_store.py --name "Store" --address "Address" --camera_name "Cam1" --location "Loc"
```

---

## ✅ Verification Checklist

After setup, verify:
- [ ] Docker containers running (`docker ps` shows 4 containers)
- [ ] Backend accessible at http://localhost:8000/docs
- [ ] Health endpoint returns `{"status": "ok"}`
- [ ] Database initialized (no errors)
- [ ] Sample data imported
- [ ] Store and camera created

---

## 📚 Additional Documentation

- **[README.md](README.md)** - Project overview and quick start
- **[PROJECT_NOTES.md](PROJECT_NOTES.md)** - Implementation details
- **[docs/IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)** - Technical AI details
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development guidelines

---

**That's it!** Your AI Attendance System is ready to use! 🎉

