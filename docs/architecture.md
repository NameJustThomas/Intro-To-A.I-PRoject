# Architecture Documentation

## System Overview

The AI Attendance System is designed to provide automated attendance tracking using face recognition technology for cafe takeaway environments.

## Architecture Components

### Backend (FastAPI)
- **Framework**: FastAPI
- **Database**: PostgreSQL 14
- **Cache**: Redis 6
- **ORM**: SQLAlchemy
- **API Versioning**: v1

### Frontend
- **Dashboard**: React application for viewing attendance reports
- **Kiosk UI**: React application for on-site attendance kiosk

### Mobile
- **Flutter App**: Mobile application for employee management

### Infrastructure
- **Docker Compose**: Container orchestration
- **Nginx**: Reverse proxy and load balancer

## Database Schema

### Core Tables
- `stores`: Store/location information
- `cameras`: Camera configuration and RTSP URLs
- `employees`: Employee information
- `face_embeddings`: Face recognition embeddings (not raw images)
- `schedules`: Employee shift schedules
- `attendance_logs`: Attendance check-in records
- `environment_logs`: Environment monitoring data (people count, brightness)

## API Design

### Endpoints
1. **POST /api/v1/employee/register-face**: Register employee face with multiple images
2. **POST /api/v1/attendance/check-in**: Check in using face recognition
3. **GET /api/v1/dashboard/attendance-month**: Get monthly attendance summary

## AI Modules

### Face Recognition
- Face detection
- Face alignment
- Embedding extraction
- Similarity matching

### People Counting
- Person detection using YOLO or MobileNet-SSD
- Count tracking

### Anti-Spoofing
- Liveness detection
- Spoof prevention

## Security Considerations

1. **Face Images**: Not stored raw in database, only embeddings
2. **Secrets**: All secrets via environment variables
3. **Authentication**: JWT-based authentication (to be implemented)
4. **Data Encryption**: Snapshots optionally encrypted

## Deployment

### Local Development
```bash
cd infra
docker compose up --build
```

### Production
- Use environment variables for all configuration
- Enable HTTPS
- Use strong secret keys
- Implement proper authentication and authorization

## Future Enhancements

- Real-time face recognition from camera streams
- Advanced anti-spoofing
- Mobile app integration
- Real-time dashboard updates
- Multi-store support with proper access control

