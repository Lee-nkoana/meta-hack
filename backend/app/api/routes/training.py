# Training data API routes
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.database import get_db
from app.models import TrainingImage
from app.schemas.training import (
    TrainingImageUploadSchema,
    TrainingImageResponseSchema,
    OCRResultSchema,
    OCRFeedbackSchema,
    TrainingStatsSchema
)
from app.services.ocr_service import ocr_service
from app.services.medication_service import medication_service
from app.api.deps import require_auth, get_current_active_user

bp = Blueprint('training', __name__, url_prefix='/api/training')

# Initialize schemas
training_upload_schema = TrainingImageUploadSchema()
training_response_schema = TrainingImageResponseSchema()
training_response_list_schema = TrainingImageResponseSchema(many=True)
ocr_result_schema = OCRResultSchema()
ocr_feedback_schema = OCRFeedbackSchema()
training_stats_schema = TrainingStatsSchema()


@bp.route('/upload', methods=['POST'])
@require_auth
def upload_training_image():
    """
    Upload a medical image for OCR training
    Supports multipart form data with image file
    """
    current_user = get_current_active_user()
    db = get_db()
    
    # Check for image file
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Get form data
    image_type = request.form.get('image_type', 'printed')
    is_training_data = request.form.get('is_training_data', 'false').lower() == 'true'
    
    # Validate image_type
    if image_type not in ['handwritten', 'printed', 'mixed']:
        return jsonify({'error': 'Invalid image_type. Must be: handwritten, printed, or mixed'}), 400
    
    # Read and encode image
    import base64
    image_bytes = file.read()
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
    
    # Extract text using OCR
    extracted_text, confidence = ocr_service.extract_text_from_image(image_b64)
    
    # Extract medications from text
    medications_detected = []
    if extracted_text:
        medications_found = medication_service.get_medication_context(db, extracted_text)
        medications_detected = [med['name'] for med in medications_found]
    
    # Save to database
    training_image = TrainingImage(
        user_id=current_user.id,
        image_data=image_b64,
        extracted_text=extracted_text,
        ocr_confidence=confidence,
        image_type=image_type,
        is_training_data=is_training_data
    )
    
    db.add(training_image)
    db.commit()
    db.refresh(training_image)
    
    # Return OCR results
    ocr_result = {
        'extracted_text': extracted_text,
        'confidence': confidence,
        'medications_detected': medications_detected
    }
    
    return jsonify({
        'training_image': training_response_schema.dump(training_image),
        'ocr_result': ocr_result_schema.dump(ocr_result)
    }), 201


@bp.route('/<int:image_id>/feedback', methods=['POST'])
@require_auth
def submit_ocr_feedback(image_id):
    """
    Submit corrected text for a training image
    This helps improve OCR accuracy over time
    """
    current_user = get_current_active_user()
    db = get_db()
    
    # Get training image
    training_image = db.query(TrainingImage).filter(
        TrainingImage.id == image_id,
        TrainingImage.user_id == current_user.id
    ).first()
    
    if not training_image:
        return jsonify({'error': 'Training image not found'}), 404
    
    # Validate request
    try:
        feedback_data = ocr_feedback_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    # Update corrected text
    training_image.corrected_text = feedback_data['corrected_text']
    db.commit()
    db.refresh(training_image)
    
    return jsonify(training_response_schema.dump(training_image)), 200


@bp.route('/images', methods=['GET'])
@require_auth
def list_training_images():
    """List user's training images"""
    current_user = get_current_active_user()
    db = get_db()
    
    skip = request.args.get('skip', 0, type=int)
    limit = request.args.get('limit', 50, type=int)
    
    images = db.query(TrainingImage).filter(
        TrainingImage.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return jsonify(training_response_list_schema.dump(images)), 200


@bp.route('/stats', methods=['GET'])
@require_auth
def get_training_stats():
    """Get OCR training statistics for current user"""
    current_user = get_current_active_user()
    db = get_db()
    
    # Total images
    total_images = db.query(TrainingImage).filter(
        TrainingImage.user_id == current_user.id
    ).count()
    
    # Images with corrections
    images_corrected = db.query(TrainingImage).filter(
        TrainingImage.user_id == current_user.id,
        TrainingImage.corrected_text.isnot(None)
    ).count()
    
    # Average confidence
    from sqlalchemy import func
    avg_confidence_result = db.query(func.avg(TrainingImage.ocr_confidence)).filter(
        TrainingImage.user_id == current_user.id,
        TrainingImage.ocr_confidence.isnot(None)
    ).scalar()
    
    avg_confidence = float(avg_confidence_result) if avg_confidence_result else None
    
    # Count by type
    type_counts = {}
    for image_type in ['handwritten', 'printed', 'mixed']:
        count = db.query(TrainingImage).filter(
            TrainingImage.user_id == current_user.id,
            TrainingImage.image_type == image_type
        ).count()
        type_counts[image_type] = count
    
    stats = {
        'total_images': total_images,
        'average_confidence': avg_confidence,
        'images_corrected': images_corrected,
        'by_type': type_counts
    }
    
    return jsonify(training_stats_schema.dump(stats)), 200
