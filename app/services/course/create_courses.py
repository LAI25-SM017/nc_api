from app.models.course import Course
from app.extensions import db

def create_courses(courses):
    try:
        for course in courses:
            new_course = Course(
                course_id=course['course_id'],
                course_title=course['course_title'],
                url=course['url'],
                is_paid=course['is_paid'],
                price=course['price'],
                num_subscribers=course['num_subscribers'],
                num_reviews=course['num_reviews'],
                num_lectures=course['num_lectures'],
                level=course['level'],
                content_duration=course['content_duration'],
                published_timestamp=course['published_timestamp'],
                subject=course['subject']
            )
            db.session.add(new_course)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
