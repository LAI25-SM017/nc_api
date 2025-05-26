from app.models.course import Course
from app.extensions import db
from app.services.recommender.contentbased_model import ContentBasedModel

def get_all_courses():
    return [course.to_dict() for course in Course.query.all()]

def get_course_by_id(course_id):
    course = Course.query.filter_by(course_id=course_id).first()
    if course:
        return course.to_dict()
    else:
        return None
    
# Get N random courses for each subject that is 'Business Finance', 'Graphics Design', 'Web Development', 'Musical Instruments'.
def get_random_courses(n=2):
    subjects = ['Business Finance', 'Graphics Design', 'Web Development', 'Musical Instruments']
    courses = []
    for subject in subjects:
        random_courses = Course.query.filter_by(subject=subject).order_by(db.func.random()).limit(n).all()
        courses.extend([course.to_dict() for course in random_courses])
    return courses

# Get recommended courses based on the course_id
def get_recommended_courses_by_course_id(course_id, n):
    # Get the singleton instance of ContentBasedModel
    model_instance = ContentBasedModel()
    
    courses = model_instance.get_recommendations_by_course_id(course_id)
    
    return courses[:n]