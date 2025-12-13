# AI Attendance Project - Implementation Notes & Progress Tracker

**IMPORTANT: Always read this file before continuing work on the project!**

## Project Overview
- **Project Name:** AI Attendance System + Environment Recognition for Cafe Takeaway
- **Goal:** End-to-end scaffold with OpenAPI spec, docker-compose, repo skeleton, DB migrations, sample data, CI checklist, and task list
- **Reference Document:** `ai_attendance_for_cafe_project_scaffold.md`

## Key Constraints & Requirements
1. **Face images NOT stored raw in DB** - store embeddings and optionally encrypted snapshots
2. **Use environment variables for secrets** - never hardcode credentials
3. **All changes via PR** - DO NOT push directly to main
4. **Code quality:** Use pre-commit (black, isort, flake8), EditorConfig
5. **Testing:** Minimal unit tests for health endpoint + register-face flow
6. **Migrations:** Must create migration files and commit them

## Project Structure
```
ai-attendance/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── attendance.py
│   │   │       ├── cameras.py
│   │   │       ├── dashboard.py
│   │   │       ├── employees.py
│   │   │       ├── environment.py
│   │   │       ├── schedules.py
│   │   │       └── stores.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logging_config.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   └── orm_models.py  # SQLAlchemy ORM models
│   │   ├── db/
│   │   │   └── base.py
│   │   ├── ai/
│   │   │   ├── face_recog.py
│   │   │   ├── anti_spoof.py
│   │   │   ├── people_count.py
│   │   │   ├── minifasnet.py
│   │   │   ├── anti_spoof_utils.py
│   │   │   ├── generate_patches.py
│   │   │   └── transform.py
│   │   └── schemas/
│   │       ├── attendance.py
│   │       └── employee.py
│   ├── models/  # AI model files (binary data)
│   │   ├── yolo-face/
│   │   │   └── weights/
│   │   │       └── yolov11m-face.pt  # 38.6 MB
│   │   └── silent-face-anti-spoofing/
│   │       └── model/
│   │           ├── 2.7_80x80_MiniFASNetV2.pth  # 1.76 MB
│   │           └── 4_0_0_80x80_MiniFASNetV1SE.pth  # 1.77 MB
│   ├── tests/
│   │   ├── test_health.py
│   │   └── test_employee_register.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pytest.ini
│   └── yolo11n.pt  # Fallback model (5.35 MB, can be removed)
├── frontend/
│   ├── dashboard/
│   │   ├── src/
│   │   │   ├── App.js
│   │   │   └── index.js
│   │   └── package.json
│   └── kiosk_ui/
│       ├── src/
│       │   ├── App.js
│       │   ├── Dashboard.js
│       │   └── index.js
│       └── package.json
├── infra/
│   ├── docker-compose.yml
│   ├── migrations/
│   │   ├── 001_init.sql
│   │   ├── 002_add_location_fields.sql
│   │   └── 003_fix_is_on_time_type.sql
│   └── nginx/
│       └── nginx.conf
├── docs/
│   ├── openapi.yaml
│   ├── architecture.md
│   └── IMPLEMENTATION_SUMMARY.md
├── scripts/
│   ├── init_db.py
│   ├── import_sample_data.py
│   ├── create_employee.py
│   ├── create_store.py
│   ├── README.md
│   └── sample_data/
│       ├── employees.csv
│       └── schedules.csv
├── README.md
├── SETUP.md
├── PROJECT_NOTES.md
├── CONTRIBUTING.md
├── Makefile
└── ai_attendance_for_cafe_project_scaffold.md
```

**Note:** Two "models" directories exist:
- `backend/app/models/` = ORM models (Python code) - SQLAlchemy models
- `backend/models/` = AI model files (binary data) - Pre-trained model weights
These serve different purposes and are intentional.

## Database Schema
- stores (id, name, address)
- cameras (id, store_id, name, rtsp_url, location)
- employees (id, emp_code, name, role, created_at) - role can be NULL
- face_embeddings (id, employee_id, embedding, created_at)
- schedules (id, employee_id, date, shift_start, shift_end)
- attendance_logs (id, employee_id, timestamp, camera_id, confidence, snapshot_url)
- environment_logs (id, camera_id, timestamp, people_count, brightness)

## API Endpoints
1. POST `/api/v1/employee/register-face` - Register employee face
2. POST `/api/v1/attendance/check-in` - Check in image/frame (with anti-spoofing)
3. GET `/api/v1/dashboard/attendance-month` - Get monthly attendance summary
4. GET `/api/v1/cameras` - List cameras (with filtering)
5. GET `/api/v1/cameras/{id}` - Get camera details
6. GET `/api/v1/environment/logs` - Get environment logs (with filtering)
7. POST `/api/v1/environment/logs` - Create environment log

## AI Modules (All Implemented)
- `face_recog.py`: ✅ detect_faces(), align_face(), get_embedding() - Using YOLO-face + InsightFace
- `people_count.py`: ✅ count_people() - Using YOLO11s
- `anti_spoof.py`: ✅ is_live() - Using MiniFASNet multi-model fusion

## Dependencies
- **Backend**: FastAPI 0.104.1, SQLAlchemy 2.0.23, psycopg[binary]>=3.1.0, uvicorn
- **Database**: PostgreSQL 14
- **Cache**: Redis 6
- **AI/ML**: 
  - torch>=2.0.0, torchvision>=0.15.0
  - ultralytics>=8.0.0
  - opencv-python>=4.8.0
  - insightface>=0.7.3
  - onnxruntime>=1.20.0
  - numpy>=1.24.3, pillow>=10.2.0
- **Frontend**: React 18.2.0, axios
- **Testing**: pytest 7.4.3, pytest-cov, httpx

## Implementation Details

### AI Modules Implementation

#### Face Recognition (`backend/app/ai/face_recog.py`)
- **Face Detection**: YOLO-face model (yolov11m-face.pt, 38.6 MB)
  - Located at: `backend/models/yolo-face/weights/yolov11m-face.pt`
  - Supports multiple variants (m, n, s, l, x) with priority order
  - Uses `Path(__file__)` for reliable path resolution
  - Falls back to generic yolo11n.pt if face-specific model not found
- **Face Recognition**: InsightFace (buffalo_l model)
  - 512-dimensional face embeddings
  - Auto-downloads model to `~/.insightface/models/buffalo_l/`
  - Lazy loading on first use
- **Functions**:
  - `detect_faces(image)` - Detects faces using YOLO-face
  - `align_face(bbox, image)` - Aligns and crops face with padding
  - `get_embedding(face_img)` - Extracts 512-dim embedding using InsightFace
  - `get_face_embedding_from_image(image_bytes)` - End-to-end processing

#### Anti-Spoofing (`backend/app/ai/anti_spoof.py`)
- **Model**: MiniFASNet architecture from Silent-Face-Anti-Spoofing
- **Models**: 
  - `2.7_80x80_MiniFASNetV2.pth` (1.76 MB)
  - `4_0_0_80x80_MiniFASNetV1SE.pth` (1.77 MB)
  - Located at: `backend/models/silent-face-anti-spoofing/model/`
- **Approach**: Multi-model fusion with multi-scale patch generation
- **Supporting Modules**:
  - `minifasnet.py` - MiniFASNet architecture (V1, V2, V1SE, V2SE variants)
  - `anti_spoof_utils.py` - Utilities (get_kernel, parse_model_name)
  - `generate_patches.py` - CropImage class for multi-scale patches
  - `transform.py` - Image transformations (Compose, ToTensor)
- **Function**: `is_live(face_img, bbox, threshold=0.5)` - Returns True if live face, False if spoof
- **Path Resolution**: Uses `Path(__file__)` for reliability

#### People Counting (`backend/app/ai/people_count.py`)
- **Model**: YOLO11s for person detection
- **Function**: `count_people(image)` - Returns number of people detected
- Auto-downloads model via ultralytics

### Backend API Implementation

#### Check-in Endpoint (`backend/app/api/v1/attendance.py`)
- **Anti-Spoofing Integration**: 
  - Calls `is_live()` before face recognition
  - Returns 403 Forbidden if spoofing detected
  - Error message: "Face spoofing detected. Please use a live face for check-in."
- **Single-Person Validation**:
  - Validates exactly 1 face detected
  - Returns 400 Bad Request if multiple faces detected
  - Error message: "Multiple faces detected (X faces). Please ensure only one person is in the image for check-in."
- **Face Recognition**: 
  - Uses YOLO-face for detection
  - Uses InsightFace for embedding extraction
  - Cosine similarity matching with threshold 0.6
- **Location Validation**: 
  - Uses Haversine formula to calculate distance
  - Minimum distance from store: 30 meters

#### Employee Endpoint (`backend/app/api/v1/employees.py`)
- **Face Registration**: 
  - Accepts multiple images
  - Uses real face recognition (YOLO-face + InsightFace)
  - Stores 512-dimensional embeddings in database
- **Schema**: 
  - `EmployeeCreateRequest.role` is `Optional[str] = None`
  - `EmployeeResponse.role` is `Optional[str] = None`

#### Dashboard Endpoint (`backend/app/api/v1/dashboard.py`)
- **Null Role Handling**: 
  - Explicitly sets `employee_role` to `None` if `log.employee.role` is null
  - Gracefully handles employees without roles

### Schema Changes

#### Employee Schema (`backend/app/schemas/employee.py`)
- `EmployeeBase.role` is `Optional[str] = None`
- `EmployeeCreate.role` is `Optional[str] = None`
- `EmployeeResponse.role` is `Optional[str] = None`

#### Attendance Schema (`backend/app/schemas/attendance.py`)
- `employee_role` field is `Optional[str]` to handle null values

### Frontend Implementation

#### Kiosk UI (`frontend/kiosk_ui/src/App.js`)
- **Camera ID**: 
  - Removed from UI (hidden from user)
  - Automatically set from first available camera in database
  - Fetched on component mount
- **Photo Upload**: 
  - Removed "Upload Photo to Check In" functionality
  - Only allows check-in via camera capture
  - Removed `handleFileUpload` function
- **UI Text**: 
  - All text translated to English
  - Status messages in English
  - Button labels in English
- **Error Messages**:
  - "Face not recognized" - Shows registration modal
  - "Detect user using picture" - Shows spoofing detection error (403)
  - Clear pop-up notifications for all error cases
- **Check-in Flow**:
  1. User starts camera
  2. User captures photo
  3. Photo sent to `/api/v1/attendance/check-in`
  4. Anti-spoofing check runs first
  5. Face recognition runs if anti-spoofing passes
  6. Success/error message displayed

#### Dashboard Component (`frontend/kiosk_ui/src/Dashboard.js`)
- **Null Role Handling**:
  - Displays "N/A" for null roles in employee list
  - Employee edit form defaults to "employee" if role is null
  - Store edit form handles null values

### Dependencies Updates

#### Python 3.13+ Compatibility
- `psycopg2-binary==2.9.9` → `psycopg[binary]>=3.1.0`
- `pillow==10.1.0` → `pillow>=10.2.0`
- `pydantic==2.5.0` → `pydantic>=2.5.0`
- `numpy==1.24.3` → `numpy>=1.24.3`

#### AI/ML Dependencies Added
- `torch>=2.0.0`
- `torchvision>=0.15.0`
- `ultralytics>=8.0.0`
- `opencv-python>=4.8.0`
- `insightface>=0.7.3`
- `onnxruntime>=1.20.0` (required by insightface)

#### Removed Dependencies
- `deepface` (not used)
- `tensorflow` (not used)
- `onnx` (not used)
- `ml_dtypes` (not used)

### Installation & Setup

#### InsightFace Installation
- Required Windows SDK 10.0.22621.0 for C++ compilation
- Set environment variables (INCLUDE, LIB) for compiler
- Successfully built and installed from source
- onnxruntime installed as dependency

### Path Resolution
- All AI modules use `Path(__file__)` for reliable path resolution
- Works from any working directory (backend/, project root, etc.)
- `face_recog.py`: Finds YOLO-face model correctly
- `anti_spoof.py`: Finds anti-spoofing models correctly

## Current Status
✅ **All Core Features Implemented**
- Face detection and recognition working
- Anti-spoofing detection working
- Single-person validation working
- People counting working
- All API endpoints functional
- Frontend UI complete with English text
- Null role handling implemented
- All dependencies installed and working

## Notes for Future Sessions
- **ALWAYS READ THIS FILE FIRST** before continuing work
- Review scaffold document (`ai_attendance_for_cafe_project_scaffold.md`) for requirements
- For quick start: See `README.md` → `cd infra && docker compose up -d`
- For detailed setup: See `SETUP.md`
- Model locations:
  - YOLO-face: `backend/models/yolo-face/weights/yolov11m-face.pt`
  - Anti-spoofing: `backend/models/silent-face-anti-spoofing/model/*.pth`
  - InsightFace: Auto-downloaded to `~/.insightface/models/buffalo_l/`
- All path resolutions use `Path(__file__)` for reliability
