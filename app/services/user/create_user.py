from app.models.user import User
from app.extensions import db
from app.services.helper.crypto import hash_password

def create_user(username, email, password):
    """
    Create a new user in the database.
    
    :param username: The username of the user.
    :param email: The email of the user.
    :param password: The password of the user.
    :return: The created User object.
    """
    hashed_password = hash_password(password)
    if not hashed_password:
        raise ValueError("Failed to hash password")
    
    new_user = User(username=username, email=email, password_hash=hashed_password)
    
    db.session.add(new_user)
    db.session.commit()
    
    return new_user.to_dict()