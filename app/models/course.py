from app.extensions import db

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, index=True, unique=True, nullable=False)
    course_title = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    price = db.Column(db.Integer, nullable=False)
    num_subscribers = db.Column(db.Integer, default=0)
    num_reviews = db.Column(db.Integer, default=0)
    num_lectures = db.Column(db.Integer, default=0)
    level = db.Column(db.String(50), nullable=False)
    content_duration = db.Column(db.Float, nullable=False)
    published_timestamp = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'course_title': self.course_title,
            'url': self.url,
            'is_paid': self.is_paid,
            'price': self.price,
            'num_subscribers': self.num_subscribers,
            'num_reviews': self.num_reviews,
            'num_lectures': self.num_lectures,
            'level': self.level,
            'content_duration': self.content_duration,
            'published_timestamp': self.published_timestamp,
            'subject': self.subject
        }
