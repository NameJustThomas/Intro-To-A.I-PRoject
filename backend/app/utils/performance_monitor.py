"""
Performance monitoring utility for tracking check-in pipeline metrics.
"""
import time
import os
from typing import Dict, Optional
from dataclasses import dataclass, field
from contextlib import contextmanager

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    # Timing metrics (in milliseconds)
    total_time_ms: float = 0.0
    image_upload_ms: float = 0.0
    face_detection_ms: float = 0.0
    anti_spoofing_ms: float = 0.0
    face_recognition_ms: float = 0.0
    database_matching_ms: float = 0.0
    database_write_ms: float = 0.0
    location_validation_ms: float = 0.0
    
    # Additional metrics
    num_faces_detected: int = 0
    num_embeddings_searched: int = 0
    confidence_score: float = 0.0
    
    # System resource metrics
    cpu_percent: float = 0.0  # CPU usage percentage (normalized 0-100%)
    cpu_cores: int = 1  # Number of CPU cores
    ram_usage_mb: float = 0.0  # Total RAM usage in MB
    ram_percent: float = 0.0  # RAM usage percentage
    gpu_available: bool = False
    gpu_memory_mb: Optional[float] = None  # GPU memory usage in MB
    
    # Per-model memory usage (MB)
    face_detection_memory_mb: float = 0.0  # Memory used by face detection model
    face_recognition_memory_mb: float = 0.0  # Memory used by face recognition model
    anti_spoofing_memory_mb: float = 0.0  # Memory used by anti-spoofing model
    
    # Performance warnings
    slow_detection_warning: bool = False  # True if face detection > 5s
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            'total_time_ms': round(self.total_time_ms, 2),
            'image_upload_ms': round(self.image_upload_ms, 2),
            'face_detection_ms': round(self.face_detection_ms, 2),
            'anti_spoofing_ms': round(self.anti_spoofing_ms, 2),
            'face_recognition_ms': round(self.face_recognition_ms, 2),
            'database_matching_ms': round(self.database_matching_ms, 2),
            'database_write_ms': round(self.database_write_ms, 2),
            'location_validation_ms': round(self.location_validation_ms, 2),
            'num_faces_detected': self.num_faces_detected,
            'num_embeddings_searched': self.num_embeddings_searched,
            'confidence_score': round(self.confidence_score, 4),
            'cpu_percent': round(self.cpu_percent, 2),
            'cpu_cores': self.cpu_cores,
            'ram_usage_mb': round(self.ram_usage_mb, 2),
            'ram_percent': round(self.ram_percent, 2),
            'gpu_available': self.gpu_available,
            'slow_detection_warning': self.slow_detection_warning,
            # Per-model memory
            'face_detection_memory_mb': round(self.face_detection_memory_mb, 2),
            'face_recognition_memory_mb': round(self.face_recognition_memory_mb, 2),
            'anti_spoofing_memory_mb': round(self.anti_spoofing_memory_mb, 2),
        }
        if self.gpu_memory_mb is not None:
            result['gpu_memory_mb'] = round(self.gpu_memory_mb, 2)
        return result
    
    def get_summary(self) -> str:
        """Get human-readable summary."""
        summary = (
            f"Total: {self.total_time_ms:.2f}ms | "
            f"Detection: {self.face_detection_ms:.2f}ms | "
            f"Anti-Spoof: {self.anti_spoofing_ms:.2f}ms | "
            f"Recognition: {self.face_recognition_ms:.2f}ms | "
            f"DB Match: {self.database_matching_ms:.2f}ms"
        )
        if self.cpu_percent > 0 or self.ram_usage_mb > 0:
            summary += f" | CPU: {self.cpu_percent:.1f}% | RAM: {self.ram_usage_mb:.1f}MB ({self.ram_percent:.1f}%)"
        
        # Add per-model memory if available
        memory_parts = []
        if self.face_detection_memory_mb > 0:
            memory_parts.append(f"YOLO: {self.face_detection_memory_mb:.1f}MB")
        if self.face_recognition_memory_mb > 0:
            memory_parts.append(f"InsightFace: {self.face_recognition_memory_mb:.1f}MB")
        if self.anti_spoofing_memory_mb > 0:
            memory_parts.append(f"MiniFASNet: {self.anti_spoofing_memory_mb:.1f}MB")
        
        if memory_parts:
            summary += f" | Model Memory: {', '.join(memory_parts)}"
        
        return summary


class PerformanceMonitor:
    """Context manager for measuring performance of check-in pipeline."""
    
    def __init__(self):
        self.metrics = PerformanceMetrics()
        self.start_time: Optional[float] = None
        self.timers: Dict[str, float] = {}
        self.process = None
        self.cpu_samples = []  # Store CPU samples during execution
        self.initial_memory_mb = 0.0  # Initial memory before any operations
        if PSUTIL_AVAILABLE:
            try:
                self.process = psutil.Process(os.getpid())
                # Initialize CPU measurement (first call returns 0.0)
                self.process.cpu_percent(interval=None)
                # Get initial memory
                self.initial_memory_mb = self.process.memory_info().rss / 1024 / 1024
            except Exception:
                pass
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        # Start CPU monitoring
        if PSUTIL_AVAILABLE and self.process:
            try:
                # Initialize CPU measurement
                self.process.cpu_percent(interval=None)
            except Exception:
                pass
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager - always measure final metrics, even on error."""
        if self.start_time:
            self.metrics.total_time_ms = (time.perf_counter() - self.start_time) * 1000
        
        # Measure CPU and RAM at the end (even if error occurred)
        self._measure_resources()
        
        # Log metrics even if there was an error (for debugging)
        if exc_type is not None:
            print(f"\n{'='*60}")
            print(f"⚠️  ERROR OCCURRED - Performance Metrics (partial)")
            print(f"{'='*60}")
            print(self.metrics.get_summary())
            print(f"Error Type: {exc_type.__name__ if exc_type else 'Unknown'}")
            print(f"Error Message: {str(exc_val) if exc_val else 'No message'}")
            print(f"{'='*60}\n")
        
        # Don't suppress exceptions
        return False
    
    def _measure_resources(self):
        """Measure CPU and RAM usage."""
        if not PSUTIL_AVAILABLE or not self.process:
            return
        
        try:
            num_cores = psutil.cpu_count(logical=True)  # Get number of CPU cores
            self.metrics.cpu_cores = num_cores
            
            # Calculate average CPU from samples collected during execution
            if self.cpu_samples:
                # Average CPU across all operations
                cpu_avg_raw = sum(self.cpu_samples) / len(self.cpu_samples)
            else:
                # Fallback: measure CPU over a small interval
                # This might be 0 if process is idle
                cpu_avg_raw = self.process.cpu_percent(interval=0.1)
            
            # Normalize to 0-100% (divide by number of cores)
            # This gives average CPU usage per core
            cpu_normalized = min(cpu_avg_raw / num_cores, 100.0) if num_cores > 0 else cpu_avg_raw
            
            # Store normalized CPU (0-100%) and number of cores
            self.metrics.cpu_percent = max(cpu_normalized, 0.0)  # Ensure non-negative
            
            # RAM usage
            mem_info = self.process.memory_info()
            self.metrics.ram_usage_mb = mem_info.rss / 1024 / 1024  # Convert to MB
            
            # RAM percentage
            system_mem = psutil.virtual_memory()
            self.metrics.ram_percent = (mem_info.rss / system_mem.total) * 100
            
            # GPU memory (if available)
            try:
                import torch
                if torch.cuda.is_available():
                    self.metrics.gpu_available = True
                    self.metrics.gpu_memory_mb = torch.cuda.memory_allocated() / 1024 / 1024
            except ImportError:
                pass
        except Exception:
            # Silently fail if resource measurement fails
            pass
    
    @contextmanager
    def measure(self, metric_name: str, measure_memory: bool = False):
        """Context manager to measure a specific operation.
        
        Args:
            metric_name: Name of the metric to store
            measure_memory: If True, measure memory delta for this operation
        """
        start = time.perf_counter()
        # Sample CPU and memory at start of operation
        cpu_start = None
        memory_start_mb = 0.0
        if PSUTIL_AVAILABLE and self.process:
            try:
                cpu_start = self.process.cpu_percent(interval=None)
                if measure_memory:
                    memory_start_mb = self.process.memory_info().rss / 1024 / 1024
            except Exception:
                pass
        
        try:
            yield
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            setattr(self.metrics, metric_name, elapsed_ms)
            
            # Sample CPU and memory at end of operation
            if PSUTIL_AVAILABLE and self.process:
                try:
                    cpu_end = self.process.cpu_percent(interval=None)
                    if cpu_start is not None and cpu_end is not None:
                        # Average CPU during this operation
                        cpu_avg = (cpu_start + cpu_end) / 2
                        self.cpu_samples.append(cpu_avg)
                    
                    # Measure memory delta if requested
                    if measure_memory:
                        memory_end_mb = self.process.memory_info().rss / 1024 / 1024
                        memory_delta = memory_end_mb - memory_start_mb
                        # Store memory for specific model operations
                        if 'face_detection' in metric_name:
                            self.metrics.face_detection_memory_mb = max(memory_delta, 0.0)
                        elif 'face_recognition' in metric_name:
                            self.metrics.face_recognition_memory_mb = max(memory_delta, 0.0)
                        elif 'anti_spoofing' in metric_name or 'anti_spoof' in metric_name:
                            self.metrics.anti_spoofing_memory_mb = max(memory_delta, 0.0)
                except Exception:
                    pass
    
    def set_metric(self, name: str, value: float):
        """Set a metric value directly."""
        if hasattr(self.metrics, name):
            setattr(self.metrics, name, value)
    
    def get_metrics(self) -> PerformanceMetrics:
        """Get the performance metrics."""
        return self.metrics

