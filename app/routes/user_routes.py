from flask import Blueprint, request, jsonify
from jsonschema import validate, ValidationError
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required

from app.models.user_schema import register_request_schema
from app.models.user_preference_schema import create_preference_request_schema

from app.services.user.create_user import create_user
from app.services.user.get_user import get_user_by_id, get_user_by_username, get_password_hash_by_username
from app.services.user.onboarding import complete_onboarding, get_user_preferences, reset_onboarding

from app.services.helper.crypto import verify_password
from datetime import timedelta

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/register', methods=['POST'])
def register_user():
    """
    Endpoint to register a new user.
    Expects JSON payload with 'username', 'email', and 'password'.
    """
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No data provided',
            'data': {}
        }), 400

    try:
        validate(instance=data, schema=register_request_schema)
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': f'Invalid payload: {e.message}',
            'data': {}
        }), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    try:
        user = create_user(username, email, password)
        return jsonify({
            'status': 'success',
            'message': 'User registered successfully',
            'data': user
        }), 201
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error creating user: {str(e)}',
            'data': {}
        }), 500
        
@user_bp.route('/login', methods=['POST'])
def login_user():
    """
    Endpoint to log in a user.
    Expects JSON payload with 'username' and 'password'.
    """
    
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No data provided',
            'data': {}
        }), 400

    username = data.get('username')
    password = data.get('password')
    
    password_hash = get_password_hash_by_username(username)
    user = get_user_by_username(username)
    
    if not password_hash:
        return jsonify({
            'status': 'error',
            'message': 'User not found',
            'data': {}
        }), 404
    
    if not verify_password(password, password_hash):
        return jsonify({
            'status': 'error',
            'message': 'Invalid password',
            'data': {}
        }), 401
    
    # Successful login
    access_token = create_access_token(identity=user['username'], expires_delta=timedelta(days=3))
    return jsonify({
        'status': 'success',
        'message': 'Login successful',
        'data': {
            'access_token': access_token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
        }
    }), 200
    
@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Endpoint to get the current logged-in user's information.
    Requires a valid JWT token.
    """
    
    try:
        username = get_jwt_identity()
        user = get_user_by_username(username)
        user_preferences = get_user_preferences(user['id'])
        return jsonify({
            'status': 'success',
            'message': 'User retrieved successfully',
            'data': {
                'user': user,
                'preferences': user_preferences
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error retrieving user: {str(e)}',
            'data': {}
        }), 500
        
@user_bp.route('/onboarding', methods=['POST'])
@jwt_required()
def complete_user_onboarding():
    """
    Endpoint to complete user onboarding.
    Requires a valid JWT token.
    
    Expects JSON payload with 'preferences':
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
    """
    
    try:
        username = get_jwt_identity()
        user = get_user_by_username(username)
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found',
                'data': {}
            }), 404
        
        if user['onboarding_done']:
            return jsonify({
                'status': 'error',
                'message': 'Onboarding already completed',
                'data': user
            }), 400
            
        data = request.get_json(silent=True)
        validate(instance=data, schema=create_preference_request_schema)
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Invalid payload',
                'data': {}
            }), 400
            
        complete_onboarding(user['id'], data)
        user = get_user_by_id(user['id'])
        user_preferences = get_user_preferences(user['id'])
        
        return jsonify({
            'status': 'success',
            'message': 'Onboarding completed successfully',
            'data': {
                'user': user,
                'preferences': user_preferences
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error completing onboarding: {str(e)}',
            'data': {}
        }), 500
        
@user_bp.route('/onboarding', methods=['DELETE'])
@jwt_required()
def reset_user_onboarding():
    """
    Endpoint to reset user onboarding.
    Requires a valid JWT token.
    """
    
    try:
        username = get_jwt_identity()
        user = get_user_by_username(username)
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found',
                'data': {}
            }), 404
            
        if not user['onboarding_done']:
            return jsonify({
                'status': 'error',
                'message': 'Onboarding not completed yet',
                'data': user
            }), 400
            
        reset_onboarding(user['id'])
        user = get_user_by_id(user['id'])
        user_preferences = get_user_preferences(user['id'])
        return jsonify({
            'status': 'success',
            'message': 'Onboarding reset successfully',
            'data': {
                'user': user,
                'preferences': user_preferences
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error resetting onboarding: {str(e)}',
            'data': {}
        }), 500