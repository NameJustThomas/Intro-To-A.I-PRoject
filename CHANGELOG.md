# Changelog

All notable changes to the AI Attendance System project will be documented in this file.

## [1.0.0] - 2025-12-04

### Added
- Initial project scaffold implementation
- Complete repository structure following scaffold specifications
- FastAPI backend with all core endpoints:
  - Employee face registration endpoint
  - Attendance check-in endpoint
  - Monthly attendance dashboard endpoint
  - Camera management endpoints
  - Environment logging endpoints
- Database schema with all required tables
- Docker Compose configuration for local development
- OpenAPI 3.0.3 specification
- React dashboard skeleton
- Unit tests for health and employee registration
- Database migration scripts
- Sample data import scripts
- CI/CD pipeline with GitHub Actions
- Pre-commit hooks for code quality
- Comprehensive documentation:
  - README with quickstart
  - CONTRIBUTING guidelines
  - Architecture documentation
  - Setup guide
  - Scripts documentation

### Enhanced (Post-Initial)
- Camera endpoints with full CRUD operations
- Environment endpoints with filtering and creation
- Logging configuration module
- Helper scripts for data management:
  - `create_employee.py`
  - `create_store.py`
- Makefile for common development tasks
- Improved error handling and validation

### Technical Details
- Python 3.11
- FastAPI 0.104.1
- PostgreSQL 14
- Redis 6
- SQLAlchemy 2.0.23
- React 18.2.0
- Docker & Docker Compose

### Notes
- AI modules are implemented as stubs ready for real model integration
- Face images are not stored raw in database (only embeddings)
- All secrets use environment variables
- Code follows black, isort, and flake8 standards

## [1.1.0] - 2025-12-11

### Added
- Complete project setup and verification
- Unified setup documentation (`SETUP.md`)
- Quick start guide in README
- **Kiosk UI component** (`frontend/kiosk_ui/`)
  - Camera capture for face recognition check-in
  - Photo upload functionality
  - Real-time check-in status feedback
  - Touch-friendly interface for kiosk devices
  - Integration with attendance check-in API

### Changed
- Consolidated documentation files (reduced from 12 to 9 .md files)
- Moved `IMPLEMENTATION_SUMMARY.md` to `docs/` folder
- Updated README with streamlined quick start instructions

### Removed
- Redundant documentation files:
  - `QUICK_START.md` (merged into README)
  - `SETUP_GUIDE.md` (merged into SETUP.md)
  - `HOW_TO_RUN.md` (merged into SETUP.md)
  - `DOCUMENTATION_GUIDE.md` (no longer needed)

### Verified
- All Docker services running correctly
- Database initialized with migrations
- Sample data imported successfully
- Test store and camera created
- Backend API accessible and functional

