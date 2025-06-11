import os

import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS

from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask import jsonify

from werkzeug.middleware.proxy_fix import ProxyFix

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from dotenv import load_dotenv
load_dotenv()

from .config import Config
from .extensions import db, limiter

from app.models.user_interaction import UserInteraction

from .routes.course_routes import course_bp
from .routes.user_routes import user_bp

from .services.recommender.contentbased_model import ContentBasedModel
from .services.recommender.collaborative_model import CollaborativeModel

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    app.config.from_object(Config)

    if os.getenv("FLASK_ENV") == "production":
        # Apply ProxyFix only in production
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
        
    # Initialize Flask-Limiter
    limiter.init_app(app)
    # Custom error handler for 429 Too Many Requests
    @app.errorhandler(429)
    def ratelimit_error(e):
        return jsonify({
            'status': 'error',
            'message': 'Rate limit exceeded. Please try again later.',
            'data': {}
        }), 429
        
    # DB
    print(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")  # Debug line
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # JWT
    jwt = JWTManager(app)
    @app.errorhandler(NoAuthorizationError)
    def handle_no_authorization_error(e):
        """
        Custom handler for missing Authorization Header.
        """
        return jsonify({
            'status': 'error',
            'message': 'Authorization header is missing or invalid',
            'data': {}
        }), 401
    
    # Initialize the ContentBasedModel singleton
    content_based_model = ContentBasedModel()
    print("ContentBasedModel initialized.")
    
    # Initialize the CollaborativeModel singleton
    colaborative_model = CollaborativeModel()
    print("ColaborativeModel initialized.")
    
    # Register blueprints
    app.register_blueprint(user_bp, provide_automatic_options=True)
    app.register_blueprint(
            course_bp,
            url_prefix="/api/courses",
            provide_automatic_options=True,
            strict_slashes=False
        )

    return app
