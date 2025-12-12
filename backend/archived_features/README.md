# Archived Image Features - README

## Overview

This directory contains image upload and OCR training features that were removed from the main application on **2025-12-12** per user request.

## Reason for Archival

- PyTorch dependencies installation issues (~3GB download)
- Complex ML training requirements
- Focus shift to core text-based features
- Simpler deployment without heavy ML dependencies

---

## Archived Components

### Training Scripts
- **`train_ocr_model.py`** - TrOCR fine-tuning on handwritten prescriptions
- **`load_prescription_training.py`** - Load 4,598 handwritten medication images
- **`batch_upload_training.py`** - Bulk image processing for training
- **`demo_training.py`** - Interactive training workflow demonstration

### Documentation
- **`TRAINING_README.md`** - Comprehensive training guide
- **`PRESCRIPTION_DATASET.md`** - Dataset integration documentation

### Frontend Features (Removed)
- Image upload on dashboard medical record form
- Image preview and thumbnails
- OCR extraction status display
- Chat image attachment button (📎)

### Backend Features (Removed)
- `image_data` field in MedicalRecord model
- `ocr_confidence` and `ocr_extracted_text` fields
- Image processing in `/api/records` endpoint
- Image analysis in `/api/ai/chat` endpoint
- Training image API routes

---

## Dataset Information

**Handwritten Prescription Dataset:**
- Training: 3,004 images
- Testing: 757 images
- Validation: 738 images
- **Total: 4,499 labeled medication word images**

CSV Format: `IMAGE,MEDICINE_NAME,GENERIC_NAME`

Location (if still present): `data/doctor_notes/`

---

## To Restore These Features

If you want to re-enable image features:

### 1. Install Dependencies
```bash
pip install torch torchvision transformers datasets evaluate jiwer
```

### 2. Move Scripts Back
```bash
mv archived_features/*.py scripts/
mv archived_features/*.md .
```

### 3. Restore Frontend
Uncomment image upload sections in:
- `frontend/templates/dashboard.html` (lines ~89-105)
- `frontend/templates/chat.html` (image upload button)

### 4. Restore Backend
Uncomment in `app/api/routes/ai.py` and `app/api/routes/medical_records.py`:
- Image data handling
- OCR processing calls
- Image field validation

### 5. Run Database Migration
```bash
python scripts/migrate_add_ocr_fields.py
```

---

## Alternative: Simpler Image Approach

If you want image upload without heavy ML:

1. **Basic Image Storage Only**
   - Store images as base64 in database
   - No OCR processing
   - Display in medical records

2. **External OCR Service**
   - Use Google Cloud Vision API
   - Use AWS Textract
   - Use Azure Computer Vision
   - (Much lighter than local ML)

3. **Client-Side Only**
   - Store images in browser localStorage
   - No server processing
   - Simpler but less powerful

---

## Files in This Archive

```
archived_features/
├── train_ocr_model.py           # TrOCR training script
├── load_prescription_training.py # Dataset loader
├── batch_upload_training.py      # Bulk processing
├── demo_training.py              # Interactive demo
├── TRAINING_README.md            # Training guide
├── PRESCRIPTION_DATASET.md       # Dataset docs
└── README.md                     # This file
```

---

## Contact

If you have questions about these archived features, refer to the commit history around 2025-12-12 for implementation details.

**Status:** Archived but preserved for future reference.
