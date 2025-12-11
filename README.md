# AI Attendance System

AI-powered employee attendance system for takeaway coffee shops using face recognition.

## 🚀 Quick Start

### Subsequent Runs (Already Set Up)

If you've already set up the project:

```powershell
cd infra
docker compose up -d
```

Wait 10-15 seconds, then access: **http://localhost:8000/docs**

### First Time Setup

See **[SETUP.md](SETUP.md)** for complete first-time setup instructions.

## Project Structure

```
ai-attendance/
├── backend/          # FastAPI backend application
├── frontend/         # React applications
│   ├── dashboard/    # Attendance reports dashboard
│   └── kiosk_ui/     # Employee check-in kiosk interface
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

**Dashboard (Reports):**
```bash
cd frontend/dashboard
npm install
npm start
```

**Kiosk UI (Check-in):**
```bash
cd frontend/kiosk_ui
npm install
npm start
```

### Testing
```bash
cd backend
pytest
```

## Documentation

- **[SETUP.md](SETUP.md)** - Complete setup and usage guide (start here for first-time setup)
- **[PROJECT_NOTES.md](PROJECT_NOTES.md)** - Implementation details and progress tracker
- **[docs/IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)** - Technical details about AI implementation
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development guidelines
- **[ai_attendance_for_cafe_project_scaffold.md](ai_attendance_for_cafe_project_scaffold.md)** - Original project requirements

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

[To be added]

