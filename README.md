# AI Attendance System

AI Attendance System + Environment Recognition for Cafe Takeaway

## Quick Start

1. **Install Docker & Docker Compose**
2. **Start services:**
   ```bash
   cd infra
   docker compose up --build
   ```
3. **Initialize database** (in new terminal):
   ```bash
   python scripts/init_db.py
   python scripts/import_sample_data.py
   ```
4. **Access:**
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - OpenAPI Spec: http://localhost:8000/openapi.json

## Project Structure

```
ai-attendance/
├── backend/          # FastAPI backend application
├── frontend/         # React dashboard and kiosk UI
├── mobile/           # Flutter mobile app
├── infra/            # Docker compose and nginx config
├── docs/             # OpenAPI spec and architecture docs
└── scripts/          # Utility scripts and sample data
```

## Development Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend/dashboard
npm install
npm start
```

### Testing
```bash
cd backend
pytest
```

## Important Files

- **`PROJECT_NOTES.md`** - ⚠️ **ALWAYS READ THIS FIRST** when continuing work
- **`ai_attendance_for_cafe_project_scaffold.md`** - Original requirements
- **`CONTRIBUTING.md`** - Development guidelines
- **`DOCUMENTATION_GUIDE.md`** - Guide to all documentation files

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

[To be added]

