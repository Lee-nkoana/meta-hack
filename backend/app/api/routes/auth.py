# Authentication API routes
from flask import Blueprint, request, jsonify, abort
from marshmallow import ValidationError
from app.database import get_db
from app.schemas.auth import TokenSchema
from app.schemas.user import UserCreateSchema, UserResponseSchema
from app.services.auth import create_user, login_user
from app.api.deps import require_auth, get_current_active_user

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Initialize schemas
user_create_schema = UserCreateSchema()
user_response_schema = UserResponseSchema()
token_schema = TokenSchema()


@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        # Validate request data
        data = user_create_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    db = get_db()
    
    # Create user (service will handle validation errors)
    try:
        user = create_user(db, data)
        return jsonify(user_response_schema.dump(user)), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bp.route('/login', methods=['POST'])
def login():
    """Login and receive JWT token"""
    # Get form data (following OAuth2 pattern)
    username = request.form.get('username') or request.get_json().get('username')
    password = request.form.get('password') or request.get_json().get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    db = get_db()
    
    # Login user (service will handle authentication errors)
    try:
        token_data = login_user(db, username, password)
        return jsonify(token_schema.dump(token_data)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401


@bp.route('/me', methods=['GET'])
@require_auth
def get_current_user_info():
    """Get current authenticated user information"""
    current_user = get_current_active_user()
    return jsonify(user_response_schema.dump(current_user)), 200
