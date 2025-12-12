# Training Data Upload Scripts

This directory contains scripts for uploading and managing OCR training data.

## Scripts Overview

### 1. Demo Training Script (`demo_training.py`)
Interactive demonstration of the training workflow.

**Features:**
- Uploads medical images with OCR
- Submits corrections to improve accuracy
- Shows medication detection
- Displays training statistics

**Usage:**
```bash
# Run full interactive demo
make demo-training

# Or directly:
python scripts/demo_training.py

# Demo medication extraction only
python scripts/demo_training.py --demo extract
```

**What it does:**
1. Logs in and gets authentication token
2. Uploads a medical image for OCR processing
3. Shows OCR results and detected medications
4. Allows you to submit corrections
5. Displays training statistics

---

### 2. Batch Upload Script (`batch_upload_training.py`)
Process entire folders of medical images for training.

**Features:**
- Recursive folder scanning
- Auto-detection of image types
- Progress tracking
- Error handling
- Training statistics

**Usage:**
```bash
# Upload all images from folder (auto-detect type)
python scripts/batch_upload_training.py /path/to/medical/images

# Specify image type
python scripts/batch_upload_training.py /path/to/images --type handwritten

# Upload only first 10 images (for testing)
python scripts/batch_upload_training.py /path/to/images --max 10

# Custom authentication
python scripts/batch_upload_training.py /path/to/images \
  --username admin \
  --password mypassword

# Create manifest file only (no upload)
python scripts/batch_upload_training.py /path/to/images --manifest-only

# Using Makefile (convenience)
make batch-upload FOLDER=./training_images TYPE=handwritten
```

**Image Organization Tips:**
```
training_images/
├── handwritten/        # Auto-detected as handwritten
│   ├── note1.jpg
│   ├── note2.png
├── printed/           # Auto-detected as printed
│   ├── prescription1.jpg
│   ├── lab_result.png
└── mixed/             # Auto-detected as mixed
    └── form.jpg
```

The script auto-detects image type from folder names containing:
- `handwritten` or `hand` → handwritten
- `mixed` → mixed
- Otherwise → printed

---

## Quick Start Examples

### Example 1: Upload Single Image (Interactive)
```bash
# Run demo
make demo-training

# Follow prompts:
# 1. Enter image path (or use sample)
# 2. Specify type (printed/handwritten/mixed)
# 3. Review OCR results
# 4. Optionally submit corrections
# 5. View statistics
```

### Example 2: Batch Upload Folder
```bash
# Organize your images
mkdir -p training_images/handwritten
mkdir -p training_images/printed

# Copy your images
cp doctor_notes/*.jpg training_images/handwritten/
cp prescriptions/*.png training_images/printed/

# Upload all images
python scripts/batch_upload_training.py training_images
```

### Example 3: Medication Extraction Demo
```bash
# Test medication detection without uploading
python scripts/demo_training.py --demo extract

# Output shows:
# - Detected medications
# - Discontinued status warnings
# - Medication details
```

---

## Supported Image Formats

✅ JPEG (.jpg, .jpeg)  
✅ PNG (.png)  
✅ BMP (.bmp)  
✅ TIFF (.tiff, .tif)  
✅ WebP (.webp)

---

## Authentication

Both scripts require authentication. Default credentials:
- **Username**: `testuser`
- **Password**: `testpassword`

You can override with command-line arguments or modify the scripts.

---

## Output & Statistics

After batch upload, you'll see:
```
==================================================
UPLOAD SUMMARY
==================================================
✅ Successful: 45
❌ Failed: 2
📊 Average OCR Confidence: 87.3%
💊 Total Medications Detected: 23
==================================================

Total Training Images: 98
Overall Avg Confidence: 85.6%

Images by Type:
  Handwritten: 30
  Printed: 60
  Mixed: 8
```

---

## Advanced Usage

### Custom Delay Between Uploads
```bash
# Slow down uploads (1 second delay)
python scripts/batch_upload_training.py /path/to/images --delay 1.0

# Speed up uploads (0.1 second delay)
python scripts/batch_upload_training.py /path/to/images --delay 0.1
```

### Process Only Subset
```bash
# Upload first 5 images (testing)
python scripts/batch_upload_training.py /path/to/images --max 5
```

### Create Inventory Manifest
```bash
# Generate JSON manifest of images without uploading
python scripts/batch_upload_training.py /path/to/images --manifest-only

# Creates: training_manifest.json
{
  "folder": "/path/to/images",
  "total_images": 47,
  "images": [
    {
      "filename": "note1.jpg",
      "path": "/full/path/to/note1.jpg",
      "size_bytes": 245678,
      "detected_type": "handwritten"
    },
    ...
  ]
}
```

---

## Troubleshooting

**"Authentication failed"**
- Check server is running: `flask run`
- Verify credentials
- Create test user: `make seed`

**"No images found"**
- Check folder path
- Verify file extensions
- Use absolute path

**"Upload failed: 401"**
- Token expired (re-run script)
- User not authenticated

**"OCR confidence low"**
- Image quality may be poor
- Try preprocessing images
- Submit corrections to improve training

---

## Next Steps

After uploading training data:

1. **Review OCR Results**
   - Check extracted text accuracy
   - Note common errors

2. **Submit Corrections**
   - Use demo script or API directly
   - Improves future OCR accuracy

3. **Monitor Statistics**
   ```bash
   curl http://localhost:5000/api/training/stats \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

4. **Export Training Dataset**
   - Future feature: Export corrections
   - Use for fine-tuning OCR models

---

## See Also

- [AI Training Guide](file:///../.gemini/antigravity/brain/.../ai_training_guide.md) - Full training concepts
- [API Documentation](http://localhost:5000/docs) - Swagger UI
- [Walkthrough](file:///../.gemini/antigravity/brain/.../walkthrough.md) - Implementation details
