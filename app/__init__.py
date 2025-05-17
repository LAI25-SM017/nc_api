from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS

from dotenv import load_dotenv
load_dotenv()

from .config import Config
from .extensions import db
from .routes.course_routes import course_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    app.config.from_object(Config)
    print(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")  # Debug line

    db.init_app(app)
    migrate = Migrate(app, db)
    
    # with app.app_context():
    #     db.create_all()

    app.register_blueprint(course_bp, url_prefix="/api/courses")

    return app
