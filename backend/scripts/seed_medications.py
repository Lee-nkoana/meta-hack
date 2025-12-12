#!/usr/bin/env python3
"""
Seed medications data from JSON and JSONL files into database
"""
import sys
import os
import json
import re

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import create_app
from app.database import get_db
from app.services.medication_service import medication_service


def extract_medication_from_jsonl_line(line_data):
    """
    Extract medication information from a JSONL training line
    Format: {"prompt": "What are the uses of MedicationName?", "completion": "..."}
    """
    prompt = line_data.get('prompt', '')
    completion = line_data.get('completion', '')
    
    # Extract medication name from prompt
    # Pattern: "What are the uses of MedicationName?" or "What interactions does MedicationName have?"
    name_match = re.search(r'(?:uses of|interactions does|side effects of)\s+([^?]+?)\s*(?:\?|have)', prompt)
    
    if not name_match:
        return None
    
    med_name = name_match.group(1).strip()
    
    # Skip generic questions or non-medication entries
    if not med_name or len(med_name) < 2:
        return None
    
    # Determine what type of information this is
    medication_data = {
        'name': med_name,
        'uses': None,
        'side_effects': None,
        'discontinued': False,
        'discontinuation_reason': None
    }
    
    # Extract uses
    if 'uses' in prompt.lower():
        medication_data['uses'] = completion[:500] if len(completion) > 500 else completion
    
    # Extract side effects
    if 'side effects' in prompt.lower():
        medication_data['side_effects'] = completion[:500] if len(completion) > 500 else completion
    
    return medication_data


def merge_medication_data(existing_meds, new_med):
    """Merge new medication data into existing medications dictionary"""
    name = new_med['name']
    
    if name not in existing_meds:
        existing_meds[name] = new_med
    else:
        # Merge: update fields if new data has more info
        if new_med.get('uses') and not existing_meds[name].get('uses'):
            existing_meds[name]['uses'] = new_med['uses']
        if new_med.get('side_effects') and not existing_meds[name].get('side_effects'):
            existing_meds[name]['side_effects'] = new_med['side_effects']


def seed_medications():
    """Load medications from JSON and JSONL files and seed into database"""
    app = create_app()
    
    with app.app_context():
        db = get_db()
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        
        all_medications = {}
        
        # 1. Load from medications_data.json
        json_path = os.path.join(data_dir, 'medications_data.json')
        if os.path.exists(json_path):
            print(f"Loading medications from {json_path}...")
            with open(json_path, 'r') as f:
                json_meds = json.load(f)
            
            print(f"Found {len(json_meds)} medications in JSON file")
            for med in json_meds:
                all_medications[med['name']] = med
        
        # 2. Load from medications_training.jsonl
        jsonl_path = os.path.join(data_dir, 'medications_training.jsonl')
        if os.path.exists(jsonl_path):
            print(f"\nLoading medications from {jsonl_path}...")
            processed = 0
            unique_meds = set()
            
            with open(jsonl_path, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            line_data = json.loads(line)
                            med_data = extract_medication_from_jsonl_line(line_data)
                            
                            if med_data:
                                merge_medication_data(all_medications, med_data)
                                unique_meds.add(med_data['name'])
                                processed += 1
                        except json.JSONDecodeError:
                            continue
            
            print(f"Processed {processed} training entries")
            print(f"Found {len(unique_meds)} unique medications in JSONL file")
        
        # Convert dict to list for bulk creation
        medications_list = list(all_medications.values())
        
        print(f"\n{'='*50}")
        print(f"Total unique medications to seed: {len(medications_list)}")
        print(f"{'='*50}\n")
        
        # Bulk create/update medications
        results = medication_service.bulk_create_medications(db, medications_list, update_existing=True)
        
        # Get total count
        from app.models.medication import Medication
        total_count = db.query(Medication).count()
        
        print("\n" + "=" * 50)
        print("MEDICATION SEEDING COMPLETE")
        print("=" * 50)
        print(f"✅ Created: {results['created']} new medications")
        print(f"🔄 Updated: {results['updated']} medications with new data")
        print(f"⏭️  Skipped: {results['skipped']} medications (no changes)")
        print(f"📊 Total medications in database: {total_count}")
        print("=" * 50 + "\n")
        
        # Show sample medications
        sample_meds = db.query(Medication).limit(10).all()
        print("Sample medications:")
        for med in sample_meds:
            discontinued_str = " [DISCONTINUED]" if med.discontinued else ""
            uses_preview = (med.uses[:50] + "...") if med.uses and len(med.uses) > 50 else (med.uses or "N/A")
            print(f"  - {med.name}{discontinued_str}")
            print(f"    Uses: {uses_preview}")


if __name__ == "__main__":
    seed_medications()
