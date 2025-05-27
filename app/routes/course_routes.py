from flask import Blueprint, request, jsonify
from jsonschema import validate, ValidationError

from app.services.course.get_courses import get_all_courses, get_course_by_id, get_random_courses, get_recommended_courses_by_course_id
from app.services.course.create_courses import create_courses
from app.models.course_schema import add_courses_schema

course_bp = Blueprint('course_bp', __name__)

@course_bp.route('/', methods=['GET'])
def get_courses_route():
    try:
        courses = get_all_courses()
        return jsonify({
            'status': 'success',
            'message': 'Successfully fetched all courses',
            'data': courses
            }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching courses: {str(e)}',
            'data': {}
            }), 500

@course_bp.route('/<int:course_id>', methods=['GET'])
def get_course_by_id_route(course_id):
    try:
        course = get_course_by_id(course_id)
        if course:
            return jsonify({
                'status': 'success',
                'message': f'Successfully fetched course with ID {course_id}',
                'data': course
                }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': f'Course with ID {course_id} not found',
                'data': {}
                }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching course with ID {course_id}: {str(e)}',
            'data': {}
            }), 500
    
@course_bp.route('/random', methods=['GET'])
def get_random_courses_route():
    try:
        n = request.args.get('n', default=2, type=int)
        courses = get_random_courses(n)
        return jsonify({
            'status': 'success',
            'message': f'Successfully fetched {n} random courses of each subject',
            'data': courses
            }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching random courses: {str(e)}',
            'data': {}
            }), 500
        
@course_bp.route('/recommender1', methods=['GET'])
def get_recommended_courses_1_route():
    try:
        course_id = request.args.get('course_id', default=1, type=int)
        n = request.args.get('n', default=5, type=int)
        
        # Sanity check for n
        if n <= 0:
            return jsonify({
                'status': 'error',
                'message': 'Parameter n must be a positive integer',
                'data': {}
                }), 400
        
        if n > 1000:
            n = 1000  # Limit n to a maximum of 1000
        
        courses = get_recommended_courses_by_course_id(course_id, n)
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully fetched {len(courses)} recommended courses for course ID {course_id}',
            'data': courses
            }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching recommended courses for course ID {course_id}: {str(e)}',
            'data': {}
            }), 500


# Should not be needed in the current version
# @course_bp.route('/', methods=['POST'])
# def post_course():
#     data = request.get_json()
#     try:
#         validate(instance=data, schema=add_courses_schema)
    
#         create_courses(data)
        
#         return jsonify({
#                 'status': 'success',
#                 'message': f'Successfully added {len(data)} courses',
#                 'data': {}
#             }), 201
#     except ValidationError as e:
#         return jsonify({
#                 'status': 'error',
#                 'message': f'Validation error: {e.message}',
#                 'data': {}
#             }), 400
