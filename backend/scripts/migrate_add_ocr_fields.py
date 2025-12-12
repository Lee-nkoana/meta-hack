#!/usr/bin/env python3
"""
Migration: Add OCR fields to medical_records table
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from sqlalchemy import text

def migrate():
    """Add ocr_confidence and ocr_extracted_text columns to medical_records"""
    
    with engine.connect() as conn:
        try:
            # Add ocr_confidence column
            conn.execute(text("""
                ALTER TABLE medical_records 
                ADD COLUMN IF NOT EXISTS ocr_confidence INTEGER;
            """))
            conn.commit()
            print("✓ Added ocr_confidence column")
            
            # Add ocr_extracted_text column
            conn.execute(text("""
                ALTER TABLE medical_records 
                ADD COLUMN IF NOT EXISTS ocr_extracted_text TEXT;
            """))
            conn.commit()
            print("✓ Added ocr_extracted_text column")
            
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            conn.rollback()
            sys.exit(1)

if __name__ == "__main__":
    migrate()
