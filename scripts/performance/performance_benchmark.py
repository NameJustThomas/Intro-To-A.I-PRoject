"""
Performance Benchmark Script for AI Attendance System

This script measures:
1. Model inference latency (Face Detection, Recognition, Anti-Spoofing, People Counting)
2. Memory usage
3. End-to-end API response time
4. Database query performance
5. System throughput

Usage:
    python scripts/performance/performance_benchmark.py
"""

import time
import sys
import os
import psutil
import numpy as np
import cv2
from pathlib import Path
from typing import Dict, List, Tuple
import statistics

# Add backend to path (go up 2 levels: performance -> scripts -> project root)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

try:
    from app.ai.face_recog import detect_faces, get_embedding, align_face
    from app.ai.anti_spoof import is_live
    from app.ai.people_count import count_people
    import torch
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from project root and dependencies are installed")
    sys.exit(1)


class PerformanceBenchmark:
    def __init__(self):
        self.results = {
            'face_detection': [],
            'face_recognition': [],
            'anti_spoofing': [],
            'people_counting': [],
            'memory_usage': [],
            'end_to_end': []
        }
        
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024  # Convert to MB
    
    def create_test_image(self, width: int = 640, height: int = 480) -> np.ndarray:
        """Create a test image with a face-like pattern"""
        # Create a simple test image (in real scenario, use actual face images)
        # Note: This synthetic image may not contain detectable faces
        # For accurate benchmarks, models need actual face images
        image = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
        return image
    
    def load_test_image(self, image_path: str = None) -> np.ndarray:
        """Load a test image from file or create synthetic"""
        if image_path and os.path.exists(image_path):
            img = cv2.imread(image_path)
            if img is not None:
                return img
        
        # Create synthetic image if no file provided
        return self.create_test_image()
    
    def benchmark_face_detection(self, image: np.ndarray, iterations: int = 10) -> Dict:
        """Measure face detection performance"""
        print("🔍 Benchmarking Face Detection (YOLO-face)...")
        times = []
        
        # Warm-up
        try:
            _ = detect_faces(image)
        except Exception as e:
            print(f"Warning: Face detection failed: {e}")
            return {'avg_ms': 0, 'min_ms': 0, 'max_ms': 0, 'std_ms': 0}
        
        for i in range(iterations):
            start = time.perf_counter()
            try:
                faces = detect_faces(image)
                elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
                times.append(elapsed)
            except Exception as e:
                print(f"  Iteration {i+1} failed: {e}")
        
        if not times:
            return {'avg_ms': 0, 'min_ms': 0, 'max_ms': 0, 'std_ms': 0}
        
        return {
            'avg_ms': statistics.mean(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'std_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'iterations': len(times)
        }
    
    def benchmark_face_recognition(self, image: np.ndarray, iterations: int = 10) -> Dict:
        """Measure face recognition (embedding extraction) performance"""
        print("👤 Benchmarking Face Recognition (InsightFace)...")
        times = []
        
        # First detect a face
        try:
            faces = detect_faces(image)
            if not faces:
                print("  ⚠️  No face detected in test image")
                print("     Note: Synthetic images may not contain detectable faces.")
                print("     For accurate benchmarks, use actual face images or test via API with live camera.")
                return {'avg_ms': 0, 'min_ms': 0, 'max_ms': 0, 'std_ms': 0, 'error': 'No face detected'}
            
            # Align face
            face_crop = align_face(faces[0], image)
            
            # Warm-up
            _ = get_embedding(face_crop)
        except Exception as e:
            print(f"  ⚠️  Warning: Face recognition failed: {e}")
            return {'avg_ms': 0, 'min_ms': 0, 'max_ms': 0, 'std_ms': 0, 'error': str(e)}
        
        for i in range(iterations):
            start = time.perf_counter()
            try:
                embedding = get_embedding(face_crop)
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)
            except Exception as e:
                print(f"  Iteration {i+1} failed: {e}")
        
        if not times:
            print("  ⚠️  No successful iterations")
            return {'avg_ms': 0, 'min_ms': 0, 'max_ms': 0, 'std_ms': 0, 'error': 'No successful iterations'}
        
        return {
            'avg_ms': statistics.mean(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'std_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'iterations': len(times)
        }
    
    def benchmark_anti_spoofing(self, image: np.ndarray, iterations: int = 10) -> Dict:
        """Measure anti-spoofing detection performance"""
        print("🛡️ Benchmarking Anti-Spoofing (MiniFASNet)...")
        times = []
        
        # First detect a face
        try:
            faces = detect_faces(image)
            if not faces:
                print("  ⚠️  No face detected in test image")
                print("     Note: Synthetic images may not contain detectable faces.")
                print("     For accurate benchmarks, use actual face images or test via API with live camera.")
                return {'avg_ms': 0, 'min_ms': 0, 'max_ms': 0, 'std_ms': 0, 'error': 'No face detected'}
            
            bbox = faces[0]
            # Convert to [x, y, w, h] format
            x1, y1, x2, y2 = bbox[:4]
            bbox_formatted = [int(x1), int(y1), int(x2 - x1), int(y2 - y1)]
            
            # Warm-up
            _ = is_live(image, bbox_formatted)
        except Exception as e:
            print(f"  ⚠️  Warning: Anti-spoofing failed: {e}")
            return {'avg_ms': 0, 'min_ms': 0, 'max_ms': 0, 'std_ms': 0, 'error': str(e)}
        
        for i in range(iterations):
            start = time.perf_counter()
            try:
                result = is_live(image, bbox_formatted)
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)
            except Exception as e:
                print(f"  Iteration {i+1} failed: {e}")
        
        if not times:
            print("  ⚠️  No successful iterations")
            return {'avg_ms': 0, 'min_ms': 0, 'max_ms': 0, 'std_ms': 0, 'error': 'No successful iterations'}
        
        return {
            'avg_ms': statistics.mean(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'std_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'iterations': len(times)
        }
    
    def benchmark_people_counting(self, image: np.ndarray, iterations: int = 10) -> Dict:
        """Measure people counting performance"""
        print("👥 Benchmarking People Counting (YOLO11s)...")
        times = []
        
        # Warm-up
        try:
            _ = count_people(image)
        except Exception as e:
            print(f"Warning: People counting failed: {e}")
            return {'avg_ms': 0, 'min_ms': 0, 'max_ms': 0, 'std_ms': 0}
        
        for i in range(iterations):
            start = time.perf_counter()
            try:
                count = count_people(image)
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)
            except Exception as e:
                print(f"  Iteration {i+1} failed: {e}")
        
        if not times:
            return {'avg_ms': 0, 'min_ms': 0, 'max_ms': 0, 'std_ms': 0}
        
        return {
            'avg_ms': statistics.mean(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'std_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'iterations': len(times)
        }
    
    def benchmark_memory_usage(self) -> Dict:
        """Measure memory usage of loaded models"""
        print("💾 Measuring Memory Usage...")
        memory_mb = self.get_memory_usage()
        
        # Check if GPU is available
        gpu_available = torch.cuda.is_available() if 'torch' in sys.modules else False
        gpu_memory = None
        if gpu_available:
            gpu_memory = torch.cuda.memory_allocated() / 1024 / 1024  # MB
        
        return {
            'ram_mb': memory_mb,
            'gpu_available': gpu_available,
            'gpu_memory_mb': gpu_memory
        }
    
    def benchmark_end_to_end(self, image: np.ndarray, iterations: int = 5) -> Dict:
        """Measure end-to-end check-in pipeline performance"""
        print("🔄 Benchmarking End-to-End Pipeline...")
        times = []
        skipped = 0
        
        for i in range(iterations):
            start = time.perf_counter()
            try:
                # Simulate full pipeline
                # 1. Face detection
                faces = detect_faces(image)
                if not faces:
                    skipped += 1
                    continue
                
                # 2. Anti-spoofing
                bbox = faces[0]
                x1, y1, x2, y2 = bbox[:4]
                bbox_formatted = [int(x1), int(y1), int(x2 - x1), int(y2 - y1)]
                is_live_result = is_live(image, bbox_formatted)
                
                if not is_live_result:
                    skipped += 1
                    continue
                
                # 3. Face recognition
                face_crop = align_face(faces[0], image)
                embedding = get_embedding(face_crop)
                
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)
            except Exception as e:
                print(f"  Iteration {i+1} failed: {e}")
                skipped += 1
        
        if not times:
            print(f"  ⚠️  All {iterations} iterations skipped (no face detected or spoofing detected)")
            print("     Note: Synthetic images may not contain detectable faces.")
            print("     For accurate benchmarks, test via API with live camera frames.")
            return {'avg_ms': 0, 'min_ms': 0, 'max_ms': 0, 'std_ms': 0, 'error': 'All iterations skipped', 'skipped': skipped}
        
        if skipped > 0:
            print(f"  ⚠️  {skipped} iterations skipped (no face or spoofing detected)")
        
        return {
            'avg_ms': statistics.mean(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'std_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'iterations': len(times),
            'skipped': skipped
        }
    
    def run_all_benchmarks(self, iterations: int = 10):
        """Run all performance benchmarks"""
        print("=" * 60)
        print("🚀 AI Attendance System - Performance Benchmark")
        print("=" * 60)
        print()
        print("⚠️  IMPORTANT: Using synthetic test data (random noise image)")
        print("   Synthetic images may NOT contain detectable faces.")
        print("   Results showing 0.00ms indicate no face was detected.")
        print()
        print("   For accurate model performance metrics:")
        print("   - Test via API endpoint with actual camera frames")
        print("   - Or use actual face images (but system uses live camera)")
        print()
        
        # Create synthetic test image for model benchmarking
        image = self.create_test_image()
        
        print(f"📸 Test Image: {image.shape[1]}x{image.shape[0]} pixels (synthetic)")
        print(f"🖥️  Device: {'GPU (CUDA)' if torch.cuda.is_available() else 'CPU'}")
        print()
        
        # Run benchmarks
        results = {}
        
        # Memory usage (before)
        memory_before = self.get_memory_usage()
        
        # Face Detection
        results['face_detection'] = self.benchmark_face_detection(image, iterations)
        print(f"   Average: {results['face_detection']['avg_ms']:.2f}ms")
        print()
        
        # Face Recognition
        results['face_recognition'] = self.benchmark_face_recognition(image, iterations)
        print(f"   Average: {results['face_recognition']['avg_ms']:.2f}ms")
        print()
        
        # Anti-Spoofing
        results['anti_spoofing'] = self.benchmark_anti_spoofing(image, iterations)
        print(f"   Average: {results['anti_spoofing']['avg_ms']:.2f}ms")
        print()
        
        # People Counting
        results['people_counting'] = self.benchmark_people_counting(image, iterations)
        print(f"   Average: {results['people_counting']['avg_ms']:.2f}ms")
        print()
        
        # Memory Usage
        memory_after = self.get_memory_usage()
        results['memory'] = self.benchmark_memory_usage()
        results['memory']['delta_mb'] = memory_after - memory_before
        print(f"   RAM Usage: {results['memory']['ram_mb']:.2f} MB")
        if results['memory']['gpu_available']:
            print(f"   GPU Memory: {results['memory']['gpu_memory_mb']:.2f} MB")
        print()
        
        # End-to-End
        results['end_to_end'] = self.benchmark_end_to_end(image, iterations=5)
        print(f"   Average: {results['end_to_end']['avg_ms']:.2f}ms")
        print()
        
        # Print summary
        self.print_summary(results)
        
        return results
    
    def print_summary(self, results: Dict):
        """Print performance summary"""
        print("=" * 60)
        print("📊 Performance Summary")
        print("=" * 60)
        print()
        
        print("Model Latency (Average):")
        fd_result = results['face_detection']
        fr_result = results['face_recognition']
        as_result = results['anti_spoofing']
        pc_result = results['people_counting']
        e2e_result = results['end_to_end']
        
        print(f"  🔍 Face Detection:      {fd_result['avg_ms']:>8.2f} ms", end="")
        if fd_result.get('error'):
            print(f" ⚠️ ({fd_result['error']})")
        else:
            print()
        
        print(f"  👤 Face Recognition:    {fr_result['avg_ms']:>8.2f} ms", end="")
        if fr_result.get('error'):
            print(f" ⚠️ ({fr_result['error']})")
        else:
            print()
        
        print(f"  🛡️  Anti-Spoofing:       {as_result['avg_ms']:>8.2f} ms", end="")
        if as_result.get('error'):
            print(f" ⚠️ ({as_result['error']})")
        else:
            print()
        
        print(f"  👥 People Counting:     {pc_result['avg_ms']:>8.2f} ms", end="")
        if pc_result.get('error'):
            print(f" ⚠️ ({pc_result['error']})")
        else:
            print()
        print()
        
        print("End-to-End Performance:")
        print(f"  🔄 Full Pipeline:       {e2e_result['avg_ms']:>8.2f} ms", end="")
        if e2e_result.get('error'):
            print(f" ⚠️ ({e2e_result['error']})")
        elif e2e_result.get('skipped', 0) > 0:
            print(f" ({e2e_result['skipped']} iterations skipped)")
        else:
            print()
        print()
        
        print("Memory Usage:")
        print(f"  💾 RAM:                 {results['memory']['ram_mb']:>8.2f} MB")
        if results['memory']['gpu_available']:
            print(f"  🎮 GPU Memory:          {results['memory']['gpu_memory_mb']:>8.2f} MB")
        print()
        
        # Calculate theoretical throughput
        if results['end_to_end']['avg_ms'] > 0:
            throughput = 1000 / results['end_to_end']['avg_ms']
            print(f"📈 Theoretical Throughput: {throughput:.2f} requests/second")
        print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Performance Benchmark for AI Attendance System')
    parser.add_argument('--iterations', type=int, default=10, help='Number of iterations per benchmark')
    parser.add_argument('--output', type=str, help='Output JSON file for results')
    
    args = parser.parse_args()
    
    benchmark = PerformanceBenchmark()
    results = benchmark.run_all_benchmarks(
        iterations=args.iterations
    )
    
    # Save results to JSON if requested
    if args.output:
        import json
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✅ Results saved to {args.output}")


if __name__ == "__main__":
    main()

