from threading import Lock
from pathlib import Path
import tensorflow as tf
import os
from app.models.course import Course
from app.extensions import db

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

class ContentBasedModel:
    """
    A class to represent a content-based recommendation model.
    """
    _instance = None
    _lock = Lock()
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    
                    # Initialize the model
                    cls._instance._load_model()
        return cls._instance
    
    def _load_model(self):
        """
        Load the content-based recommendation model.
        This is a placeholder for the actual model loading logic.
        """
        
        # Dynamically construct the path to the saved model directory
        model_dir = Path(__file__).parent.parent.parent / "saved_cb_index"
        if model_dir.exists():
            self.model = tf.saved_model.load(str(model_dir))
            print(f"Content-based model loaded from {model_dir}")
        else:
            raise FileNotFoundError(f"Model directory {model_dir} does not exist. Please ensure the model is saved correctly.")
        
    def get_model(self):
        """
        Get the content-based recommendation model.
        
        Returns:
            The content-based recommendation model.
        """
        return self.model
    
    def get_recommendations_by_course_id(self, course_id):
        # Check if course_id is valid
        if not isinstance(course_id, int):
            raise ValueError("course_id must be an integer.")
        
        # Check if course_id exists in the database
        course = Course.query.filter_by(course_id=course_id).first()
        if not course:
            raise ValueError(f"Course with ID {course_id} does not exist.")
        
        # Get the model
        model = self.get_model()
        
        # Prepare the input for the model
        query_features = {
            "course_id": tf.constant([str(course.course_id)]),
            "course_title": tf.constant([course.course_title]),
            "subject": tf.constant([course.subject]),
            "level": tf.constant([course.level]),
            "price": tf.constant([course.price], dtype=tf.float32),
            "num_subscribers": tf.constant([course.num_subscribers], dtype=tf.float32),
            "num_reviews": tf.constant([course.num_reviews], dtype=tf.float32),
            "num_lectures": tf.constant([course.num_lectures], dtype=tf.float32),
            "content_duration": tf.constant([course.content_duration], dtype=tf.float32),
        }
        
        # Get recommendations from the model
        scores, ids = model(query_features)
        
        recommendations = []

        recommended_ids = [id.numpy().decode('utf-8') for id in ids[0]]

        recommended_courses = Course.query.filter(Course.course_id.in_(recommended_ids)).all()
        recommendations = [course.to_dict() for course in recommended_courses]

        return recommendations
