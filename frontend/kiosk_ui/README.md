# AI Attendance Kiosk UI

Touch-friendly React application for employee face recognition check-in at cafe kiosk devices.

## Features

- 📷 **Camera Capture**: Real-time camera access for face recognition
- 📤 **Photo Upload**: Alternative check-in via photo upload
- ✅ **Real-time Feedback**: Instant check-in status and results
- 🎯 **Touch-friendly**: Optimized for kiosk touchscreen devices
- 🔄 **API Integration**: Connects to `/api/v1/attendance/check-in` endpoint

## Setup

```bash
cd frontend/kiosk_ui
npm install
npm start
```

The kiosk UI will run on http://localhost:3001 (or next available port).

## Usage

1. **Enter Camera ID**: Input the camera ID for the location (default: 1)
2. **Start Camera**: Click "Start Camera" to enable webcam
3. **Check In**: 
   - Click "Check In with Camera" to capture and check in
   - OR click "Upload Photo to Check In" to upload an image file
4. **View Results**: Check-in status and employee details will be displayed

## Requirements

- Backend API running on http://localhost:8000
- Camera ID must exist in the database
- Employee faces must be registered via `/api/v1/employee/register-face`

## API Integration

The kiosk UI calls:
- `GET /api/v1/cameras` - Fetch available cameras
- `POST /api/v1/attendance/check-in` - Submit check-in with face image

## Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari (with camera permissions)

## Production Build

```bash
npm run build
```

Build output will be in the `build/` directory, ready for deployment to a kiosk device.

