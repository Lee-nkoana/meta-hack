#!/usr/bin/env python3
"""
Demo script for training data upload and OCR feedback
Shows how to:
1. Upload medical images for OCR training
2. Submit corrections to improve OCR accuracy
3. Check training statistics
"""
import requests
import json
import base64
import sys
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"


def get_auth_token(username: str = "testuser", password: str = "testpassword"):
    """Login and get JWT token"""
    print(f"🔐 Logging in as {username}...")
    
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"username": username, "password": password}
    )
    
    if response.status_code == 200:
        token = response.json()['access_token']
        print(f"✅ Successfully logged in!\n")
        return token
    else:
        print(f"❌ Login failed: {response.json()}")
        sys.exit(1)


def upload_training_image(token: str, image_path: str, image_type: str = "printed"):
    """Upload a medical image for OCR training"""
    print(f"📤 Uploading image: {image_path}")
    print(f"   Type: {image_type}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
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
    
    if response.status_code == 201:
        result = response.json()
        training_image = result['training_image']
        ocr_result = result['ocr_result']
        
        print(f"✅ Upload successful!")
        print(f"   Image ID: {training_image['id']}")
        print(f"   OCR Confidence: {ocr_result['confidence']:.2%}")
        print(f"\n📝 Extracted Text:")
        print(f"   {ocr_result['extracted_text'][:200]}...")
        
        if ocr_result['medications_detected']:
            print(f"\n💊 Medications Detected:")
            for med in ocr_result['medications_detected']:
                print(f"   - {med}")
        
        return training_image['id'], ocr_result
    else:
        print(f"❌ Upload failed: {response.json()}")
        return None, None


def submit_ocr_correction(token: str, image_id: int, corrected_text: str):
    """Submit corrected text for OCR feedback"""
    print(f"\n📝 Submitting OCR correction for image {image_id}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{API_BASE}/training/{image_id}/feedback",
        headers=headers,
        json={"corrected_text": corrected_text}
    )
    
    if response.status_code == 200:
        print(f"✅ Correction submitted successfully!")
        return True
    else:
        print(f"❌ Correction failed: {response.json()}")
        return False


def get_training_stats(token: str):
    """Get OCR training statistics"""
    print(f"\n📊 Fetching training statistics...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{API_BASE}/training/stats",
        headers=headers
    )
    
    if response.status_code == 200:
        stats = response.json()
        print(f"\n{'='*50}")
        print(f"TRAINING STATISTICS")
        print(f"{'='*50}")
        print(f"Total Images: {stats['total_images']}")
        print(f"Average OCR Confidence: {stats['average_confidence']:.2%}" if stats['average_confidence'] else "N/A")
        print(f"Images Corrected: {stats['images_corrected']}")
        print(f"\nImages by Type:")
        for img_type, count in stats['by_type'].items():
            print(f"  {img_type.capitalize()}: {count}")
        print(f"{'='*50}\n")
        return stats
    else:
        print(f"❌ Failed to get stats: {response.json()}")
        return None


def create_sample_medical_note(output_path: str = "sample_medical_note.txt"):
    """Create a sample medical note for demo purposes"""
    sample_text = """
MEDICAL RECORD

Patient: John Doe
Date: December 12, 2024

Chief Complaint: High blood pressure and diabetes management

Current Medications:
- Lisinopril 10mg once daily (for hypertension)
- Metformin 500mg twice daily (for type 2 diabetes)
- Aspirin 81mg once daily (cardiovascular protection)

Assessment:
Blood pressure controlled at 128/82 mmHg.
HbA1c at 6.8%, improved from previous 7.2%.

Plan:
Continue current medication regimen.
Follow-up in 3 months.
Advised on diet and exercise.

Dr. Smith
    """
    
    with open(output_path, 'w') as f:
        f.write(sample_text.strip())
    
    print(f"📄 Created sample medical note: {output_path}")
    return output_path


def demo_full_workflow():
    """Demonstrate complete training workflow"""
    print("\n" + "="*60)
    print("TRAINING DATA UPLOAD DEMO")
    print("="*60 + "\n")
    
    # Step 1: Login
    token = get_auth_token()
    
    # Step 2: Create sample note (if no image provided)
    print("📄 For this demo, you can upload any medical image.")
    print("   If you don't have one, I'll create a sample text note.\n")
    
    # You can replace this with an actual image path
    sample_note = create_sample_medical_note()
    
    # Step 3: Upload image
    # Note: If you have a real medical image, replace sample_note with its path
    image_path = input(f"Enter image path (or press Enter to use {sample_note}): ").strip()
    if not image_path:
        print(f"\n⚠️  Note: Using text file for demo. In production, use actual images!")
        image_path = sample_note
        image_type = "printed"
    else:
        image_type = input("Image type (printed/handwritten/mixed): ").strip() or "printed"
    
    if not os.path.exists(image_path):
        print(f"❌ File not found: {image_path}")
        return
    
    image_id, ocr_result = upload_training_image(token, image_path, image_type)
    
    if not image_id:
        return
    
    # Step 4: Optionally submit correction
    print(f"\n{'='*60}")
    print("OPTIONAL: Submit OCR Correction")
    print(f"{'='*60}")
    print("Did the OCR make any mistakes?")
    submit_correction = input("Submit a correction? (y/N): ").strip().lower()
    
    if submit_correction == 'y':
        print("\nEnter the corrected text (press Enter twice when done):")
        lines = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        
        corrected_text = "\n".join(lines[:-1])  # Remove last empty line
        submit_ocr_correction(token, image_id, corrected_text)
    
    # Step 5: View statistics
    get_training_stats(token)
    
    print(f"\n{'='*60}")
    print("✅ DEMO COMPLETE!")
    print(f"{'='*60}")
    print("\nNext steps:")
    print("1. Upload more medical images to build training dataset")
    print("2. Correct OCR errors to improve accuracy")
    print("3. Use batch upload script for multiple images")
    print("4. Monitor training stats to track progress\n")


def demo_medication_extraction():
    """Demo: Extract medications from text"""
    print("\n" + "="*60)
    print("MEDICATION EXTRACTION DEMO")
    print("="*60 + "\n")
    
    sample_texts = [
        "Patient is taking aspirin and metformin daily",
        "Prescribed lisinopril for hypertension management",
        "Discontinued Zantac due to recall, switched to omeprazole"
    ]
    
    for i, text in enumerate(sample_texts, 1):
        print(f"\n{i}. Testing: \"{text}\"")
        
        response = requests.post(
            f"{API_BASE}/medications/extract",
            json={"text": text}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Found {result['count']} medication(s):")
            for med in result['medications_found']:
                status = "⚠️ DISCONTINUED" if med['discontinued'] else "✅ Active"
                print(f"   - {med['name']} ({status})")
                if med['warning']:
                    print(f"     Warning: {med['discontinuation_reason']}")
        print("-" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Training data upload demo")
    parser.add_argument("--demo", choices=['full', 'extract'], default='full',
                       help="Demo type: full workflow or medication extraction")
    
    args = parser.parse_args()
    
    if args.demo == 'full':
        demo_full_workflow()
    elif args.demo == 'extract':
        demo_medication_extraction()
