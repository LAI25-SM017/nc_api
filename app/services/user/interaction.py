from app.models.user_interaction import UserInteraction
from app.models.user import User
from app.models.course import Course
from app.extensions import db

from sqlalchemy.exc import IntegrityError

def add_user_interaction(user_id, course_id, interaction_type):
    """
    Adds a user interaction to the database after validating the IDs.
    
    :param user_id: ID of the user
    :param course_id: ID of the course (not the primary key)
    :param interaction_type: Type of interaction (e.g., 'view', 'enrolled', 'complete', 'buy')
    :return: The created UserInteraction object or an error message
    """
    user = User.query.get(user_id)
    if not user:
        raise ValueError(f"User with ID {user_id} does not exist.")
    
    # Use filter_by() to query by course_id (not the primary key)
    course = Course.query.filter_by(course_id=course_id).first()
    if not course:
        raise ValueError(f"Course with course_id {course_id} does not exist.")
    
    interaction = UserInteraction(user_id=user_id, course_id=course_id, interaction_type=interaction_type)
    try:
        db.session.add(interaction)
        db.session.commit()
        return interaction
    except IntegrityError:
        db.session.rollback()  # Rollback the transaction to avoid leaving it in a broken state
        raise ValueError(f"Duplicate interaction: user_id={user_id}, course_id={course_id}, interaction_type={interaction_type}")

def get_user_interactions(user_id):
    """
    Retrieves all interactions for a given user.
    
    :param user_id: ID of the user
    :return: List of UserInteraction objects
    """
    interactions = UserInteraction.query.filter_by(user_id=user_id).all()
    return [interaction.to_dict() for interaction in interactions]

def get_course_interactions(course_id):
    """
    Retrieves all interactions for a given course.
    
    :param course_id: ID of the course
    :return: List of UserInteraction objects
    """
    interactions = UserInteraction.query.filter_by(course_id=course_id).all()
    return [interaction.to_dict() for interaction in interactions]

def delete_user_interaction_by_id(interaction_id):
    """
    Deletes a user interaction by its ID.
    
    :param interaction_id: ID of the interaction to delete
    :return: Success message or error message
    """
    interaction = UserInteraction.query.get(interaction_id)
    if not interaction:
        raise ValueError(f"Interaction with ID {interaction_id} does not exist.")
    
    db.session.delete(interaction)
    db.session.commit()
    return f"Interaction with ID {interaction_id} has been deleted."

def delete_user_interactions_by_user_id(user_id):
    """
    Deletes all interactions for a given user.
    
    :param user_id: ID of the user whose interactions are to be deleted
    :return: Success message or error message
    """
    interactions = UserInteraction.query.filter_by(user_id=user_id).all()
    if not interactions:
        raise ValueError(f"No interactions found for user with ID {user_id}.")
    
    for interaction in interactions:
        db.session.delete(interaction)
    
    db.session.commit()
    return f"All interactions for user with ID {user_id} have been deleted."