"""
Helper script to create a store and camera in the database.
Usage: python scripts/create_store.py --name "Main Store" --address "123 Main St" --camera_name "Camera 1" --location "Entrance"
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.models.orm_models import Store, Camera


def create_store_with_camera(name: str, address: str, camera_name: str, location: str, rtsp_url: str = None):
    """Create a new store with a camera in the database."""
    db = SessionLocal()
    try:
        # Create store
        store = Store(name=name, address=address)
        db.add(store)
        db.flush()  # Get store ID
        
        # Create camera
        camera = Camera(
            store_id=store.id,
            name=camera_name,
            location=location,
            rtsp_url=rtsp_url or ""
        )
        db.add(camera)
        db.commit()
        db.refresh(store)
        db.refresh(camera)
        
        print(f"Store and camera created successfully:")
        print(f"  Store ID: {store.id}")
        print(f"  Store Name: {store.name}")
        print(f"  Store Address: {store.address}")
        print(f"  Camera ID: {camera.id}")
        print(f"  Camera Name: {camera.name}")
        print(f"  Camera Location: {camera.location}")
        return True
        
    except Exception as e:
        print(f"Error creating store/camera: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description='Create a new store with camera')
    parser.add_argument('--name', required=True, help='Store name')
    parser.add_argument('--address', required=True, help='Store address')
    parser.add_argument('--camera_name', required=True, help='Camera name')
    parser.add_argument('--location', required=True, help='Camera location')
    parser.add_argument('--rtsp_url', help='RTSP URL for camera stream')
    
    args = parser.parse_args()
    
    success = create_store_with_camera(
        args.name, 
        args.address, 
        args.camera_name, 
        args.location,
        args.rtsp_url
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

