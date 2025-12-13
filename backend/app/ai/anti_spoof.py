# -*- coding: utf-8 -*-
"""
Anti-spoofing module using MiniFASNet models from Silent-Face-Anti-Spoofing.
Properly integrated with multiple model fusion approach.
Function: is_live(face_img, bbox) returning True/False
"""
import numpy as np
import cv2
import torch
import torch.nn.functional as F
from pathlib import Path
import warnings
import os
from collections import OrderedDict

# Import model architecture
try:
    from app.ai.minifasnet import MiniFASNetV1, MiniFASNetV2, MiniFASNetV1SE, MiniFASNetV2SE
except ImportError:
    from .minifasnet import MiniFASNetV1, MiniFASNetV2, MiniFASNetV1SE, MiniFASNetV2SE

# Import utilities
try:
    from app.ai.anti_spoof_utils import get_kernel, parse_model_name
    from app.ai.generate_patches import CropImage
    from app.ai.transform import Compose, ToTensor
except ImportError:
    from .anti_spoof_utils import get_kernel, parse_model_name
    from .generate_patches import CropImage
    from .transform import Compose, ToTensor

warnings.filterwarnings("ignore")

# Model mapping
MODEL_MAPPING = {
    'MiniFASNetV1': MiniFASNetV1,
    'MiniFASNetV2': MiniFASNetV2,
    'MiniFASNetV1SE': MiniFASNetV1SE,
    'MiniFASNetV2SE': MiniFASNetV2SE
}

# Global variables
_models_cache = {}  # Cache loaded models
_device = None
_model_dir = None
_image_cropper = None


def _initialize_anti_spoofing():
    """Initialize anti-spoofing system (lazy loading)."""
    global _device, _model_dir, _image_cropper
    
    if _device is not None:
        return
    
    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Anti-spoofing initialized on device: {_device}")
    
    # Find model directory - use Path(__file__) for reliable path resolution
    base_paths = [
        Path(__file__).parent.parent.parent / "models" / "silent-face-anti-spoofing" / "model",  # From backend/app/ai/
        Path(__file__).parent.parent.parent.parent / "backend" / "models" / "silent-face-anti-spoofing" / "model",  # From project root
        Path("models") / "silent-face-anti-spoofing" / "model",  # From backend/
        Path("backend") / "models" / "silent-face-anti-spoofing" / "model",  # From project root
    ]
    
    for base_path in base_paths:
        if base_path.exists():
            _model_dir = str(base_path)
            break
    
    if _model_dir is None:
        print("⚠ Warning: Anti-spoofing model directory not found")
        print("  Expected paths:")
        for path in base_paths:
            print(f"    - {path}")
    else:
        print(f"Model directory found: {_model_dir}")
    
    _image_cropper = CropImage()


def _load_model(model_path):
    """
    Load a single model from file path.
    Returns: (model, model_info) or (None, None) if failed
    """
    global _models_cache, _device
    
    # Check cache
    if model_path in _models_cache:
        return _models_cache[model_path]
    
    try:
        model_name = os.path.basename(model_path)
        h_input, w_input, model_type, scale = parse_model_name(model_name)
        kernel_size = get_kernel(h_input, w_input)
        
        # Create model
        model_class = MODEL_MAPPING.get(model_type)
        if model_class is None:
            print(f"⚠ Unknown model type: {model_type}")
            return None, None
        
        model = model_class(conv6_kernel=kernel_size).to(_device)
        
        # Load weights
        state_dict = torch.load(model_path, map_location=_device)
        
        # Handle 'module.' prefix
        keys = iter(state_dict)
        first_layer_name = next(keys)
        if first_layer_name.find('module.') >= 0:
            new_state_dict = OrderedDict()
            for key, value in state_dict.items():
                name_key = key[7:]  # Remove 'module.' prefix
                new_state_dict[name_key] = value
            state_dict = new_state_dict
        
        model.load_state_dict(state_dict)
        model.eval()
        
        model_info = {
            'h_input': h_input,
            'w_input': w_input,
            'model_type': model_type,
            'scale': scale,
            'kernel_size': kernel_size
        }
        
        # Cache model
        _models_cache[model_path] = (model, model_info)
        
        return model, model_info
        
    except Exception as e:
        print(f"Error loading model {model_path}: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def _predict_with_model(img, model_path):
    """
    Run prediction with a single model.
    Returns: prediction array or None
    """
    global _device, _image_cropper
    
    model, model_info = _load_model(model_path)
    if model is None:
        return None
    
    try:
        # Prepare image
        h_input = model_info['h_input']
        w_input = model_info['w_input']
        scale = model_info['scale']
        
        # Transform image
        test_transform = Compose([ToTensor()])
        img_tensor = test_transform(img)
        img_tensor = img_tensor.unsqueeze(0).to(_device)
        
        # Run inference
        with torch.no_grad():
            result = model.forward(img_tensor)
            result = F.softmax(result).cpu().numpy()
        
        return result
        
    except Exception as e:
        print(f"Error running prediction with {model_path}: {e}")
        return None


def is_live(face_img: np.ndarray, bbox=None, threshold: float = 0.5) -> bool:
    """
    Check if face is live (not a photo/spoof) using MiniFASNet models.
    
    This function uses the proper approach from Silent-Face-Anti-Spoofing:
    - Loads all models from the model directory
    - Generates patches with different scales for each model
    - Sums predictions from all models
    - Makes final decision based on argmax
    
    Args:
        face_img: Face image as numpy array (BGR format)
        bbox: Bounding box [x, y, w, h] for face. If None, uses full image.
        threshold: Threshold for real face probability (not used in original approach,
                  but kept for compatibility. Original uses argmax)
        
    Returns:
        True if live, False if spoof
    """
    global _model_dir, _image_cropper
    
    if face_img is None or face_img.size == 0:
        print("ANTI-SPOOFING ERROR: Invalid face image provided")
        return False
    
    _initialize_anti_spoofing()
    
    if _model_dir is None:
        print("⚠ Anti-spoofing models not found, rejecting for safety")
        return False
    
    try:
        # Get all model files
        model_files = [f for f in os.listdir(_model_dir) if f.endswith('.pth')]
        
        if not model_files:
            print("⚠ No model files found in model directory")
            return False
        
        # Prepare bbox - if not provided, use full image
        if bbox is None:
            h, w = face_img.shape[:2]
            bbox = [0, 0, w, h]
        
        # Sum predictions from all models
        prediction = np.zeros((1, 3))  # Default: 3 classes (real, print, replay)
        
        for model_name in model_files:
            model_path = os.path.join(_model_dir, model_name)
            
            # Parse model info
            h_input, w_input, model_type, scale = parse_model_name(model_name)
            
            # Generate patch/crop based on scale
            if scale is None:
                # Original image (no crop)
                img = cv2.resize(face_img, (w_input, h_input))
            else:
                # Crop with scale
                param = {
                    "org_img": face_img,
                    "bbox": bbox,
                    "scale": scale,
                    "out_w": w_input,
                    "out_h": h_input,
                    "crop": True,
                }
                img = _image_cropper.crop(**param)
            
            # Run prediction
            result = _predict_with_model(img, model_path)
            
            if result is not None:
                # Ensure same number of classes
                if result.shape[1] == prediction.shape[1]:
                    prediction += result
                else:
                    print(f"⚠ Model {model_name} has {result.shape[1]} classes, expected {prediction.shape[1]}")
        
        # Make final decision
        label = np.argmax(prediction)
        value = prediction[0][label] / len(model_files)  # Average probability
        
        # Class 1 = Real Face (according to original test.py)
        # Class 0 = Fake Face (print or replay)
        is_live_result = (label == 1)
        
        # Logging
        print("=" * 70)
        print("ANTI-SPOOFING ANALYSIS (Multi-Model Fusion):")
        print(f"  Models Used:           {len(model_files)}")
        print(f"  Prediction:            {prediction[0]}")
        print(f"  Label:                 {label} ({'REAL' if label == 1 else 'FAKE'})")
        print(f"  Confidence:            {value:.4f}")
        print(f"  Decision:              {'✓ LIVE FACE' if is_live_result else '✗ SPOOF DETECTED'}")
        print(f"  Face Size:             {face_img.shape}")
        if bbox:
            print(f"  BBox:                  {bbox}")
        print("=" * 70)
        
        return is_live_result
        
    except Exception as e:
        print(f"ANTI-SPOOFING ERROR: {e}")
        import traceback
        traceback.print_exc()
        # For safety, reject if error occurs
        return False
