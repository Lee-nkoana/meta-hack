# Medical records API routes
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.database import get_db
from app.schemas.medical_record import (
    MedicalRecordCreateSchema,
    MedicalRecordUpdateSchema,
    MedicalRecordResponseSchema,
    MedicalRecordListSchema
)
from app.models import User, MedicalRecord
from app.api.deps import require_auth, get_current_active_user

bp = Blueprint('records', __name__, url_prefix='/api/records')

# Initialize schemas
record_create_schema = MedicalRecordCreateSchema()
record_update_schema = MedicalRecordUpdateSchema()
record_response_schema = MedicalRecordResponseSchema()
record_list_schema = MedicalRecordListSchema(many=True)


@bp.route('', methods=['POST'])
@require_auth
def create_medical_record():
    """Create a new medical record (supports JSON or Multipart/Form-Data with image)"""
    current_user = get_current_active_user()
    db = get_db()
    
    # Handle Image Upload (Multipart)
    if 'image' in request.files:
        file = request.files['image']
        title = request.form.get('title', 'Uploaded Medical Image')
        record_type = request.form.get('record_type', 'doctor_note')
        
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        import base64
        # Read and encode image
        image_bytes = file.read()
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Analyze image with AI
        from app.services.ai_service import ai_service
        # Use a prompt to extract text and details
        analysis_prompt = "Extract all text from this medical document and summarize key medical details."
        ai_result = "Image processing pending..." # Default if AI fails/not configured
        
        try:
             # Run sync or via async helper (Flask is sync by default unless async route)
             # Since ai_service methods are async, we need a way to run them.
             # Ideally we should use `async def` route if using Quart/Async Flask, 
             # but here we might need to rely on the event loop or simple run.
             # For simplicity in standard Flask, we might need a sync wrapper or just hope the async run works if set up.
             # However, assuming standard Flask sync route:
             import asyncio
             try:
                 # Check if there is an existing loop
                 loop = asyncio.get_event_loop()
             except RuntimeError:
                 loop = asyncio.new_event_loop()
                 asyncio.set_event_loop(loop)
                 
             ai_text = loop.run_until_complete(ai_service.analyze_image(image_b64, analysis_prompt))
             if ai_text:
                 ai_result = ai_text
        except Exception as e:
            print(f"AI Image Analysis Failed: {e}")
            
        db_record = MedicalRecord(
            user_id=current_user.id,
            title=title,
            original_text=ai_result, # Extracted text becomes the record content
            image_data=image_b64,
            record_type=record_type
        )
        
    else:
        # Handle Standard JSON
        try:
            # Validate request data
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
                
            record_data = record_create_schema.load(data)
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
        
        db_record = MedicalRecord(
            user_id=current_user.id,
            title=record_data['title'],
            original_text=record_data['original_text'],
            record_type=record_data.get('record_type', 'doctor_note')
        )

    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    # Add to RAG Knowledge Base
    try:
        from app.services.knowledge_base import knowledge_base
        knowledge_base.add_record(
            record_id=str(db_record.id),
            text=db_record.original_text,
            meta={"title": db_record.title, "type": db_record.record_type, "user_id": current_user.id}
        )
    except Exception as e:
        print(f"RAG Indexing Failed: {e}")
        
    return jsonify(record_response_schema.dump(db_record)), 201


@bp.route('', methods=['GET'])
@require_auth
def list_medical_records():
    """List all medical records for the current user"""
    current_user = get_current_active_user()
    db = get_db()
    
    skip = request.args.get('skip', 0, type=int)
    limit = request.args.get('limit', 100, type=int)
    
    records = db.query(MedicalRecord).filter(
        MedicalRecord.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    # Transform to list view
    record_list = [
        {
            "id": record.id,
            "title": record.title,
            "record_type": record.record_type,
            "created_at": record.created_at,
            "has_translation": record.translated_text is not None,
            "has_suggestions": record.lifestyle_suggestions is not None
        }
        for record in records
    ]
    
    return jsonify(record_list_schema.dump(record_list)), 200


@bp.route('/<int:record_id>', methods=['GET'])
@require_auth
def get_medical_record(record_id):
    """Get a specific medical record"""
    current_user = get_current_active_user()
    db = get_db()
    
    record = db.query(MedicalRecord).filter(
        MedicalRecord.id == record_id,
        MedicalRecord.user_id == current_user.id
    ).first()
    
    if not record:
        return jsonify({"error": "Medical record not found"}), 404
    
    return jsonify(record_response_schema.dump(record)), 200


@bp.route('/<int:record_id>', methods=['PUT'])
@require_auth
def update_medical_record(record_id):
    """Update a medical record"""
    current_user = get_current_active_user()
    db = get_db()
    
    record = db.query(MedicalRecord).filter(
        MedicalRecord.id == record_id,
        MedicalRecord.user_id == current_user.id
    ).first()
    
    if not record:
        return jsonify({"error": "Medical record not found"}), 404
    
    try:
        # Validate request data
        update_data = record_update_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    # Update fields
    for field, value in update_data.items():
        setattr(record, field, value)
    
    # Clear cached AI data if original text changed
    if "original_text" in update_data:
        record.translated_text = None
        record.lifestyle_suggestions = None
    
    db.commit()
    db.refresh(record)
    return jsonify(record_response_schema.dump(record)), 200


@bp.route('/<int:record_id>', methods=['DELETE'])
@require_auth
def delete_medical_record(record_id):
    """Delete a medical record"""
    current_user = get_current_active_user()
    db = get_db()
    
    record = db.query(MedicalRecord).filter(
        MedicalRecord.id == record_id,
        MedicalRecord.user_id == current_user.id
    ).first()
    
    if not record:
        return jsonify({"error": "Medical record not found"}), 404
    
    db.delete(record)
    db.commit()
    return '', 204
