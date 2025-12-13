"""
Face recognition module using YOLO-face and InsightFace.
Functions: detect_faces(image), align_face(bbox), get_embedding(face_img)
"""
import numpy as np
import cv2
from PIL import Image
import io
import warnings
from pathlib import Path
import os

warnings.filterwarnings("ignore")

# Global models (loaded on first use)
_yolo_face_model = None
_insightface_app = None
_device = None


def _initialize_models():
    """Initialize YOLO-face and InsightFace models (lazy loading)."""
    global _yolo_face_model, _insightface_app, _device
    
    if _yolo_face_model is not None:
        return
    
    try:
        from ultralytics import YOLO
        import torch
        
        _device = "0" if torch.cuda.is_available() else "cpu"
        
        # Initialize YOLO-face model
        # Try to find the model file (check multiple variants: m, n, s, l, x)
        # Check paths relative to different working directories
        base_paths = [
            Path(__file__).parent.parent.parent / "models" / "yolo-face" / "weights",  # From backend/app/ai/
            Path(__file__).parent.parent.parent.parent / "backend" / "models" / "yolo-face" / "weights",  # From project root
            Path("models") / "yolo-face" / "weights",  # From backend/
            Path("backend") / "models" / "yolo-face" / "weights",  # From project root
            Path("yolo-face") / "weights",  # From project root or backend/
            Path("weights"),  # Current directory
        ]
        
        model_variants = ["yolov11m-face.pt", "yolov11n-face.pt", "yolov11s-face.pt", 
                         "yolov11l-face.pt", "yolov11x-face.pt"]
        
        model_paths = []
        for base in base_paths:
            for variant in model_variants:
                model_paths.append(str(base / variant))
        
        yolo_face_path = None
        for path in model_paths:
            if Path(path).exists():
                yolo_face_path = path
                break
        
        if yolo_face_path is None:
            # Download or use fallback (generic YOLO, not face-specific - less accurate)
            print("Warning: YOLO-face model not found. Using YOLO11n as fallback (not face-specific).")
            _yolo_face_model = YOLO("yolo11n.pt")
        else:
            print(f"Using YOLO-face model: {yolo_face_path}")
            _yolo_face_model = YOLO(yolo_face_path)
        
        # Initialize InsightFace for face recognition (embedding extraction)
        from insightface.app import FaceAnalysis
        
        _insightface_app = FaceAnalysis(
            name="buffalo_l",
            allowed_modules=["detection", "recognition"]  # Only need detection and recognition
        )
        ctx_id = 0 if torch.cuda.is_available() else -1
        _insightface_app.prepare(ctx_id=ctx_id, det_size=(640, 640))
        
        print("Face recognition models initialized successfully")
        
    except Exception as e:
        print(f"Error initializing models: {e}")
        raise


def detect_faces(image_bytes: bytes, conf_threshold: float = 0.5) -> list:
    """
    Detect faces in an image using YOLO-face.
    
    Args:
        image_bytes: Image bytes
        conf_threshold: Confidence threshold for face detection
        
    Returns:
        List of face bounding boxes: [(x1, y1, x2, y2, confidence), ...]
    """
    _initialize_models()
    
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
        
        # Use YOLO-face to detect faces
        results = _yolo_face_model.predict(
            source=image_bgr,
            conf=conf_threshold,
            device=_device,
            verbose=False
        )[0]
        
        face_boxes = []
        if results.boxes is not None:
            for box in results.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                confidence = float(box.conf.item())
                face_boxes.append((x1, y1, x2, y2, confidence))
        
        return face_boxes
        
    except Exception as e:
        print(f"Error detecting faces: {e}")
        return []


def align_face(bbox: tuple, image: np.ndarray) -> np.ndarray:
    """
    Extract and align face region from image.
    
    Args:
        bbox: Bounding box (x1, y1, x2, y2, confidence)
        image: Image array (BGR format)
        
    Returns:
        Cropped face image
    """
    x1, y1, x2, y2 = bbox[:4]
    h, w = image.shape[:2]
    
    # Add padding (25% of face size)
    face_h = y2 - y1
    face_w = x2 - x1
    pad_h = int(face_h * 0.25)
    pad_w = int(face_w * 0.25)
    
    # Crop with padding
    cx1 = max(0, x1 - pad_w)
    cy1 = max(0, y1 - pad_h)
    cx2 = min(w, x2 + pad_w)
    cy2 = min(h, y2 + pad_h)
    
    face_crop = image[cy1:cy2, cx1:cx2]
    return face_crop


def get_embedding(face_img: np.ndarray) -> np.ndarray:
    """
    Get face embedding vector using InsightFace.
    
    Args:
        face_img: Face image as numpy array (BGR format)
        
    Returns:
        Face embedding vector (512 dimensions for buffalo_l model)
    """
    _initialize_models()
    
    try:
        # Convert BGR to RGB for InsightFace
        if len(face_img.shape) == 3:
            face_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
        else:
            face_rgb = face_img
        
        # Get face embedding using InsightFace
        faces = _insightface_app.get(face_rgb)
        
        if len(faces) == 0:
            # If no face detected, return zero vector
            return np.zeros(512, dtype=np.float32)
        
        # Use the first detected face's embedding
        embedding = faces[0].normed_embedding
        
        # Ensure it's a numpy array
        if not isinstance(embedding, np.ndarray):
            embedding = np.array(embedding)
        
        return embedding.astype(np.float32)
        
    except Exception as e:
        print(f"Error extracting embedding: {e}")
        # Return zero vector on error
        return np.zeros(512, dtype=np.float32)


def get_face_embedding_from_image(image_bytes: bytes) -> tuple:
    """
    Convenience function: detect faces and get embeddings.
    
    Args:
        image_bytes: Image bytes
        
    Returns:
        Tuple of (face_boxes, embeddings_list)
        face_boxes: List of (x1, y1, x2, y2, confidence)
        embeddings_list: List of embedding vectors
    """
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image_bgr is None:
        # Try PIL as fallback
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Detect faces
    face_boxes = detect_faces(image_bytes)
    
    embeddings = []
    for bbox in face_boxes:
        # Extract face region
        face_crop = align_face(bbox, image_bgr)
        
        # Get embedding
        embedding = get_embedding(face_crop)
        embeddings.append(embedding)
    
    return face_boxes, embeddings
