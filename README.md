# AI Attendance System

AI-powered employee attendance system for takeaway coffee shops using face recognition.

## 🚀 Quick Start

### Next Time You Run the Project (Already Set Up)

If you've already completed the first-time setup:

**1. Start Docker Services (Backend, Database, Redis):**
```powershell
cd infra
docker compose up -d
```

Wait 10-15 seconds for services to start.

**2. Start Frontend (Kiosk UI + Dashboard):**
```powershell
cd frontend/kiosk_ui
npm start
```

The frontend will open at **http://localhost:3001**

**3. Access the Application:**
- **Check-in Page (Kiosk UI):** http://localhost:3001
- **Dashboard:** http://localhost:3001/dashboard (after check-in)
- **Backend API Docs:** http://localhost:8000/docs

**4. Stop Services (when done):**
```powershell
# Stop frontend: Press Ctrl+C in the terminal running npm start

# Stop Docker services:
cd infra
docker compose down
```

### First Time Setup

See **[SETUP.md](SETUP.md)** for complete first-time setup instructions (database initialization, sample data, etc.).

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

