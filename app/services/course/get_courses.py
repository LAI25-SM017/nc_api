from app.models.course import Course
from app.extensions import db
from app.services.recommender.contentbased_model import ContentBasedModel
from app.services.recommender.collaborative_model import CollaborativeModel

def get_all_courses():
    return [course.to_dict() for course in Course.query.all()]
    
def get_courses(page=1, per_page=10, subject=None, level=None, is_paid=None, order_by='num_subscribers', order_direction='desc'):
    # Subject mapping:
    # 1 -> 'Business Finance'
    # 2 -> 'Graphic Design'
    # 3 -> 'Web Development'
    # 4 -> 'Musical Instruments'
    
    # Level may be 'Beginner Level', 'Intermediate Level', 'Expert Level', 'All Levels'
    # Level mapping:
    # 1 -> 'Beginner Level'
    # 2 -> 'Intermediate Level'
    # 3 -> 'Expert Level'
    # 0 -> 'All Levels'
    
    # is_paid may be 1 (paid) or 0 (free)
    
    # Order by num_subscribers, num_reviews, total_interactions, and total_users
    
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 25
    if per_page > 200:
        per_page = 200
        
    if order_by not in ['num_subscribers', 'num_reviews', 'total_interactions', 'total_users']:
        order_by = 'num_subscribers'
    
    if is_paid not in [1, 0, None]:
        is_paid = None
        
    subject_mapping = {
        1: 'Business Finance',
        2: 'Graphic Design',
        3: 'Web Development',
        4: 'Musical Instruments'
    }

    level_mapping = {
        1: 'Beginner Level',
        2: 'Intermediate Level',
        3: 'Expert Level',
        0: 'All Levels'
    }

    # Handle multiple subjects
    if subject:
        if not isinstance(subject, list):
            subject = [subject]
        subject = [subject_mapping.get(s) for s in subject if s in subject_mapping]

    # Handle multiple levels
    if level:
        if not isinstance(level, list):
            level = [level]
        level = [level_mapping.get(l) for l in level if l in level_mapping]

    print("Mapped Subjects:", subject)
    print("Mapped Levels:", level)
    
    query = Course.query
    if subject:
        query = query.filter(Course.subject.in_(subject))
    if level:
        query = query.filter(Course.level.in_(level))
    if is_paid is not None:
        query = query.filter_by(is_paid=is_paid)
        
    if order_by == 'num_subscribers':
        if order_direction == 'desc':
            query = query.order_by(Course.num_subscribers.desc())
        else:
            query = query.order_by(Course.num_subscribers.asc())
    elif order_by == 'num_reviews':
        if order_direction == 'desc':
            query = query.order_by(Course.num_reviews.desc())
        else:
            query = query.order_by(Course.num_reviews.asc())
    elif order_by == 'total_interactions':
        if order_direction == 'desc':
            query = query.order_by(Course.total_interactions.desc())
        else:
            query = query.order_by(Course.total_interactions.asc())
    elif order_by == 'total_users':
        if order_direction == 'desc':
            query = query.order_by(Course.total_users.desc())
        else:
            query = query.order_by(Course.total_users.asc())
    
    courses = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'courses': [course.to_dict() for course in courses.items],
        'total': courses.total,
        'pages': courses.pages,
        'page': page,
        'per_page': per_page
    }

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
    
    courses = model_instance.get_recommendations_by_course_id(course_id, n)
    
    return courses

def get_recommended_courses_by_user_id(user_id, n):
    # Get the singleton instance of CollaborativeModel
    model_instance = CollaborativeModel()
    
    courses = model_instance.get_recommendations_by_user_id(user_id, n)
    
    return courses