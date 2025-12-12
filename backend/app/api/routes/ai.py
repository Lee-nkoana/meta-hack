import asyncio
from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, ValidationError
from app.database import get_db
from app.models import User, MedicalRecord
from app.api.deps import require_auth, get_current_active_user
from app.services.ai_service import ai_service

bp = Blueprint('ai', __name__, url_prefix='/api/ai')


# Request/Response schemas
class ChatRequestSchema(Schema):
    """Request schema for AI chat"""
    message = fields.Str(required=True)
    include_context = fields.Bool(missing=True, default=True)

class TranslateRequestSchema(Schema):
    """Request schema for text translation"""
    text = fields.Str(required=True)


class SuggestionsRequestSchema(Schema):
    """Request schema for lifestyle suggestions"""
    condition = fields.Str(required=True)


class AIResponseSchema(Schema):
    """Response schema for AI operations"""
    result = fields.Str(allow_none=True)
    cached = fields.Bool(missing=False, default=False)


# Initialize schemas
chat_request_schema = ChatRequestSchema()
translate_request_schema = TranslateRequestSchema()
suggestions_request_schema = SuggestionsRequestSchema()
ai_response_schema = AIResponseSchema()


@bp.route('/chat', methods=['POST'])
@require_auth
def chat_with_ai():
    """Chat with AI using medical context (text only)"""
    current_user = get_current_active_user()
    db = get_db()
    
    # Get JSON data
    try:
        data = request.get_json()
        message = data.get('message', '')
        include_context = data.get('include_context', True)
    except Exception as err:
        return jsonify({"error": "Invalid request format"}), 400
    
    context = None
    
    # Add Medical Records Context if requested
    if include_context:
        # Fetch last 5 records
        recent_records = db.query(MedicalRecord).filter(
            MedicalRecord.user_id == current_user.id
        ).order_by(MedicalRecord.created_at.desc()).limit(5).all()
        
        if recent_records:
            context = "\n\n".join([
                f"Record ({r.created_at.strftime('%Y-%m-%d')}): {r.title} ({r.record_type})\n{r.original_text}"
                for r in recent_records
            ])

    if not ai_service.is_configured:
        return jsonify({
            "error": "AI service is not configured."
        }), 503
        
    # Run chat
    try:
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        response = loop.run_until_complete(ai_service.chat_with_patient(message, context))
    except Exception as e:
        print(f"Chat execution failed: {e}")
        import traceback
        traceback.print_exc()
        response = None
    
    if not response:
         return jsonify({"error": "AI service temporarily unavailable (Model Error). Please try again or switch model."}), 503
         
    return jsonify({"response": response}), 200
@require_auth
def chat_with_ai():
    """Chat with AI using medical context (supports JSON or Multipart with Image)"""
    current_user = get_current_active_user()
    db = get_db()
    
    # Handle Input (JSON vs Multipart)
    message = ""
    include_context = True
    image_description = None
    ocr_result = None
    
    if 'image' in request.files:
        # Multipart request
        message = request.form.get('message', '')
        include_context = request.form.get('include_context', 'true').lower() == 'true'
        
        file = request.files['image']
        if file.filename != '':
            import base64
            image_bytes = file.read()
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Process with OCR first
            from app.services.ocr_service import ocr_service
            try:
                extracted_text, confidence = ocr_service.extract_text_from_image(image_b64)
                ocr_result = {
                    "extracted_text": extracted_text or "",
                    "confidence": int(confidence * 100) if confidence else 0
                }
            except Exception as e:
                print(f"OCR processing failed: {e}")
            
            # Use Vision model to describe the image for the chat context
            prompt = "Describe this medical image in detail so I can answer questions about it."
            try:
                # Sync wrapper for async call
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_closed():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                image_description = loop.run_until_complete(ai_service.analyze_image(image_b64, prompt))
            except Exception as e:
                print(f"Chat Image Analysis Failed: {e}")
                image_description = "Error analyzing image."
    else:
        # Standard JSON
        try:
            data = request.get_json()
            message = data.get('message', '')
            include_context = data.get('include_context', True)
            
            # Check for base64 image in JSON
            if 'image_data' in data and data['image_data']:
                image_b64 = data['image_data']
                # Remove data URI prefix if present
                if 'base64,' in image_b64:
                    image_b64 = image_b64.split('base64,')[1]
                
                # Process with OCR first
                from app.services.ocr_service import ocr_service
                try:
                    extracted_text, confidence = ocr_service.extract_text_from_image(image_b64)
                    ocr_result = {
                        "extracted_text": extracted_text or "",
                        "confidence": int(confidence * 100) if confidence else 0
                    }
                except Exception as e:
                    print(f"OCR processing failed: {e}")
                
                # Use Vision model to analyze
                prompt = "Analyze this medical image and describe what you see. Focus on any text, medications, or medical conditions visible."
                try:
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_closed():
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    image_description = loop.run_until_complete(ai_service.analyze_image(image_b64, prompt))
                except Exception as e:
                    print(f"Chat Image Analysis Failed: {e}")
                    image_description = "Error analyzing image."
                    
        except Exception as err:
            return jsonify({"error": "Invalid request format"}), 400
    
    context = None
    context_parts = []
    
    # 1. Add Image Description if present
    if image_description:
        context_parts.append(f"User uploaded an image. Content/Description: {image_description}")
    
    # 2. Add Medical Records Context if requested
    if include_context:
        # Fetch last 5 records
        recent_records = db.query(MedicalRecord).filter(
            MedicalRecord.user_id == current_user.id
        ).order_by(MedicalRecord.created_at.desc()).limit(5).all()
        
        if recent_records:
            records_text = "\n\n".join([
                f"Record ({r.created_at.strftime('%Y-%m-%d')}): {r.title} ({r.record_type})\n{r.original_text}"
                for r in recent_records
            ])
            context_parts.append(records_text)
            
    if context_parts:
        context = "\n\n---\n\n".join(context_parts)

    if not ai_service.is_configured:
        return jsonify({
            "error": "AI service is not configured."
        }), 503
        
    # Run chat (handling async loop properly)
    try:
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        response = loop.run_until_complete(ai_service.chat_with_patient(message, context))
    except Exception as e:
        print(f"Chat execution failed: {e}")
        import traceback
        traceback.print_exc()
        response = None
    
    if not response:
         return jsonify({"error": "AI service temporarily unavailable (Model Error). Please try again or switch model."}), 503
         
    # Prepare response
    response_data = {"response": response}
    
    # Include OCR result if available
    if ocr_result:
        response_data["ocr_result"] = {
            "extracted_text": ocr_result.get("extracted_text", ""),
            "confidence": ocr_result.get("confidence", 0),
            "medications": ocr_result.get("detected_medications", [])
        }
    
    return jsonify(response_data), 200


@bp.route('/translate', methods=['POST'])
@require_auth
def translate_medical_text():
    """Translate medical text to layman's terms on-demand"""
    current_user = get_current_active_user()
    
    try:
        data = translate_request_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    if not ai_service.is_configured:
        return jsonify({
            "error": "AI service is not configured. Please set META_AI_API_KEY in environment variables."
        }), 503
    
    # Run async function in sync context
    translation = asyncio.run(ai_service.translate_medical_text(data['text']))
    
    if translation is None:
        return jsonify({
            "error": "Failed to translate medical text. Please try again."
        }), 500
    
    return jsonify(ai_response_schema.dump({"result": translation, "cached": False})), 200


@bp.route('/suggestions', methods=['POST'])
@require_auth
def get_lifestyle_suggestions():
    """Get lifestyle suggestions for a medical condition on-demand"""
    current_user = get_current_active_user()
    
    try:
        data = suggestions_request_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    if not ai_service.is_configured:
        return jsonify({
            "error": "AI service is not configured. Please set META_AI_API_KEY in environment variables."
        }), 503
    
    # Run async function in sync context
    suggestions = asyncio.run(ai_service.generate_lifestyle_suggestions(data['condition']))
    
    if suggestions is None:
        return jsonify({
            "error": "Failed to generate lifestyle suggestions. Please try again."
        }), 500
    
    return jsonify(ai_response_schema.dump({"result": suggestions, "cached": False})), 200


@bp.route('/explain/<int:record_id>', methods=['POST'])
@require_auth
def explain_medical_record(record_id):
    """Get AI explanation and suggestions for a specific medical record"""
    current_user = get_current_active_user()
    db = get_db()
    
    force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
    
    # Get the medical record
    record = db.query(MedicalRecord).filter(
        MedicalRecord.id == record_id,
        MedicalRecord.user_id == current_user.id
    ).first()
    
    if not record:
        return jsonify({"error": "Medical record not found"}), 404
    
    # Check if we have cached results and force_refresh is False
    if not force_refresh and record.translated_text and record.lifestyle_suggestions:
        return jsonify({
            "translation": record.translated_text,
            "suggestions": record.lifestyle_suggestions,
            "cached": True
        }), 200
    
    # Check if AI service is configured
    if not ai_service.is_configured:
        return jsonify({
            "error": "AI service is not configured. Please set META_AI_API_KEY in environment variables."
        }), 503
    
    # Get AI explanations (run async in sync context)
    result = asyncio.run(ai_service.explain_medical_record(record.original_text, record.record_type))
    
    # Cache the results
    if result["translation"]:
        record.translated_text = result["translation"]
    if result["suggestions"]:
        record.lifestyle_suggestions = result["suggestions"]
    
    db.commit()
    db.refresh(record)
    
    return jsonify({
        "translation": result["translation"],
        "suggestions": result["suggestions"],
        "cached": False
    }), 200
