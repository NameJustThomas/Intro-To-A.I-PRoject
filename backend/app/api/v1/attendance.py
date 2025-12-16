from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import time
from app.db.base import get_db
from app.schemas.attendance import CheckInResponse, CheckInHistoryItem, PerformanceMetricsResponse, CheckInErrorResponse, CheckInErrorResponse
from app.models.orm_models import Employee, AttendanceLog, Camera, FaceEmbedding, Store, Schedule
from app.ai.face_recog import get_face_embedding_from_image, align_face
from app.ai.anti_spoof import is_live
from app.utils.performance_monitor import PerformanceMonitor
import numpy as np
import cv2
import io
from PIL import Image
import math
from fastapi.responses import JSONResponse

router = APIRouter()

# Similarity threshold for face matching (cosine similarity)
SIMILARITY_THRESHOLD = 0.6  # Adjust based on your needs (0.6-0.7 is typical)
# Minimum distance from store to validate location (in meters)
MIN_DISTANCE_FROM_STORE = 30.0  # 10 meters


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two GPS coordinates using Haversine formula.
    Returns distance in meters.
    """
    if not all([lat1, lon1, lat2, lon2]):
        return None
    
    # Earth radius in meters
    R = 6371000
    
    # Convert to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


@router.post("/attendance/check-in", response_model=CheckInResponse)
async def check_in(
    camera_id: str = Form(...),
    image: UploadFile = File(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Check in using face recognition.
    Uses YOLO-face for detection and InsightFace for embedding extraction.
    Matches against stored employee embeddings using cosine similarity.
    
    Automatically measures and returns performance metrics for the check-in pipeline.
    """
    # Initialize performance monitor
    with PerformanceMonitor() as perf_monitor:
        try:
            # Verify camera exists
            camera = db.query(Camera).filter(Camera.id == int(camera_id)).first()
            if not camera:
                raise HTTPException(status_code=404, detail="Camera not found")

            # Read image and measure upload time
            with perf_monitor.measure('image_upload_ms'):
                image_bytes = await image.read()
                
                # Convert bytes to numpy array for anti-spoofing
                nparr = np.frombuffer(image_bytes, np.uint8)
                image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if image_bgr is None:
                    # Try PIL as fallback
                    image = Image.open(io.BytesIO(image_bytes))
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    image_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Detect faces and get embeddings using real AI models
            # Measure face detection and recognition separately for accuracy
            from app.ai.face_recog import detect_faces, get_embedding, align_face
            
            # Measure face detection time and memory
            with perf_monitor.measure('face_detection_ms', measure_memory=True):
                face_boxes = detect_faces(image_bytes)
            
            # Warn if face detection is too slow (likely model loading/downloading)
            if perf_monitor.metrics.face_detection_ms > 5000:  # > 5 seconds
                perf_monitor.metrics.slow_detection_warning = True
                print(f"⚠️  WARNING: Face detection took {perf_monitor.metrics.face_detection_ms:.2f}ms")
                print("   This is likely due to first-time model loading or downloading.")
                print("   Subsequent check-ins should be much faster (< 200ms).")
            
            if not face_boxes:
                raise HTTPException(status_code=404, detail="No face detected in image")
            
            # Set number of faces detected
            perf_monitor.metrics.num_faces_detected = len(face_boxes)
            
            # Validate: Only allow check-in with exactly 1 person
            if len(face_boxes) > 1:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Multiple faces detected ({len(face_boxes)} faces). Please ensure only one person is in the image for check-in."
                )

            # Extract face region for anti-spoofing check
            first_face_box = face_boxes[0]
            face_crop = align_face(first_face_box, image_bgr)
            
            # Measure face recognition (embedding extraction) time and memory
            with perf_monitor.measure('face_recognition_ms', measure_memory=True):
                face_embedding = get_embedding(face_crop)
            
            # Validate embedding
            if len(face_embedding) == 0 or np.all(face_embedding == 0):
                raise HTTPException(status_code=400, detail="Invalid face embedding extracted")
            
            embeddings = [face_embedding]  # For compatibility
            
            # Convert bbox format: YOLO format [x1, y1, x2, y2] to [x, y, w, h]
            # face_boxes format from YOLO: [[x1, y1, x2, y2, conf], ...]
            bbox_x1, bbox_y1, bbox_x2, bbox_y2 = first_face_box[:4]
            bbox = [int(bbox_x1), int(bbox_y1), int(bbox_x2 - bbox_x1), int(bbox_y2 - bbox_y1)]
            
            # Check if face is live (anti-spoofing) using MiniFASNet model
            # Note: is_live now uses the full image with bbox, not just the crop
            print(f"\n{'='*60}")
            print(f"ANTI-SPOOFING CHECK STARTED")
            print(f"Face bbox: {bbox}")
            print(f"Image size: {image_bgr.shape}")
            print(f"{'='*60}\n")
            
            try:
                # Measure anti-spoofing time and memory
                with perf_monitor.measure('anti_spoofing_ms', measure_memory=True):
                    # Pass full image and bbox - the function will handle cropping with different scales
                    is_live_result = is_live(image_bgr, bbox=bbox, threshold=0.5)
                    
                    if not is_live_result:
                        print(f"\n{'='*60}")
                        print(f"❌ ANTI-SPOOFING: SPOOF DETECTED!")
                        print(f"   Rejecting check-in attempt.")
                        print(f"{'='*60}\n")
                        raise HTTPException(
                            status_code=403, 
                            detail="Face spoofing detected. Please use a live face for check-in."
                        )
                    else:
                        print(f"\n{'='*60}")
                        print(f"✓ ANTI-SPOOFING: LIVE FACE CONFIRMED")
                        print(f"   Proceeding with face recognition...")
                        print(f"{'='*60}\n")
                        
            except HTTPException:
                raise
            except Exception as e:
                print(f"\n{'='*60}")
                print(f"❌ ANTI-SPOOFING ERROR: {e}")
                import traceback
                traceback.print_exc()
                print(f"{'='*60}\n")
                raise HTTPException(
                    status_code=403,
                    detail="Unable to verify face liveness. Please try again with a live face."
                )
            
            # Use the first detected face for matching (already extracted above)
            # face_embedding is already available from above
            
            # Match against stored embeddings using cosine similarity
            best_match = None
            best_confidence = 0.0
            
            with perf_monitor.measure('database_matching_ms'):
                all_embeddings = db.query(FaceEmbedding).all()
                perf_monitor.metrics.num_embeddings_searched = len(all_embeddings)
                
                for stored_embedding in all_embeddings:
                    stored_vec = np.array(stored_embedding.embedding)
                    
                    # Skip invalid embeddings
                    if len(stored_vec) == 0 or np.all(stored_vec == 0):
                        continue
                    
                    # Calculate cosine similarity
                    # Normalize vectors first
                    face_norm = face_embedding / (np.linalg.norm(face_embedding) + 1e-8)
                    stored_norm = stored_vec / (np.linalg.norm(stored_vec) + 1e-8)
                    
                    similarity = np.dot(face_norm, stored_norm)
                    
                    if similarity > best_confidence and similarity >= SIMILARITY_THRESHOLD:
                        best_confidence = float(similarity)
                        best_match = stored_embedding
                        
                        perf_monitor.metrics.confidence_score = best_confidence

            if not best_match:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Employee not recognized. Best match confidence: {best_confidence:.3f} (threshold: {SIMILARITY_THRESHOLD})"
                )

            employee = db.query(Employee).filter(Employee.id == best_match.employee_id).first()
            
            if not employee:
                raise HTTPException(status_code=404, detail="Employee associated with embedding not found")
    
            # Validate location if provided
            location_validated = 0  # 0 = not validated, 1 = valid, 2 = invalid
            distance_from_store = None
            
            with perf_monitor.measure('location_validation_ms'):
                if latitude and longitude:
                    # Get store location from camera
                    store = db.query(Store).filter(Store.id == camera.store_id).first()
                    
                    if store and store.latitude and store.longitude:
                        # Calculate distance from store
                        distance_from_store = calculate_distance(
                            latitude, longitude,
                            store.latitude, store.longitude
                        )
                        
                        if distance_from_store is not None:
                            # Validate if within 10 meters
                            if distance_from_store <= MIN_DISTANCE_FROM_STORE:
                                location_validated = 1  # Valid
                            else:
                                location_validated = 2  # Invalid (too far)
                    else:
                        # Store location not set, can't validate
                        location_validated = 0
            
            # Store attendance log
            check_in_time = datetime.utcnow()
            
            # Validate check-in time (only for employees, not admin/manager)
            is_on_time = 1  # Default: on time
            if employee.role and employee.role.lower() not in ['admin', 'manager']:
                # Check if employee has a schedule for today
                check_in_date = check_in_time.date()
                schedule = db.query(Schedule).filter(
                    Schedule.employee_id == employee.id,
                    Schedule.date == check_in_date
                ).first()
                
                if schedule and schedule.shift_start:
                    # Compare check-in time with shift start
                    # Allow 15 minutes grace period
                    from datetime import timedelta
                    shift_start = schedule.shift_start
                    grace_period = timedelta(minutes=15)
                    late_threshold = shift_start + grace_period
                    
                    if check_in_time > late_threshold:
                        is_on_time = 0  # Late
                else:
                    is_on_time = 1  # On time
                # If no schedule, assume on time (flexible schedule)
            
            with perf_monitor.measure('database_write_ms'):
                attendance_log = AttendanceLog(
                    employee_id=employee.id,
                    camera_id=camera.id,
                    confidence=best_confidence,
                    snapshot_url=None,  # In production, save snapshot and store URL
                    latitude=latitude,
                    longitude=longitude,
                    location_validated=location_validated,
                    distance_from_store=distance_from_store,
                    is_on_time=is_on_time,
                    timestamp=check_in_time
                )
                db.add(attendance_log)
                db.commit()

            # Calculate total time manually (before exiting the with block)
            if perf_monitor.start_time:
                perf_monitor.metrics.total_time_ms = (time.perf_counter() - perf_monitor.start_time) * 1000
            
            # Measure system resources before getting metrics
            perf_monitor._measure_resources()
            
            # Get final metrics
            metrics = perf_monitor.get_metrics()
            
            # Log performance summary
            print(f"\n{'='*60}")
            print(f"📊 PERFORMANCE METRICS")
            print(f"{'='*60}")
            print(metrics.get_summary())
            print(f"{'='*60}\n")
            
            return CheckInResponse(
                employee_id=employee.emp_code,
                employee_name=employee.name,
                timestamp=check_in_time,
                confidence=best_confidence,
                camera_id=camera_id,
                latitude=latitude,
                longitude=longitude,
                location_validated=location_validated == 1,
                distance_from_store=distance_from_store,
                performance_metrics=PerformanceMetricsResponse(**metrics.to_dict())
            )
        
        except HTTPException as e:
            # Capture metrics before raising exception
            perf_monitor._measure_resources()
            if perf_monitor.start_time:
                perf_monitor.metrics.total_time_ms = (time.perf_counter() - perf_monitor.start_time) * 1000
            
            metrics = perf_monitor.get_metrics()
            
            # Return error with performance metrics for debugging
            error_response = CheckInErrorResponse(
                detail=e.detail,
                error_type=type(e).__name__,
                performance_metrics=PerformanceMetricsResponse(**metrics.to_dict())
            )
            
            # Log error with metrics
            print(f"\n{'='*60}")
            print(f"❌ CHECK-IN ERROR: {e.detail}")
            print(f"{'='*60}")
            print(metrics.get_summary())
            print(f"{'='*60}\n")
            
            # Return JSON response with error and metrics
            return JSONResponse(
                status_code=e.status_code,
                content=error_response.model_dump()
            )
        
        except Exception as e:
            # Capture metrics for unexpected errors
            perf_monitor._measure_resources()
            if perf_monitor.start_time:
                perf_monitor.metrics.total_time_ms = (time.perf_counter() - perf_monitor.start_time) * 1000
            
            metrics = perf_monitor.get_metrics()
            
            # Log error with metrics
            import traceback
            print(f"\n{'='*60}")
            print(f"❌ UNEXPECTED ERROR: {str(e)}")
            print(f"{'='*60}")
            print(metrics.get_summary())
            print(f"Traceback:")
            traceback.print_exc()
            print(f"{'='*60}\n")
            
            # Return error with metrics
            error_response = CheckInErrorResponse(
                detail=f"Internal server error: {str(e)}",
                error_type=type(e).__name__,
                performance_metrics=PerformanceMetricsResponse(**metrics.to_dict())
            )
            
            return JSONResponse(
                status_code=500,
                content=error_response.model_dump()
            )


@router.get("/attendance/history", response_model=list[CheckInHistoryItem])
def get_check_in_history(
    employee_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get check-in history with employee details.
    """
    query = db.query(AttendanceLog).join(Employee).join(Camera).join(Store)
    
    if employee_id:
        query = query.filter(Employee.emp_code == employee_id)
    
    logs = query.order_by(AttendanceLog.timestamp.desc()).limit(limit).all()
    
    result = []
    for log in logs:
        result.append(CheckInHistoryItem(
            id=log.id,
            employee_id=log.employee.emp_code,
            employee_name=log.employee.name,
            employee_role=log.employee.role,
            timestamp=log.timestamp,
            camera_id=log.camera_id,
            camera_name=log.camera.name if log.camera else None,
            store_name=log.camera.store.name if log.camera and log.camera.store else None,
            confidence=log.confidence,
            latitude=log.latitude,
            longitude=log.longitude,
            location_validated=log.location_validated,
            distance_from_store=log.distance_from_store,
            is_on_time=log.is_on_time
        ))
    
    return result

