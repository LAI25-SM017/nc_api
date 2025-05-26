from app.models.user import User
from app.extensions import db

def get_user_by_id(user_id):
    """
    Retrieve a user by their ID from the database.
    
    :param user_id: The ID of the user to retrieve.
    :return: The User object if found, None otherwise.
    """
    user = User.query.get(user_id)
    return user.to_dict() if user else None

def get_user_by_username(username):
    """
    Retrieve a user by their username from the database.
    
    :param username: The username of the user to retrieve.
    :return: The User object if found, None otherwise.
    """
    user = User.query.filter_by(username=username).first()
    return user.to_dict() if user else None

def get_password_hash_by_username(username):
    """
    Retrieve the password hash of a user by their username.
    
    :param username: The username of the user.
    :return: The password hash if the user exists, None otherwise.
    """
    user = User.query.filter_by(username=username).first()
    return user.get_password_hash() if user else None