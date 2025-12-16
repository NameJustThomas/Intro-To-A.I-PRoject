"""
API Performance Testing Script

Measures:
1. API endpoint response times
2. Database query performance
3. Concurrent request handling
4. Throughput (requests per second)

Usage:
    python scripts/performance/api_performance_test.py --base-url http://localhost:8000
"""

import time
import os
import requests
import statistics
import argparse
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import json


class APIPerformanceTest:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.results = {}
    
    def test_health_endpoint(self, iterations: int = 10) -> Dict:
        """Test health check endpoint"""
        print("🏥 Testing Health Endpoint...")
        times = []
        errors = 0
        
        for i in range(iterations):
            start = time.perf_counter()
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                elapsed = (time.perf_counter() - start) * 1000
                if response.status_code == 200:
                    times.append(elapsed)
                else:
                    errors += 1
            except Exception as e:
                errors += 1
                print(f"  Error: {e}")
        
        if not times:
            return {'avg_ms': 0, 'errors': errors}
        
        return {
            'avg_ms': statistics.mean(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'std_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'errors': errors,
            'iterations': len(times)
        }
    
    def test_cameras_endpoint(self, iterations: int = 10) -> Dict:
        """Test cameras list endpoint"""
        print("📹 Testing Cameras Endpoint...")
        times = []
        errors = 0
        
        for i in range(iterations):
            start = time.perf_counter()
            try:
                response = requests.get(f"{self.base_url}/api/v1/cameras", timeout=10)
                elapsed = (time.perf_counter() - start) * 1000
                if response.status_code == 200:
                    times.append(elapsed)
                else:
                    errors += 1
            except Exception as e:
                errors += 1
        
        if not times:
            return {'avg_ms': 0, 'errors': errors}
        
        return {
            'avg_ms': statistics.mean(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'std_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'errors': errors,
            'iterations': len(times)
        }
    
    def test_concurrent_requests(self, endpoint: str = "/health", num_requests: int = 50, concurrency: int = 10) -> Dict:
        """Test concurrent request handling"""
        print(f"🔄 Testing Concurrent Requests ({concurrency} concurrent, {num_requests} total)...")
        
        def make_request():
            start = time.perf_counter()
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                elapsed = (time.perf_counter() - start) * 1000
                return {'success': response.status_code == 200, 'time_ms': elapsed}
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        start_total = time.perf_counter()
        results = []
        
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            for future in as_completed(futures):
                results.append(future.result())
        
        total_time = (time.perf_counter() - start_total) * 1000
        
        successful = [r for r in results if r.get('success', False)]
        failed = len(results) - len(successful)
        
        if successful:
            times = [r['time_ms'] for r in successful]
            return {
                'total_requests': num_requests,
                'successful': len(successful),
                'failed': failed,
                'total_time_ms': total_time,
                'throughput_rps': len(successful) / (total_time / 1000),
                'avg_response_ms': statistics.mean(times),
                'min_ms': min(times),
                'max_ms': max(times),
                'p95_ms': sorted(times)[int(len(times) * 0.95)] if len(times) > 1 else times[0]
            }
        else:
            return {
                'total_requests': num_requests,
                'successful': 0,
                'failed': failed,
                'total_time_ms': total_time,
                'throughput_rps': 0
            }
    
    def run_all_tests(self):
        """Run all API performance tests"""
        print("=" * 60)
        print("🌐 API Performance Testing")
        print("=" * 60)
        print(f"Base URL: {self.base_url}")
        print("ℹ️  Note: Check-in endpoint test skipped (system uses live camera)")
        print()
        
        results = {}
        
        # Health endpoint
        results['health'] = self.test_health_endpoint(iterations=20)
        print(f"   Average: {results['health']['avg_ms']:.2f}ms")
        print()
        
        # Cameras endpoint
        results['cameras'] = self.test_cameras_endpoint(iterations=10)
        print(f"   Average: {results['cameras']['avg_ms']:.2f}ms")
        print()
        
        # Concurrent requests
        results['concurrent'] = self.test_concurrent_requests("/health", num_requests=50, concurrency=10)
        print(f"   Throughput: {results['concurrent']['throughput_rps']:.2f} req/s")
        print(f"   Success Rate: {results['concurrent']['successful']}/{results['concurrent']['total_requests']}")
        print()
        
        # Print summary
        self.print_summary(results)
        
        return results
    
    def print_summary(self, results: Dict):
        """Print API performance summary"""
        print("=" * 60)
        print("📊 API Performance Summary")
        print("=" * 60)
        print()
        
        print("Endpoint Response Times (Average):")
        if 'health' in results:
            print(f"  🏥 Health:              {results['health']['avg_ms']:>8.2f} ms")
        if 'cameras' in results:
            print(f"  📹 Cameras:             {results['cameras']['avg_ms']:>8.2f} ms")
        print("  ℹ️  Check-In:            (Skipped - uses live camera)")
        print()
        
        if 'concurrent' in results:
            print("Concurrent Performance:")
            print(f"  🔄 Throughput:          {results['concurrent']['throughput_rps']:>8.2f} req/s")
            print(f"  ✅ Success Rate:        {results['concurrent']['successful']}/{results['concurrent']['total_requests']}")
            print(f"  📊 P95 Response Time:   {results['concurrent'].get('p95_ms', 0):>8.2f} ms")
        print()


def main():
    parser = argparse.ArgumentParser(description='API Performance Testing')
    parser.add_argument('--base-url', type=str, default='http://localhost:8000',
                       help='Base URL of the API')
    parser.add_argument('--output', type=str, help='Output JSON file for results')
    
    args = parser.parse_args()
    
    tester = APIPerformanceTest(base_url=args.base_url)
    results = tester.run_all_tests()
    
    # Save results to JSON if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✅ Results saved to {args.output}")


if __name__ == "__main__":
    main()

