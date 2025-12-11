"""
People counting module using YOLO11.
Function: count_people(image) using YOLO11
"""
import numpy as np
import cv2
from PIL import Image
import io
import warnings

warnings.filterwarnings("ignore")

# Global model (loaded on first use)
_yolo_person_model = None
_device = None


def _initialize_model():
    """Initialize YOLO11 model for person detection (lazy loading)."""
    global _yolo_person_model, _device
    
    if _yolo_person_model is not None:
        return
    
    try:
        from ultralytics import YOLO
        import torch
        
        _device = 0 if torch.cuda.is_available() else "cpu"
        
        # Initialize YOLO11 for person detection
        # YOLO11s is a good balance between speed and accuracy
        _yolo_person_model = YOLO("yolo11s.pt")
        
        print("People counting model initialized successfully")
        
    except Exception as e:
        print(f"Error initializing YOLO model: {e}")
        raise


def count_people(image_bytes: bytes, conf_threshold: float = 0.35) -> int:
    """
    Count people in an image using YOLO11.
    
    Args:
        image_bytes: Image bytes
        conf_threshold: Confidence threshold for person detection
        
    Returns:
        Number of people detected
    """
    _initialize_model()
    
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image_bgr is None:
            # Try PIL as fallback
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert BGR to RGB for YOLO
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        
        # Use YOLO11 to detect people (class 0 = person)
        results = _yolo_person_model.predict(
            source=image_rgb,
            imgsz=768,
            conf=conf_threshold,
            classes=[0],  # Only detect person class
            device=_device,
            verbose=False
        )[0]
        
        person_count = 0
        if results.boxes is not None:
            for box in results.boxes:
                cls_id = int(box.cls.item())
                if cls_id == 0:  # Person class
                    person_count += 1
        
        return person_count
        
    except Exception as e:
        print(f"Error counting people: {e}")
        return 0
