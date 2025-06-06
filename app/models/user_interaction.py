from app.extensions import db
from app.models.user import User
from app.models.course import Course

class UserInteraction(db.Model):
    __tablename__ = 'user_interactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'), nullable=False, index=True)
    interaction_type = db.Column(db.String(35), nullable=False)  # e.g., 'view', 'enrolled', 'complete', 'buy'

    user = db.relationship('User', back_populates='interactions')
    course = db.relationship('Course', back_populates='interactions')
    
    # Add a unique constraint for the combination of user_id, course_id, and interaction_type
    __table_args__ = (
        db.UniqueConstraint('user_id', 'course_id', 'interaction_type', name='uq_user_course_interaction'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'interaction_type': self.interaction_type
        }
