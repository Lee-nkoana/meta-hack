# Medication API routes
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.database import get_db
from app.schemas.medication import (
    MedicationCreateSchema,
    MedicationResponseSchema,
    MedicationSearchResponseSchema,
    MedicationListResponseSchema
)
from app.services.medication_service import medication_service
from app.api.deps import require_auth, get_current_active_user

bp = Blueprint('medications', __name__, url_prefix='/api/medications')

# Initialize schemas
medication_create_schema = MedicationCreateSchema()
medication_response_schema = MedicationResponseSchema()
medication_search_response_schema = MedicationSearchResponseSchema(many=True)
medication_list_response_schema = MedicationListResponseSchema()


@bp.route('', methods=['GET'])
def list_medications():
    """List all medications with pagination"""
    db = get_db()
    
    skip = request.args.get('skip', 0, type=int)
    limit = request.args.get('limit', 100, type=int)
    discontinued_only = request.args.get('discontinued_only', 'false').lower() == 'true'
    
    medications, total = medication_service.list_medications(
        db, 
        skip=skip, 
        limit=limit,
        discontinued_only=discontinued_only
    )
    
    # Transform to search response format
    medication_dicts = [
        {
            'id': med.id,
            'name': med.name,
            'uses': med.uses,
            'discontinued': med.discontinued
        }
        for med in medications
    ]
    
    response = {
        'medications': medication_search_response_schema.dump(medication_dicts),
        'total': total,
        'skip': skip,
        'limit': limit
    }
    
    return jsonify(medication_list_response_schema.dump(response)), 200


@bp.route('/search', methods=['GET'])
def search_medications():
    """Search medications by name or uses"""
    db = get_db()
    
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400
    
    skip = request.args.get('skip', 0, type=int)
    limit = request.args.get('limit', 50, type=int)
    include_discontinued = request.args.get('include_discontinued', 'false').lower() == 'true'
    
    medications = medication_service.search_medications(
        db,
        query=query,
        skip=skip,
        limit=limit,
        include_discontinued=include_discontinued
    )
    
    # Transform to search response format
    medication_dicts = [
        {
            'id': med.id,
            'name': med.name,
            'uses': med.uses,
            'discontinued': med.discontinued
        }
        for med in medications
    ]
    
    return jsonify(medication_search_response_schema.dump(medication_dicts)), 200


@bp.route('/<int:medication_id>', methods=['GET'])
def get_medication(medication_id):
    """Get specific medication by ID"""
    db = get_db()
    
    medication = medication_service.get_medication_by_id(db, medication_id)
    
    if not medication:
        return jsonify({'error': 'Medication not found'}), 404
    
    return jsonify(medication_response_schema.dump(medication)), 200


@bp.route('/name/<string:name>', methods=['GET'])
def get_medication_by_name(name):
    """Get medication by name (case-insensitive)"""
    db = get_db()
    
    medication = medication_service.get_medication_by_name(db, name)
    
    if not medication:
        return jsonify({'error': 'Medication not found'}), 404
    
    return jsonify(medication_response_schema.dump(medication)), 200


@bp.route('', methods=['POST'])
@require_auth
def create_medication():
    """
    Create a new medication (authenticated users only)
    This is mainly for admin purposes or future expansion
    """
    current_user = get_current_active_user()
    db = get_db()
    
    try:
        medication_data = medication_create_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    # Check if medication already exists
    existing = medication_service.get_medication_by_name(db, medication_data['name'])
    if existing:
        return jsonify({'error': 'Medication with this name already exists'}), 409
    
    medication = medication_service.create_medication(db, medication_data)
    
    return jsonify(medication_response_schema.dump(medication)), 201


@bp.route('/extract', methods=['POST'])
def extract_medications_from_text():
    """
    Extract medication mentions from provided text
    Returns medication details for all found medications
    """
    db = get_db()
    
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Field "text" is required'}), 400
    
    text = data['text']
    medications_found = medication_service.get_medication_context(db, text)
    
    return jsonify({
        'medications_found': medications_found,
        'count': len(medications_found)
    }), 200
