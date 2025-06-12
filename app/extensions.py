import os

from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()

# Initialize Flask-Limiter parameters
default_limits=["100 per second"]
storage_uri = "memory://"

if os.getenv("FLASK_ENV") == "production":
    storage_uri = os.getenv("REDIS_URL")
    
# Initialize Flask-Limiter
limiter = Limiter(
    get_remote_address,
    default_limits=default_limits,
    storage_uri=storage_uri,
)
