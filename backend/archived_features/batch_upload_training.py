#!/usr/bin/env python3
"""
Batch upload training images from a folder
Processes entire directories of medical images for OCR training
"""
import requests
import json
import os
import sys
from pathlib import Path
from typing import List, Dict
import time
import mimetypes

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

# Supported image formats
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}


def get_auth_token(username: str = "testuser", password: str = "testpassword"):
    """Login and get JWT token"""
    print(f"🔐 Authenticating as {username}...")
    
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"username": username, "password": password}
    )
    
    if response.status_code == 200:
        token = response.json()['access_token']
        print(f"✅ Authentication successful!\n")
        return token
    else:
        print(f"❌ Authentication failed: {response.json()}")
        sys.exit(1)


def find_images_in_folder(folder_path: str) -> List[Path]:
    """Recursively find all images in folder"""
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"❌ Folder not found: {folder_path}")
        return []
    
    images = []
    for ext in IMAGE_EXTENSIONS:
        images.extend(folder.rglob(f"*{ext}"))
        images.extend(folder.rglob(f"*{ext.upper()}"))
    
    return sorted(images)


def detect_image_type(image_path: Path) -> str:
    """
    Try to detect if image is handwritten or printed
    Default to 'printed' if uncertain
    You can enhance this with ML model or manual categorization
    """
    # Simple heuristic: check folder name or filename
    path_str = str(image_path).lower()
    
    if 'handwritten' in path_str or 'hand' in path_str:
        return 'handwritten'
    elif 'mixed' in path_str:
        return 'mixed'
    else:
        return 'printed'


def upload_single_image(
    token: str, 
    image_path: Path, 
    image_type: str,
    delay: float = 0.5
) -> Dict:
    """Upload a single training image"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        with open(image_path, 'rb') as f:
            files = {'image': (image_path.name, f, mimetypes.guess_type(str(image_path))[0])}
            data = {
                'image_type': image_type,
                'is_training_data': 'true'
            }
            
            response = requests.post(
                f"{API_BASE}/training/upload",
                headers=headers,
                files=files,
                data=data
            )
        
        # Add small delay to avoid overwhelming server
        time.sleep(delay)
        
        if response.status_code == 201:
            result = response.json()
            return {
                'success': True,
                'image_id': result['training_image']['id'],
                'confidence': result['ocr_result']['confidence'],
                'medications': result['ocr_result']['medications_detected'],
                'text_length': len(result['ocr_result']['extracted_text'] or '')
            }
        else:
            return {
                'success': False,
                'error': response.json().get('error', 'Unknown error')
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def batch_upload_images(
    token: str, 
    folder_path: str,
    image_type: str = 'auto',
    max_images: int = None,
    delay: float = 0.5
):
    """Batch upload all images from folder"""
    
    print(f"\n{'='*70}")
    print(f"BATCH TRAINING IMAGE UPLOAD")
    print(f"{'='*70}")
    print(f"Source Folder: {folder_path}")
    print(f"Image Type: {image_type}")
    print(f"{'='*70}\n")
    
    # Find all images
    print("🔍 Scanning for images...")
    images = find_images_in_folder(folder_path)
    
    if not images:
        print(f"❌ No images found in {folder_path}")
        print(f"   Supported formats: {', '.join(IMAGE_EXTENSIONS)}")
        return
    
    if max_images:
        images = images[:max_images]
    
    print(f"✅ Found {len(images)} image(s) to upload\n")
    
    # Confirm upload
    confirm = input(f"Proceed with batch upload? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Upload cancelled")
        return
    
    # Upload progress tracking
    results = {
        'successful': 0,
        'failed': 0,
        'total_medications': 0,
        'avg_confidence': 0.0,
        'errors': []
    }
    
    confidences = []
    
    print(f"\n{'='*70}")
    print("UPLOADING IMAGES")
    print(f"{'='*70}\n")
    
    for i, image_path in enumerate(images, 1):
        # Auto-detect image type if needed
        if image_type == 'auto':
            current_type = detect_image_type(image_path)
        else:
            current_type = image_type
        
        print(f"[{i}/{len(images)}] 📤 {image_path.name} ({current_type})... ", end='')
        
        result = upload_single_image(token, image_path, current_type, delay)
        
        if result['success']:
            print(f"✅ Success!")
            print(f"         ID: {result['image_id']} | "
                  f"Confidence: {result['confidence']:.1%} | "
                  f"Meds: {len(result['medications'])} | "
                  f"Text: {result['text_length']} chars")
            
            results['successful'] += 1
            results['total_medications'] += len(result['medications'])
            confidences.append(result['confidence'])
            
            if result['medications']:
                print(f"         💊 {', '.join(result['medications'])}")
        else:
            print(f"❌ Failed: {result['error']}")
            results['failed'] += 1
            results['errors'].append({
                'file': image_path.name,
                'error': result['error']
            })
        
        print()
    
    # Calculate stats
    if confidences:
        results['avg_confidence'] = sum(confidences) / len(confidences)
    
    # Print summary
    print(f"\n{'='*70}")
    print("UPLOAD SUMMARY")
    print(f"{'='*70}")
    print(f"✅ Successful: {results['successful']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"📊 Average OCR Confidence: {results['avg_confidence']:.1%}")
    print(f"💊 Total Medications Detected: {results['total_medications']}")
    print(f"{'='*70}\n")
    
    if results['errors']:
        print("⚠️  Failed uploads:")
        for error in results['errors']:
            print(f"   - {error['file']}: {error['error']}")
        print()
    
    # Get updated stats
    print("📊 Fetching updated training statistics...")
    response = requests.get(
        f"{API_BASE}/training/stats",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        stats = response.json()
        print(f"\nTotal Training Images: {stats['total_images']}")
        print(f"Overall Avg Confidence: {stats['average_confidence']:.1%}" if stats['average_confidence'] else "N/A")
        print("\nImages by Type:")
        for img_type, count in stats['by_type'].items():
            print(f"  {img_type.capitalize()}: {count}")
        print()


def export_training_manifest(folder_path: str, output_file: str = "training_manifest.json"):
    """Create a manifest file of all images for tracking"""
    images = find_images_in_folder(folder_path)
    
    manifest = {
        'folder': str(folder_path),
        'total_images': len(images),
        'images': []
    }
    
    for img in images:
        manifest['images'].append({
            'filename': img.name,
            'path': str(img),
            'size_bytes': img.stat().st_size,
            'detected_type': detect_image_type(img)
        })
    
    with open(output_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"📄 Manifest created: {output_file}")
    print(f"   {len(images)} images catalogued")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Batch upload medical images for OCR training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload all images from a folder (auto-detect type)
  python batch_upload_training.py /path/to/images

  # Upload with specific type
  python batch_upload_training.py /path/to/images --type handwritten

  # Upload only first 10 images
  python batch_upload_training.py /path/to/images --max 10

  # Create manifest only (don't upload)
  python batch_upload_training.py /path/to/images --manifest-only

  # Custom credentials
  python batch_upload_training.py /path/to/images --username admin --password secret
        """
    )
    
    parser.add_argument("folder", help="Folder containing medical images")
    parser.add_argument("--type", "-t", 
                       choices=['auto', 'printed', 'handwritten', 'mixed'],
                       default='auto',
                       help="Image type (default: auto-detect from path)")
    parser.add_argument("--max", "-m", type=int,
                       help="Maximum number of images to upload")
    parser.add_argument("--delay", "-d", type=float, default=0.5,
                       help="Delay between uploads in seconds (default: 0.5)")
    parser.add_argument("--username", "-u", default="testuser",
                       help="Username for authentication")
    parser.add_argument("--password", "-p", default="testpassword",
                       help="Password for authentication")
    parser.add_argument("--manifest-only", action="store_true",
                       help="Only create manifest file, don't upload")
    
    args = parser.parse_args()
    
    if args.manifest_only:
        export_training_manifest(args.folder)
    else:
        token = get_auth_token(args.username, args.password)
        batch_upload_images(
            token, 
            args.folder,
            args.type,
            args.max,
            args.delay
        )
