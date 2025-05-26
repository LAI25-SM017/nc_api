import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS

from flask_jwt_extended import JWTManager

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
    
    # Initialize the ContentBasedModel singleton
    content_based_model = ContentBasedModel()
    print("ContentBasedModel initialized.")
    
    # Register blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(course_bp, url_prefix="/api/courses")

    return app
