# Knowledge Base API routes
from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, ValidationError
from app.database import get_db
from app.models.knowledge import KnowledgeBase
from app.api.deps import require_auth, get_current_active_user

bp = Blueprint('knowledge', __name__, url_prefix='/api/knowledge')

class KnowledgeCreateSchema(Schema):
    """Schema for creating a knowledge entry"""
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    source = fields.Str(allow_none=True)

class KnowledgeResponseSchema(Schema):
    """Schema for knowledge entry response"""
    id = fields.Int()
    title = fields.Str()
    content = fields.Str()
    source = fields.Str(allow_none=True)
    created_at = fields.DateTime()

# Initialize schemas
knowledge_create_schema = KnowledgeCreateSchema()
knowledge_response_schema = KnowledgeResponseSchema()
knowledge_list_schema = KnowledgeResponseSchema(many=True)


@bp.route('/', methods=['POST'])
@require_auth
def create_knowledge_entry():
    """Add a new entry to the knowledge base"""
    current_user = get_current_active_user()
    db = get_db()
    
    try:
        # Validate request data
        entry_data = knowledge_create_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    db_entry = KnowledgeBase(
        title=entry_data['title'],
        content=entry_data['content'],
        source=entry_data.get('source')
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return jsonify(knowledge_response_schema.dump(db_entry)), 201


@bp.route('/', methods=['GET'])
@require_auth
def list_knowledge_entries():
    """List all knowledge base entries"""
    current_user = get_current_active_user()
    db = get_db()
    
    skip = request.args.get('skip', 0, type=int)
    limit = request.args.get('limit', 100, type=int)
    
    entries = db.query(KnowledgeBase).offset(skip).limit(limit).all()
    return jsonify(knowledge_list_schema.dump(entries)), 200
