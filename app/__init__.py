import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS

from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask import jsonify

from dotenv import load_dotenv
load_dotenv()

from .config import Config
from .extensions import db

from .routes.course_routes import course_bp
from .routes.user_routes import user_bp

from .services.recommender.contentbased_model import ContentBasedModel

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    app.config.from_object(Config)
    
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
    
    # Register blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(course_bp, url_prefix="/api/courses")

    return app
