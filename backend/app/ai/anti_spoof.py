"""
Anti-spoofing module.
Function: is_live(face_img) returning True/False
"""
import numpy as np


def is_live(face_img: np.ndarray) -> bool:
    """
    Check if face is live (not a photo/spoof).
    
    Args:
        face_img: Face image as numpy array
        
    Returns:
        True if face is live, False if spoofed
    """
    # Stub implementation
    # In production, would use anti-spoofing models:
    # - Face liveness detection models
    # - 3D face analysis
    # - Texture analysis
    # - Blink detection
    # - Motion analysis
    
    # For now, always return True (assume live)
    return True

