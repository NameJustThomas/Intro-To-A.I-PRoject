"""
Anti-spoofing module for face liveness detection.
Uses multiple computer vision techniques to detect if a face is live or a photo/spoof.
"""
import numpy as np
import cv2
from typing import Dict, Tuple


def analyze_texture(face_img: np.ndarray) -> float:
    """
    Analyze texture using Laplacian variance.
    Photos/screens typically have different texture patterns than real skin.
    
    Args:
        face_img: Face image as numpy array (BGR format)
        
    Returns:
        Texture score (higher = more likely live)
    """
    # Convert to grayscale
    gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY) if len(face_img.shape) == 3 else face_img
    
    # Calculate Laplacian variance
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    variance = laplacian.var()
    
    # Normalize score (typical range: 0-500, photos often < 100, live faces > 150)
    # Higher variance = more texture = more likely live
    # Balanced thresholds - strict on photos, lenient on live video
    if variance < 35:
        return 0.2  # Very blurry/low texture (likely photo)
    elif variance < 65:
        return 0.4  # Low texture (probably photo)
    elif variance < 105:
        return 0.65  # Moderate-low texture (could be photo or poor video)
    elif variance < 155:
        return 0.8  # Moderate texture (likely live)
    elif variance < 250:
        return 0.95  # Good texture (very likely live)
    else:
        return 1.0  # High texture (definitely live)


def analyze_color_distribution(face_img: np.ndarray) -> float:
    """
    Analyze color distribution patterns.
    Photos often have different color characteristics than live faces.
    
    Args:
        face_img: Face image as numpy array (BGR format)
        
    Returns:
        Color score (higher = more likely live)
    """
    if len(face_img.shape) != 3:
        return 0.5  # Can't analyze color if grayscale
    
    # Convert to HSV for better color analysis
    hsv = cv2.cvtColor(face_img, cv2.COLOR_BGR2HSV)
    
    # Calculate color variance in each channel
    h_var = np.var(hsv[:, :, 0])
    s_var = np.var(hsv[:, :, 1])
    v_var = np.var(hsv[:, :, 2])
    
    # Live faces typically have more color variation
    # Photos/screens often have more uniform colors
    total_variance = (h_var + s_var + v_var) / 3.0
    
    # Normalize (typical range: 0-10000, photos often < 2000, live > 3000)
    # Balanced thresholds - strict on photos, lenient on live video
    if total_variance < 900:
        return 0.3  # Very uniform colors (likely photo)
    elif total_variance < 1700:
        return 0.5  # Low color variation (probably photo)
    elif total_variance < 2700:
        return 0.7  # Moderate-low variation (could be photo or video)
    elif total_variance < 4000:
        return 0.9  # Moderate variation (likely live)
    else:
        return 1.0  # High variation (definitely live)


def analyze_edge_patterns(face_img: np.ndarray) -> float:
    """
    Analyze edge patterns using Canny edge detection.
    Photos may have different edge characteristics (too sharp or too uniform).
    
    Args:
        face_img: Face image as numpy array (BGR format)
        
    Returns:
        Edge score (higher = more likely live)
    """
    # Convert to grayscale
    gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY) if len(face_img.shape) == 3 else face_img
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)
    
    # Calculate edge density
    edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
    
    # Live faces typically have moderate edge density (0.1-0.3)
    # Photos may have very high (over-sharpened) or very low (blurry) edge density
    # Balanced detection - strict on photos, lenient on live video
    if edge_density < 0.03:
        return 0.2  # Too blurry, likely photo
    elif edge_density < 0.08:
        return 0.45  # Low edge density, might be photo
    elif 0.10 <= edge_density <= 0.30:
        return 1.0  # Good range for live face
    elif edge_density > 0.5:
        return 0.3  # Too sharp/artificial, likely printed photo
    elif edge_density > 0.38:
        return 0.55  # High edge density, suspicious
    else:
        return 0.75  # Moderate score (acceptable)


def analyze_face_quality(face_img: np.ndarray) -> float:
    """
    Analyze overall face image quality.
    Photos may have artifacts, compression, or unrealistic quality.
    
    Args:
        face_img: Face image as numpy array (BGR format)
        
    Returns:
        Quality score (higher = more likely live)
    """
    # Convert to grayscale
    gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY) if len(face_img.shape) == 3 else face_img
    
    # Calculate image sharpness using gradient magnitude
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    gradient_magnitude = np.sqrt(gx**2 + gy**2)
    sharpness = np.mean(gradient_magnitude)
    
    # Normalize (typical range: 0-100, good quality: 20-60)
    # Photos often have compression artifacts or unrealistic sharpness
    # Balanced thresholds - lenient for live video
    if sharpness < 8:
        return 0.3  # Too blurry, likely photo
    elif sharpness < 16:
        return 0.55  # Low sharpness, might be photo
    elif 18 <= sharpness <= 62:
        return 1.0  # Good quality range (live video)
    elif sharpness > 80:
        return 0.4  # Too sharp/artificial, likely photo
    elif sharpness > 70:
        return 0.65  # High sharpness, suspicious but acceptable
    else:
        return 0.85  # Acceptable


def analyze_compression_artifacts(face_img: np.ndarray) -> float:
    """
    Detect JPEG compression artifacts which are common in photos.
    Live video typically has less compression artifacts.
    
    Args:
        face_img: Face image as numpy array (BGR format)
        
    Returns:
        Compression score (higher = more likely live, less compression)
    """
    # Convert to grayscale
    gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY) if len(face_img.shape) == 3 else face_img
    
    # Apply DCT (Discrete Cosine Transform) to detect JPEG compression blocks
    # JPEG compression creates 8x8 block patterns
    h, w = gray.shape
    
    # Check for block artifacts by analyzing high-frequency components
    # Compressed images have more uniform blocks
    block_size = 8
    block_variance_sum = 0
    block_count = 0
    
    for y in range(0, h - block_size, block_size):
        for x in range(0, w - block_size, block_size):
            block = gray[y:y+block_size, x:x+block_size]
            block_var = np.var(block)
            block_variance_sum += block_var
            block_count += 1
    
    if block_count == 0:
        return 0.5  # Can't analyze
    
    avg_block_variance = block_variance_sum / block_count
    
    # Low variance in blocks = more compression artifacts = likely photo
    # High variance = less compression = likely live video
    # Balanced thresholds - lenient for live video
    if avg_block_variance < 45:
        return 0.35  # Heavy compression, likely photo
    elif avg_block_variance < 95:
        return 0.6  # Moderate compression, suspicious but could be video
    elif avg_block_variance < 200:
        return 0.85  # Low compression, likely live
    else:
        return 1.0  # Very low compression, definitely live


def analyze_lighting_consistency(face_img: np.ndarray) -> float:
    """
    Analyze lighting consistency across the face.
    Photos/screens may have unrealistic or inconsistent lighting.
    
    Args:
        face_img: Face image as numpy array (BGR format)
        
    Returns:
        Lighting score (higher = more likely live)
    """
    # Convert to grayscale
    gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY) if len(face_img.shape) == 3 else face_img
    
    # Divide face into regions (left, right, top, bottom)
    h, w = gray.shape
    left = gray[:, :w//2]
    right = gray[:, w//2:]
    top = gray[:h//2, :]
    bottom = gray[h//2:, :]
    
    # Calculate mean brightness for each region
    left_mean = np.mean(left)
    right_mean = np.mean(right)
    top_mean = np.mean(top)
    bottom_mean = np.mean(bottom)
    
    # Calculate variance in lighting across regions
    means = [left_mean, right_mean, top_mean, bottom_mean]
    lighting_variance = np.var(means)
    
    # Live faces typically have some natural lighting variation
    # Photos may have very uniform or very inconsistent lighting
    # Good range: 50-500 variance
    if 50 <= lighting_variance <= 500:
        return 1.0  # Natural lighting variation
    elif lighting_variance < 20:
        return 0.5  # Too uniform, might be photo
    elif lighting_variance > 1000:
        return 0.6  # Too inconsistent, might be screen reflection
    else:
        return 0.8  # Acceptable


def is_live(face_img: np.ndarray, threshold: float = 0.48) -> Tuple[bool, Dict[str, float]]:
    """
    Check if face is live (not a photo/spoof) using multiple detection methods.
    
    Args:
        face_img: Face image as numpy array (BGR format)
        threshold: Minimum score to consider face as live (0.0-1.0)
        
    Returns:
        Tuple of (is_live: bool, scores: dict with detailed scores)
    """
    if face_img is None or face_img.size == 0:
        return False, {"error": "Invalid face image"}
    
    # Ensure minimum size for analysis
    if face_img.shape[0] < 50 or face_img.shape[1] < 50:
        return False, {"error": "Face image too small"}
    
    # Run all analysis methods
    texture_score = analyze_texture(face_img)
    color_score = analyze_color_distribution(face_img)
    edge_score = analyze_edge_patterns(face_img)
    quality_score = analyze_face_quality(face_img)
    lighting_score = analyze_lighting_consistency(face_img)
    compression_score = analyze_compression_artifacts(face_img)  # New check for JPEG artifacts
    
    # Weighted combination of scores
    # Adjusted weights to be stricter on photos
    # Texture, edge, and compression detection are most reliable for detecting photos
    weights = {
        'texture': 0.28,      # Most important - photos have different texture
        'edge': 0.22,         # Very important - photos have different edge patterns
        'compression': 0.18,  # Important - photos often have JPEG compression artifacts
        'color': 0.18,        # Important - photos have different color patterns
        'quality': 0.10,      # Useful for detecting artifacts
        'lighting': 0.04      # Least reliable but adds value
    }
    
    final_score = (
        texture_score * weights['texture'] +
        color_score * weights['color'] +
        edge_score * weights['edge'] +
        quality_score * weights['quality'] +
        lighting_score * weights['lighting'] +
        compression_score * weights['compression']
    )
    
    is_live_result = final_score >= threshold
    
    scores = {
        'final_score': float(final_score),
        'texture': float(texture_score),
        'color': float(color_score),
        'edge': float(edge_score),
        'quality': float(quality_score),
        'lighting': float(lighting_score),
        'compression': float(compression_score),
        'threshold': threshold,
        'is_live': is_live_result
    }
    
    return is_live_result, scores

