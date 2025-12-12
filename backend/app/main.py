
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from app.config import settings
from app.database import init_db, close_db

# Import blueprints
from app.api.routes import auth, medical_records, ai, users, knowledge, medications, training


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__, 
                template_folder="../../frontend/templates",
                static_folder="../../frontend/static")
    
    # Configure app
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['JWT_SECRET_KEY'] = settings.JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = settings.JWT_ACCESS_TOKEN_EXPIRES
    
    # Initialize CORS
    CORS(app, 
         resources={r"/api/*": {"origins": settings.BACKEND_CORS_ORIGINS}},
         supports_credentials=True)
    
    # Initialize JWT Manager
    jwt = JWTManager(app)

    # Swagger Configuration
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs"
    }

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Medical Records Bridge API",
            "description": "API for processing medical records and generating insights",
            "version": "1.0.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
            }
        },
        "security": [
            {"Bearer": []}
        ]
    }

    Swagger(app, config=swagger_config, template=swagger_template) # Initialize Flasgger
    
    # Register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(medical_records.bp)
    app.register_blueprint(ai.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(knowledge.bp)
    app.register_blueprint(medications.bp)
    app.register_blueprint(training.bp)
    
    # Register teardown function for database
    app.teardown_appcontext(close_db)
    
    # Initialize database before first request
    with app.app_context():
        init_db()
    
    @app.route("/")
    def root():
        """Root endpoint - renders login page"""
        return render_template("login.html")
    
    @app.route("/login")
    def login():
        """Login page"""
        return render_template("login.html")

    @app.route("/register")
    def register():
        """Register page"""
        return render_template("register.html")

    @app.route("/chat")
    def chat_page():
        return render_template("chat.html")
    
    @app.route("/dashboard")
    def dashboard():
        """Dashboard page"""
        return render_template("dashboard.html")
    
    @app.route("/records")
    def records():
        """Records page"""
        return render_template("records.html")
    
    @app.route("/profile")
    def profile():
        """Profile page"""
        return render_template("profile.html")
    
    @app.route("/health")
    def health_check():
        """Health check endpoint"""
        return jsonify({"status": "healthy"})
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=settings.DEBUG)
