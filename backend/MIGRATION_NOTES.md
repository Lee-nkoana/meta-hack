# Database Migration - Add OCR Fields

## Issue
After adding `ocr_confidence` and `ocr_extracted_text` fields to the MedicalRecord model, PostgreSQL database didn't have these columns, causing errors:
```
psycopg2.errors.UndefinedColumn: column medical_records.ocr_confidence does not exist
```

## Solution
Created and executed migration script: `scripts/migrate_add_ocr_fields.py`

##Migration Details

**Columns Added:**
- `ocr_confidence` (INTEGER) - Stores OCR confidence score 0-100
- `ocr_extracted_text` (TEXT) - Stores original OCR output before user edits

**SQL Executed:**
```sql
ALTER TABLE medical_records 
ADD COLUMN IF NOT EXISTS ocr_confidence INTEGER;

ALTER TABLE medical_records 
ADD COLUMN IF NOT EXISTS ocr_extracted_text TEXT;
```

## Verification

✅ Migration completed successfully
✅ No errors on dashboard load
✅ Tesseract OCR installed (`sudo apt-get install tesseract-ocr`)
✅ Ready for image upload testing

## Future Migrations

For future schema changes, follow this pattern:
1. Update model in `app/models/`
2. Create migration script in `scripts/migrate_*.py`
3. Run migration: `venv/bin/python scripts/migrate_*.py`
4. Test endpoints that use the model
