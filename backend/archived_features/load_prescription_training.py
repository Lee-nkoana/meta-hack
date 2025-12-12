#!/usr/bin/env python3
"""
Load handwritten prescription training data into the system
Processes word-level images of medication names with labels
"""
import sys
import os
import csv
import base64

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import create_app
from app.database import get_db
from app.models.training_image import TrainingImage
from app.models.medication import Medication


def load_prescription_training_data(split='Training', limit=None):
    """
    Load handwritten prescription dataset
    
    Args:
        split: 'Training', 'Testing', or 'Validation'
        limit: Maximum number of images to load (None for all)
    """
    app = create_app()
    
    with app.app_context():
        db = get_db()
        
        # Use renamed directory
        dataset_base = os.path.join("data", "doctor_notes")
        split_path = os.path.join(dataset_base, split)
        csv_file = os.path.join(split_path, f"{split.lower()}_labels.csv")
        images_dir = os.path.join(split_path, f"{split.lower()}_words")
        
        # Verify paths exist
        if not os.path.exists(csv_file):
            print(f"❌ CSV file not found: {csv_file}")
            if os.path.exists(split_path):
                print(f"   Files in {split_path}:")
                for f in os.listdir(split_path):
                    print(f"      - {f}")
            return
        
        if not os.path.exists(images_dir):
            print(f"❌ Images directory not found: {images_dir}")
            return
        
        print(f"\n{'='*70}")
        print(f"Loading {split} Dataset - Handwritten Prescription Words")
        print(f"{'='*70}\n")
        
        # Read CSV
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        total_rows = len(rows)
        if limit:
            rows = rows[:limit]
        
        print(f"Found {total_rows} labeled images")
        if limit:
            print(f"Processing first {limit} images\n")
        else:
            print()
        
        # Process each image
        loaded_count = 0
        skipped_count = 0
        medication_updates = 0
        
        for i, row in enumerate(rows, 1):
            image_filename = row['IMAGE']
            medicine_name = row['MEDICINE_NAME']
            generic_name = row['GENERIC_NAME']
            
            image_path = os.path.join(images_dir, image_filename)
            
            if not os.path.exists(image_path):
                print(f"⚠️  Skipping {image_filename}: file not found")
                skipped_count += 1
                continue
            
            # Read and encode image
            with open(image_path, 'rb') as img_file:
                image_bytes = img_file.read()
                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Check if already exists
            existing = db.query(TrainingImage).filter(
                TrainingImage.image_data == image_b64
            ).first()
            
            if existing:
                skipped_count += 1
                continue
            
            # Create training image entry
            training_image = TrainingImage(
                image_data=image_b64,
                extracted_text=medicine_name,  # What was written
                corrected_text=f"{medicine_name} ({generic_name})",  # Full label
                image_type='handwritten',
                is_training_data=True,
                ocr_confidence=None  # Will be set when OCR is run
            )
            
            db.add(training_image)
            loaded_count += 1
            
            # Also check/update medication database
            # Look for generic name in medications
            if generic_name:
                existing_med = db.query(Medication).filter(
                    Medication.name == generic_name
                ).first()
                
                if not existing_med:
                    # Create new medication entry
                    try:
                        new_med = Medication(
                            name=generic_name,
                            discontinued=False
                        )
                        db.add(new_med)
                        db.flush()  # Flush to catch uniqueness constraint
                        medication_updates += 1
                    except Exception as e:
                        # Likely duplicate, skip
                        db.rollback()
                        pass
            
            # Progress
            if i % 100 == 0:
                print(f"Processed: {i}/{len(rows)} images ({loaded_count} new, {skipped_count} skipped)")
                db.commit()
        
        # Final commit
        db.commit()
        
        # Print summary
        print(f"\n{'='*70}")
        print("LOADING COMPLETE")
        print(f"{'='*70}")
        print(f"✅ Loaded: {loaded_count} new training images")
        print(f"⏭️  Skipped: {skipped_count} duplicates")
        print(f"💊 Medications added/updated: {medication_updates}")
        
        # Get total stats
        total_training = db.query(TrainingImage).filter(
            TrainingImage.is_training_data == True
        ).count()
        total_handwritten = db.query(TrainingImage).filter(
            TrainingImage.image_type == 'handwritten'
        ).count()
        
        print(f"\n📊 Database Stats:")
        print(f"   Total training images: {total_training}")
        print(f"   Handwritten images: {total_handwritten}")
        print(f"{'='*70}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load handwritten prescription training data")
    parser.add_argument('--split', choices=['Training', 'Testing', 'Validation'], 
                       default='Training',
                       help='Dataset split to load')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of images to load (for testing)')
    parser.add_argument('--all', action='store_true',
                       help='Load all splits (Training, Testing, Validation)')
    
    args = parser.parse_args()
    
    if args.all:
        for split in ['Training', 'Testing', 'Validation']:
            load_prescription_training_data(split, args.limit)
    else:
        load_prescription_training_data(args.split, args.limit)
