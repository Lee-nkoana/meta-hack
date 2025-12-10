# Flask main application
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import settings
from app.database import init_db, close_db

# Import blueprints
from app.api.routes import auth, medical_records, ai, users


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
    
    # Register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(medical_records.bp)
    app.register_blueprint(ai.bp)
    app.register_blueprint(users.bp)
    
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

    @app.route("/dashboard")
    def dashboard():
        """Dashboard page"""
        return render_template("dashboard.html")
    
    @app.route("/health")
    def health_check():
        """Health check endpoint"""
        return jsonify({"status": "healthy"})
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=settings.DEBUG)
