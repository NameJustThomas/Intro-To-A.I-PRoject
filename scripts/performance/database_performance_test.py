"""
Database Performance Testing Script

Measures:
1. Query execution time
2. Connection pool performance
3. Database write performance
4. Index effectiveness

Usage:
    python scripts/performance/database_performance_test.py
"""

import time
import sys
from pathlib import Path
from typing import Dict, List
import statistics

# Add backend to path (go up 2 levels: performance -> scripts -> project root)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

try:
    from app.db.base import SessionLocal, engine
    from app.models.orm_models import (
        Employee, FaceEmbedding, AttendanceLog, 
        Camera, Store, Schedule
    )
    from sqlalchemy import text
    DB_AVAILABLE = True
except (ImportError, AssertionError) as e:
    print(f"⚠️  Warning: Database modules cannot be imported: {e}")
    print("   This may be due to SQLAlchemy compatibility issues with Python 3.13.")
    print("   Try upgrading SQLAlchemy: pip install --upgrade sqlalchemy>=2.0.30")
    print("   Database performance tests will be skipped.")
    DB_AVAILABLE = False


class DatabasePerformanceTest:
    def __init__(self):
        if not DB_AVAILABLE:
            self.db = None
            self.results = {}
            return
        try:
            self.db = SessionLocal()
            self.results = {}
        except Exception as e:
            print(f"Error creating database session: {e}")
            self.db = None
            self.results = {}
    
    def __del__(self):
        if hasattr(self, 'db') and self.db is not None:
            try:
                self.db.close()
            except:
                pass
    
    def test_simple_query(self, iterations: int = 10) -> Dict:
        """Test simple SELECT query"""
        print("📊 Testing Simple Query (SELECT employees)...")
        times = []
        
        for i in range(iterations):
            start = time.perf_counter()
            try:
                employees = self.db.query(Employee).limit(100).all()
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)
            except Exception as e:
                print(f"  Error: {e}")
        
        if not times:
            return {'avg_ms': 0}
        
        return {
            'avg_ms': statistics.mean(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'std_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'iterations': len(times)
        }
    
    def test_join_query(self, iterations: int = 10) -> Dict:
        """Test JOIN query"""
        print("🔗 Testing JOIN Query (Employee with FaceEmbedding)...")
        times = []
        
        for i in range(iterations):
            start = time.perf_counter()
            try:
                results = self.db.query(Employee, FaceEmbedding).join(
                    FaceEmbedding, Employee.id == FaceEmbedding.employee_id
                ).limit(100).all()
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)
            except Exception as e:
                print(f"  Error: {e}")
        
        if not times:
            return {'avg_ms': 0}
        
        return {
            'avg_ms': statistics.mean(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'std_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'iterations': len(times)
        }
    
    def test_filter_query(self, iterations: int = 10) -> Dict:
        """Test filtered query"""
        print("🔍 Testing Filtered Query (AttendanceLog by date)...")
        times = []
        
        for i in range(iterations):
            start = time.perf_counter()
            try:
                from datetime import datetime, timedelta
                date_from = datetime.now() - timedelta(days=30)
                logs = self.db.query(AttendanceLog).filter(
                    AttendanceLog.timestamp >= date_from
                ).limit(100).all()
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)
            except Exception as e:
                print(f"  Error: {e}")
        
        if not times:
            return {'avg_ms': 0}
        
        return {
            'avg_ms': statistics.mean(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'std_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'iterations': len(times)
        }
    
    def test_embedding_search(self, iterations: int = 10) -> Dict:
        """Test embedding search (linear search through all embeddings)"""
        print("🔎 Testing Embedding Search (Linear Search)...")
        times = []
        
        # Get all embeddings
        try:
            all_embeddings = self.db.query(FaceEmbedding).all()
            if not all_embeddings:
                print("  ⚠️  No embeddings found in database")
                return {'avg_ms': 0, 'skipped': True}
        except Exception as e:
            print(f"  Error: {e}")
            return {'avg_ms': 0}
        
        # Create a dummy embedding for search
        import numpy as np
        test_embedding = np.random.rand(512).astype(np.float32)
        
        for i in range(iterations):
            start = time.perf_counter()
            try:
                # Simulate linear search
                best_match = None
                best_similarity = 0
                for fe in all_embeddings:
                    stored_vec = np.frombuffer(fe.embedding, dtype=np.float32)
                    similarity = np.dot(test_embedding, stored_vec) / (
                        np.linalg.norm(test_embedding) * np.linalg.norm(stored_vec) + 1e-8
                    )
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = fe
                
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)
            except Exception as e:
                print(f"  Error: {e}")
        
        if not times:
            return {'avg_ms': 0}
        
        return {
            'avg_ms': statistics.mean(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'std_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'num_embeddings': len(all_embeddings),
            'iterations': len(times)
        }
    
    def test_write_performance(self, iterations: int = 5) -> Dict:
        """Test database write performance"""
        print("✍️  Testing Write Performance...")
        times = []
        
        # Get a test employee
        test_employee = self.db.query(Employee).first()
        if not test_employee:
            print("  ⚠️  No employees found, skipping write test")
            return {'avg_ms': 0, 'skipped': True}
        
        # Get a test camera
        test_camera = self.db.query(Camera).first()
        if not test_camera:
            print("  ⚠️  No cameras found, skipping write test")
            return {'avg_ms': 0, 'skipped': True}
        
        for i in range(iterations):
            start = time.perf_counter()
            try:
                from datetime import datetime
                log = AttendanceLog(
                    employee_id=test_employee.id,
                    camera_id=test_camera.id,
                    timestamp=datetime.now(),
                    confidence=0.95,
                    location_validated=True
                )
                self.db.add(log)
                self.db.commit()
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)
                
                # Clean up - delete the test log
                self.db.delete(log)
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                print(f"  Error: {e}")
        
        if not times:
            return {'avg_ms': 0}
        
        return {
            'avg_ms': statistics.mean(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'std_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'iterations': len(times)
        }
    
    def test_connection_pool(self, iterations: int = 20) -> Dict:
        """Test connection pool performance"""
        print("🔌 Testing Connection Pool...")
        times = []
        
        for i in range(iterations):
            start = time.perf_counter()
            try:
                # Create new session to test pool
                db = SessionLocal()
                db.query(Employee).first()
                db.close()
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)
            except Exception as e:
                print(f"  Error: {e}")
        
        if not times:
            return {'avg_ms': 0}
        
        return {
            'avg_ms': statistics.mean(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'std_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'iterations': len(times)
        }
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        print("📈 Getting Database Statistics...")
        stats = {}
        
        try:
            stats['employees'] = self.db.query(Employee).count()
            stats['face_embeddings'] = self.db.query(FaceEmbedding).count()
            stats['attendance_logs'] = self.db.query(AttendanceLog).count()
            stats['cameras'] = self.db.query(Camera).count()
            stats['stores'] = self.db.query(Store).count()
            stats['schedules'] = self.db.query(Schedule).count()
        except Exception as e:
            print(f"  Error: {e}")
        
        return stats
    
    def run_all_tests(self):
        """Run all database performance tests"""
        print("=" * 60)
        print("🗄️  Database Performance Testing")
        print("=" * 60)
        print()
        
        if not DB_AVAILABLE:
            print("❌ Database tests skipped due to import errors.")
            print("   Please upgrade SQLAlchemy: pip install --upgrade sqlalchemy>=2.0.30")
            return {'error': 'Database modules not available', 'skipped': True}
        
        # Get database stats
        stats = self.get_database_stats()
        print("Database Statistics:")
        for key, value in stats.items():
            print(f"  {key.capitalize()}: {value}")
        print()
        
        results = {}
        
        # Simple query
        results['simple_query'] = self.test_simple_query(iterations=20)
        print(f"   Average: {results['simple_query']['avg_ms']:.2f}ms")
        print()
        
        # Join query
        results['join_query'] = self.test_join_query(iterations=10)
        print(f"   Average: {results['join_query']['avg_ms']:.2f}ms")
        print()
        
        # Filter query
        results['filter_query'] = self.test_filter_query(iterations=10)
        print(f"   Average: {results['filter_query']['avg_ms']:.2f}ms")
        print()
        
        # Embedding search
        results['embedding_search'] = self.test_embedding_search(iterations=5)
        if not results['embedding_search'].get('skipped'):
            print(f"   Average: {results['embedding_search']['avg_ms']:.2f}ms")
            print(f"   Embeddings searched: {results['embedding_search'].get('num_embeddings', 0)}")
        print()
        
        # Write performance
        results['write'] = self.test_write_performance(iterations=5)
        if not results['write'].get('skipped'):
            print(f"   Average: {results['write']['avg_ms']:.2f}ms")
        print()
        
        # Connection pool
        results['connection_pool'] = self.test_connection_pool(iterations=20)
        print(f"   Average: {results['connection_pool']['avg_ms']:.2f}ms")
        print()
        
        # Print summary
        self.print_summary(results, stats)
        
        return results
    
    def print_summary(self, results: Dict, stats: Dict):
        """Print database performance summary"""
        print("=" * 60)
        print("📊 Database Performance Summary")
        print("=" * 60)
        print()
        
        print("Query Performance (Average):")
        if 'simple_query' in results:
            print(f"  📊 Simple Query:        {results['simple_query']['avg_ms']:>8.2f} ms")
        if 'join_query' in results:
            print(f"  🔗 JOIN Query:           {results['join_query']['avg_ms']:>8.2f} ms")
        if 'filter_query' in results:
            print(f"  🔍 Filtered Query:       {results['filter_query']['avg_ms']:>8.2f} ms")
        if 'embedding_search' in results and not results['embedding_search'].get('skipped'):
            print(f"  🔎 Embedding Search:     {results['embedding_search']['avg_ms']:>8.2f} ms")
            print(f"     (Searched {results['embedding_search'].get('num_embeddings', 0)} embeddings)")
        print()
        
        print("Write Performance:")
        if 'write' in results and not results['write'].get('skipped'):
            print(f"  ✍️  Write Operation:      {results['write']['avg_ms']:>8.2f} ms")
        print()
        
        print("Connection Pool:")
        if 'connection_pool' in results:
            print(f"  🔌 Connection Time:      {results['connection_pool']['avg_ms']:>8.2f} ms")
        print()


def main():
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='Database Performance Testing')
    parser.add_argument('--output', type=str, help='Output JSON file for results')
    
    args = parser.parse_args()
    
    tester = DatabasePerformanceTest()
    results = tester.run_all_tests()
    
    # Save results to JSON if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✅ Results saved to {args.output}")


if __name__ == "__main__":
    main()

