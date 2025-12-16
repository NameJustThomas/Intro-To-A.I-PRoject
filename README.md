# AI Attendance System

AI-powered employee attendance system for takeaway coffee shops using face recognition, anti-spoofing detection, and GPS location verification.

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [AI Models](#-ai-models)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Development Setup](#-development-setup)
- [API Documentation](#-api-documentation)
- [Performance Monitoring](#-performance-monitoring)
- [Security Features](#-security-features)
- [Documentation](#-documentation)
- [Contributing](#-contributing)

## ✨ Features

### Core Functionality
- ✅ **Face Recognition Check-in**: Automated employee identification using AI
- ✅ **Anti-Spoofing Detection**: Prevents photo/video attacks using MiniFASNet
- ✅ **GPS Location Verification**: Ensures employees are at the correct store location
- ✅ **Real-time Performance Monitoring**: Automatic latency, memory, and CPU tracking
- ✅ **Late Detection**: Automatic late check-in detection with 15-minute grace period
- ✅ **Multi-Store Support**: Location-based validation for multiple store locations

### Management Features
- 📊 **Attendance Dashboard**: Monthly attendance reports with analytics
- 👥 **Employee Management**: Face registration with multiple images
- 📅 **Shift Scheduling**: Automated schedule-based attendance tracking
- 📷 **Camera Management**: Multi-camera support with RTSP streaming
- 🌍 **Environment Monitoring**: People counting and brightness tracking

### Technical Features
- 🔒 **Privacy-Preserving**: Stores only face embeddings, not raw images
- ⚡ **High Performance**: ~1 second end-to-end check-in time
- 📈 **Performance Metrics**: Detailed metrics for each pipeline step
- 🐳 **Dockerized**: Complete containerization with Docker Compose
- 🔄 **Auto-reload**: Hot reload for development

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL 14 with SQLAlchemy 2.0.30+
- **Cache**: Redis 6
- **ORM**: SQLAlchemy 2.0+
- **Validation**: Pydantic 2.5+

### Frontend
- **Framework**: React 18.2.0
- **Routing**: React Router DOM 7.10.1
- **HTTP Client**: Axios 1.6.0
- **Build Tool**: Create React App

### AI/ML
- **Face Detection**: YOLO-face (yolov11m-face.pt)
- **Face Recognition**: InsightFace (buffalo_l, 512-dim embeddings)
- **Anti-Spoofing**: MiniFASNet (multi-model fusion)
- **People Counting**: YOLO11s
- **Deep Learning**: PyTorch 2.0+, ONNX Runtime
- **Image Processing**: OpenCV 4.8+

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx
- **Process Manager**: Uvicorn (ASGI server)

## 🤖 AI Models

### 1. YOLO-face (Face Detection)
- **Model**: yolov11m-face.pt
- **Purpose**: Detect faces in images
- **Output**: Bounding boxes with confidence scores
- **Performance**: ~100-200ms (CPU), ~15-30ms (GPU)

### 2. InsightFace (Face Recognition)
- **Model**: buffalo_l
- **Purpose**: Extract 512-dimensional face embeddings
- **Output**: Normalized embedding vectors
- **Performance**: ~50-100ms per face
- **Similarity**: Cosine similarity (threshold ≥ 0.6)

### 3. MiniFASNet (Anti-Spoofing)
- **Models**: MiniFASNetV1SE + MiniFASNetV2
- **Purpose**: Detect live faces vs photos/videos
- **Method**: Multi-scale + multi-model fusion
- **Output**: True (live) / False (spoof)
- **Performance**: ~80-150ms per face

### 4. YOLO11 (People Counting)
- **Model**: yolo11s.pt
- **Purpose**: Count people in environment images
- **Output**: Integer count
- **Performance**: ~80-150ms (CPU), ~15-30ms (GPU)

## 🚀 Quick Start

### Prerequisites

- ✅ **Docker Desktop** installed and running
- ✅ **Node.js 16+** and npm (for frontend)
- ✅ **Python 3.11+** (for running scripts)
- ✅ **At least 8GB RAM** (AI models require memory)
- ✅ **Internet connection** (for downloading models on first run)

### First Time Setup

See **[SETUP.md](SETUP.md)** for complete first-time setup instructions including:
- Database initialization
- Sample data import
- Model download
- Configuration

### Running the Application

**1. Start Docker Services (Backend, Database, Redis):**
```powershell
cd infra
docker compose up -d
```

Wait 10-15 seconds for services to start. Models will download automatically on first use (5-10 minutes).

**2. Start Frontend (Kiosk UI):**
```powershell
cd frontend/kiosk_ui
npm install  # Only needed first time
npm start
```

The frontend will open at **http://localhost:3001**

**3. Access the Application:**
- **Check-in Page (Kiosk UI)**: http://localhost:3001
- **Dashboard**: http://localhost:3001/dashboard (after check-in)
- **Backend API Docs**: http://localhost:8000/docs
- **Backend Health Check**: http://localhost:8000/health

**4. Stop Services:**
```powershell
# Stop frontend: Press Ctrl+C in the terminal running npm start

# Stop Docker services:
cd infra
docker compose down
```

## 📁 Project Structure

```
ai-attendance/
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── ai/                 # AI/ML modules
│   │   │   ├── face_recog.py   # Face detection & recognition
│   │   │   ├── anti_spoof.py   # Anti-spoofing detection
│   │   │   ├── people_count.py # People counting
│   │   │   └── ...
│   │   ├── api/v1/             # API endpoints
│   │   │   ├── attendance.py   # Check-in endpoint
│   │   │   ├── employees.py    # Employee management
│   │   │   ├── dashboard.py    # Attendance reports
│   │   │   └── ...
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic validation schemas
│   │   ├── utils/              # Utilities (performance monitoring)
│   │   └── main.py             # FastAPI application entry
│   ├── models/                 # AI model files (binary)
│   │   ├── yolo-face/          # YOLO-face model weights
│   │   └── silent-face-anti-spoofing/  # MiniFASNet models
│   ├── tests/                  # Unit tests
│   ├── Dockerfile              # Backend container definition
│   └── requirements.txt        # Python dependencies
├── frontend/                   # React applications
│   ├── dashboard/              # Attendance reports dashboard
│   └── kiosk_ui/               # Employee check-in kiosk interface
├── infra/                      # Infrastructure configuration
│   ├── docker-compose.yml      # Docker Compose configuration
│   ├── migrations/             # Database migration scripts
│   └── nginx/                  # Nginx configuration
├── scripts/                    # Utility scripts
│   ├── performance/           # Performance testing scripts
│   ├── init_db.py             # Database initialization
│   └── import_sample_data.py  # Sample data import
├── docs/                       # Documentation
│   ├── architecture.md        # System architecture
│   ├── IMPLEMENTATION_SUMMARY.md  # AI implementation details
│   └── openapi.yaml           # OpenAPI specification
└── README.md                   # This file
```

## 💻 Development Setup

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at http://localhost:8000

### Frontend Development

**Kiosk UI (Check-in):**
```bash
cd frontend/kiosk_ui
npm install
npm start
```

**Dashboard (Reports):**
```bash
cd frontend/dashboard
npm install
npm start
```

### Running Tests

```bash
cd backend
pytest
```

## 📡 API Documentation

### Main Endpoints

- **POST** `/api/v1/attendance/check-in` - Employee check-in with face recognition
- **POST** `/api/v1/employee/register-face` - Register employee face with multiple images
- **GET** `/api/v1/dashboard/attendance-month` - Get monthly attendance summary
- **GET** `/api/v1/cameras` - List all cameras
- **POST** `/api/v1/environment/logs` - Create environment log (people count, brightness)

### Interactive API Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📊 Performance Monitoring

The system automatically measures and returns performance metrics for each check-in:

- **Latency**: Image upload, face detection, anti-spoofing, face recognition, database operations
- **Memory Usage**: RAM, GPU (if available), per-model memory
- **CPU Usage**: Average CPU percentage during processing
- **Throughput**: Number of embeddings searched, total processing time

Metrics are:
- Logged to backend console
- Returned in API response
- Displayed in frontend UI
- Available even when errors occur (for debugging)

See `scripts/performance/` for standalone performance testing scripts.

## 🔒 Security Features

### Privacy Protection
- ✅ **No Raw Images Stored**: Only 512-dimensional face embeddings stored in database
- ✅ **Embeddings Cannot Be Reverse-Engineered**: Mathematical vectors, not images
- ✅ **Compliance**: Meets privacy regulations (GDPR-ready)

### Anti-Spoofing
- ✅ **Multi-Model Fusion**: Combines multiple MiniFASNet models for accuracy
- ✅ **Multi-Scale Analysis**: Detects spoofing at different scales
- ✅ **Live Face Detection**: Prevents photo/video attacks

### Location Verification
- ✅ **GPS Validation**: Ensures employees are at correct store location
- ✅ **Distance Calculation**: Haversine formula for accurate distance measurement
- ✅ **10-Meter Radius**: Configurable validation radius

### Access Control
- ✅ **Single-Person Validation**: Only allows check-in with exactly 1 face
- ✅ **Confidence Threshold**: Configurable similarity threshold (default: 0.6)
- ✅ **Error Handling**: Comprehensive error handling with performance metrics

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Complete setup and usage guide (start here for first-time setup)
- **[PROJECT_NOTES.md](PROJECT_NOTES.md)** - Implementation details and progress tracker
- **[docs/IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)** - Technical details about AI implementation
- **[docs/architecture.md](docs/architecture.md)** - System architecture documentation
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development guidelines
- **[ai_attendance_for_cafe_project_scaffold.md](ai_attendance_for_cafe_project_scaffold.md)** - Original project requirements

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines, code style, and contribution process.

## 📝 License

[To be added]

---

**Built with ❤️ using FastAPI, React, and state-of-the-art AI models**
