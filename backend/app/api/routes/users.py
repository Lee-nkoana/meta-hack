# User profile and dashboard API routes
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.database import get_db
from app.schemas.user import UserProfileSchema, UserUpdateSchema, UserResponseSchema
from app.models import User, MedicalRecord
from app.api.deps import require_auth, get_current_active_user
from app.utils.security import get_password_hash

bp = Blueprint('users', __name__, url_prefix='/api/users')

# Initialize schemas
user_profile_schema = UserProfileSchema()
user_update_schema = UserUpdateSchema()
user_response_schema = UserResponseSchema()


@bp.route('/me', methods=['GET'])
@require_auth
def get_user_profile():
    """Get current user profile with statistics"""
    current_user = get_current_active_user()
    db = get_db()
    
    record_count = db.query(MedicalRecord).filter(
        MedicalRecord.user_id == current_user.id
    ).count()
    
    # Create response dict
    user_dict = {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "record_count": record_count
    }
    
    return jsonify(user_profile_schema.dump(user_dict)), 200


@bp.route('/me', methods=['PUT'])
@require_auth
def update_user_profile():
    """Update current user profile"""
    current_user = get_current_active_user()
    db = get_db()
    
    try:
        # Validate request data
        update_data = user_update_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    # Check if email is being updated and if it's already taken
    if "email" in update_data:
        existing_user = db.query(User).filter(
            User.email == update_data["email"],
            User.id != current_user.id
        ).first()
        if existing_user:
            return jsonify({"error": "Email already registered"}), 400
    
    # Handle password update separately
    if "password" in update_data:
        current_user.hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
    
    # Update other fields
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return jsonify(user_response_schema.dump(current_user)), 200


@bp.route('/dashboard', methods=['GET'])
@require_auth
def get_dashboard_stats():
    """Get dashboard statistics for the current user"""
    current_user = get_current_active_user()
    db = get_db()
    
    # Get all records for the user
    all_records = db.query(MedicalRecord).filter(
        MedicalRecord.user_id == current_user.id
    ).all()
    
    total_records = len(all_records)
    records_with_translation = sum(1 for r in all_records if r.translated_text)
    records_with_suggestions = sum(1 for r in all_records if r.lifestyle_suggestions)
    
    # Get recent records (last 5)
    recent_records_query = db.query(MedicalRecord).filter(
        MedicalRecord.user_id == current_user.id
    ).order_by(MedicalRecord.created_at.desc()).limit(5).all()
    
    recent_records = [
        {
            "id": record.id,
            "title": record.title,
            "record_type": record.record_type,
            "created_at": record.created_at.isoformat(),
            "has_translation": record.translated_text is not None,
            "has_suggestions": record.lifestyle_suggestions is not None
        }
        for record in recent_records_query
    ]
    
    response = {
        "total_records": total_records,
        "records_with_translation": records_with_translation,
        "records_with_suggestions": records_with_suggestions,
        "recent_records": recent_records
    }
    
    return jsonify(response), 200
