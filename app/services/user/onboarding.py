from app.models.user import User
from app.models.user_preference import UserPreferences
from app.extensions import db

def complete_onboarding(user_id, preferences):
    """
    Complete the onboarding process for a user by updating their preferences and marking onboarding as done.
    
    Format of preferences:
    {
        "subject": [
            "value1",
            "value2"
            ],
        "level": [
            "value1",
            "value2"
        ]
    }
    
    Allowed preference types:
    - "subject"
    - "level"
    
    Allows multiple preferences of the same type.
    
    Allowed values for "subject":
    - "Business Finance"
    - "Graphic Design"
    - "Web Development"
    - "Musical Instruments"
    
    Allowed values for "level":
    - "Beginner Level"
    - "Intermediate Level"
    - "Expert Level"
    - "All Levels"
    
    :param user_id: The ID of the user completing onboarding.
    :param preferences: A dictionary of user preferences to be saved.
    :return: The updated User object.
    """
    
    user = User.query.get(user_id)
    if not user:
        raise ValueError("User not found")
    
    if not isinstance(preferences, dict):
        raise ValueError("Preferences must be a dictionary")
    
    if "subject" not in preferences or "level" not in preferences:
        raise ValueError("Preferences must contain 'subject' and 'level' keys")
    
    if not all(isinstance(v, list) for v in preferences.values()):
        raise ValueError("All preference values must be lists")
    
    if not all(preferences["subject"]) or not all(preferences["level"]):
        raise ValueError("Preferences lists cannot be empty")
    
    allowed_subjects = ["Business Finance", "Graphic Design", "Web Development", "Musical Instruments"]
    allowed_levels = ["Beginner Level", "Intermediate Level", "Expert Level", "All Levels"]
    
    if not all(value in allowed_subjects for value in preferences["subject"]):
        raise ValueError(f"Invalid subject values. Allowed values are: {', '.join(allowed_subjects)}")
    
    if not all(value in allowed_levels for value in preferences["level"]):
        raise ValueError(f"Invalid level values. Allowed values are: {', '.join(allowed_levels)}")
    
    try:
        # Delete existing preferences
        UserPreferences.query.filter_by(user_id=user_id).delete()
        
        # Add new preferences
        for pref_type, values in preferences.items():
            if pref_type not in ["subject", "level"]:
                raise ValueError(f"Invalid preference type: {pref_type}")
            for value in values:
                new_preference = UserPreferences(user_id=user_id, type=pref_type, value=value)
                db.session.add(new_preference)
        
        # Mark onboarding as done
        user.onboarding_done = True
        db.session.commit()
        return user.to_dict()
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"An error occurred while completing onboarding: {str(e)}") from e



def get_user_preferences(user_id):
    """
    Retrieve the preferences of a user.

    :param user_id: The ID of the user whose preferences are to be retrieved.
    :return: A dictionary of user preferences with each type having a list of values.
    """
    
    user = User.query.get(user_id)
    if not user:
        raise ValueError("User not found")
    
    preferences = UserPreferences.query.filter_by(user_id=user_id).all()
    
    # Group preferences by type and return as lists
    grouped_preferences = {}
    for pref in preferences:
        if pref.type not in grouped_preferences:
            grouped_preferences[pref.type] = []
        grouped_preferences[pref.type].append(pref.value)
    
    return grouped_preferences

def reset_onboarding(user_id):
    """
    Reset the onboarding process for a user by deleting their preferences and marking onboarding as not done.
    
    :param user_id: The ID of the user whose onboarding is to be reset.
    :return: The updated User object.
    """
    
    user = User.query.get(user_id)
    if not user:
        raise ValueError("User not found")
    
    try:
        # Delete user preferences
        UserPreferences.query.filter_by(user_id=user_id).delete()
        
        # Mark onboarding as not done
        user.onboarding_done = False
        db.session.commit()
        return user.to_dict()
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"An error occurred while resetting onboarding: {str(e)}") from e