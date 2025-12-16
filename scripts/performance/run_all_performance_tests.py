"""
Run All Performance Tests

This script runs all performance benchmarks:
1. Model Performance (AI models)
2. API Performance
3. Database Performance

Usage:
    python scripts/performance/run_all_performance_tests.py
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add performance scripts to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from performance_benchmark import PerformanceBenchmark
    from api_performance_test import APIPerformanceTest
    from database_performance_test import DatabasePerformanceTest
except ImportError as e:
    print(f"Error importing test modules: {e}")
    print("Make sure all test scripts are in the scripts/performance/ directory")
    sys.exit(1)


def run_all_tests(
    api_base_url: str = "http://localhost:8000",
    iterations: int = 10,
    output_dir: str = "performance_results"
):
    """Run all performance tests and save results"""
    
    print("=" * 70)
    print("🚀 AI Attendance System - Complete Performance Test Suite")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    all_results = {
        'timestamp': datetime.now().isoformat(),
        'model_performance': {},
        'api_performance': {},
        'database_performance': {}
    }
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # 1. Model Performance Tests
    print("\n" + "=" * 70)
    print("PART 1: Model Performance Tests")
    print("=" * 70 + "\n")
    
    try:
        benchmark = PerformanceBenchmark()
        model_results = benchmark.run_all_benchmarks(
            iterations=iterations
        )
        all_results['model_performance'] = model_results
        
        # Save individual results
        with open(output_path / 'model_performance.json', 'w') as f:
            json.dump(model_results, f, indent=2)
        print(f"\n✅ Model performance results saved to {output_path / 'model_performance.json'}")
    except Exception as e:
        print(f"❌ Model performance test failed: {e}")
        all_results['model_performance'] = {'error': str(e)}
    
    # 2. API Performance Tests
    print("\n" + "=" * 70)
    print("PART 2: API Performance Tests")
    print("=" * 70 + "\n")
    print(f"⚠️  Make sure the API server is running at {api_base_url}")
    print()
    
    try:
        api_tester = APIPerformanceTest(base_url=api_base_url)
        api_results = api_tester.run_all_tests()
        all_results['api_performance'] = api_results
        
        # Save individual results
        with open(output_path / 'api_performance.json', 'w') as f:
            json.dump(api_results, f, indent=2)
        print(f"\n✅ API performance results saved to {output_path / 'api_performance.json'}")
    except Exception as e:
        print(f"❌ API performance test failed: {e}")
        print("   Make sure the API server is running")
        all_results['api_performance'] = {'error': str(e)}
    
    # 3. Database Performance Tests
    print("\n" + "=" * 70)
    print("PART 3: Database Performance Tests")
    print("=" * 70 + "\n")
    print("⚠️  Make sure the database is running and accessible")
    print()
    
    try:
        db_tester = DatabasePerformanceTest()
        db_results = db_tester.run_all_tests()
        all_results['database_performance'] = db_results
        
        # Only save if not skipped
        if not db_results.get('skipped'):
            # Save individual results
            with open(output_path / 'database_performance.json', 'w') as f:
                json.dump(db_results, f, indent=2)
            print(f"\n✅ Database performance results saved to {output_path / 'database_performance.json'}")
        else:
            print(f"\n⚠️  Database performance tests were skipped")
    except Exception as e:
        print(f"❌ Database performance test failed: {e}")
        print("   Make sure the database is set up and running")
        print("   If using Python 3.13, try: pip install --upgrade sqlalchemy>=2.0.30")
        all_results['database_performance'] = {'error': str(e)}
    
    # Save combined results
    output_file = output_path / f'complete_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Print final summary
    print("\n" + "=" * 70)
    print("📊 FINAL SUMMARY")
    print("=" * 70)
    print(f"\n✅ All results saved to: {output_path}")
    print(f"📄 Complete results: {output_file}")
    print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Quick summary
    if 'model_performance' in all_results and 'end_to_end' in all_results['model_performance']:
        e2e_time = all_results['model_performance']['end_to_end'].get('avg_ms', 0)
        print(f"⚡ End-to-End Pipeline: {e2e_time:.2f}ms")
    
    if 'api_performance' in all_results and 'concurrent' in all_results['api_performance']:
        throughput = all_results['api_performance']['concurrent'].get('throughput_rps', 0)
        print(f"🌐 API Throughput: {throughput:.2f} req/s")
    
    if 'database_performance' in all_results and 'embedding_search' in all_results['database_performance']:
        search_time = all_results['database_performance']['embedding_search'].get('avg_ms', 0)
        if search_time > 0:
            print(f"🗄️  Embedding Search: {search_time:.2f}ms")
    
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Run all performance tests for AI Attendance System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests with default settings
  python scripts/performance/run_all_performance_tests.py

  # Run with custom API URL
  python scripts/performance/run_all_performance_tests.py --api-url http://localhost:8000

  # Run with more iterations
  python scripts/performance/run_all_performance_tests.py --iterations 20
        """
    )
    
    parser.add_argument('--api-url', type=str, default='http://localhost:8000',
                       help='Base URL of the API server')
    parser.add_argument('--iterations', type=int, default=10,
                       help='Number of iterations for model benchmarks')
    parser.add_argument('--output-dir', type=str, default='performance_results',
                       help='Directory to save results')
    
    args = parser.parse_args()
    
    run_all_tests(
        api_base_url=args.api_url,
        iterations=args.iterations,
        output_dir=args.output_dir
    )


if __name__ == "__main__":
    main()

