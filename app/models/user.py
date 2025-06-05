from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    onboarding_done = db.Column(db.Boolean, default=False, nullable=False)
    
    preferences = db.relationship('UserPreferences', back_populates='user', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'onboarding_done': self.onboarding_done  # Include the new column
        }
        
    def get_password_hash(self):
        return self.password_hash