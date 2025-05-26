from flask import Blueprint, request, jsonify
from jsonschema import validate, ValidationError
from app.models.user_schema import register_request_schema

from app.services.user.create_user import create_user
from app.services.helper.crypto import verify_password

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