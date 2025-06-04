from flask import Blueprint, request, jsonify
from jsonschema import validate, ValidationError

from app.services.course.get_courses import get_all_courses, get_course_by_id, get_random_courses, get_recommended_courses_by_course_id, get_recommended_courses_by_user_id, get_courses
from app.services.course.create_courses import create_courses
from app.models.course_schema import add_courses_schema

course_bp = Blueprint('course_bp', __name__)

@course_bp.route('', methods=['GET'])
def get_courses_route():
    # Subject mapping:
    # 1 -> 'Business Finance'
    # 2 -> 'Graphics Design'
    # 3 -> 'Web Development'
    # 4 -> 'Musical Instruments'
    
    # Level may be 'Beginner Level', 'Intermediate Level', 'Expert Level', 'All Levels'
    # Level mapping:
    # 1 -> 'Beginner Level'
    # 2 -> 'Intermediate Level'
    # 3 -> 'Expert Level'
    # 0 -> 'All Levels'
    
    # is_paid may be 1 (paid) or 0 (free)
    
    # Order by num_subscribers, num_reviews, total_interactions, and total_users
    
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        
        # Parse subject and level to support comma-separated values
        subject = request.args.get('subject', default=None, type=str)
        if subject:
            subject = [int(s) for s in subject.split(',') if s.isdigit()]
        
        level = request.args.get('level', default=None, type=str)
        if level:
            level = [int(l) for l in level.split(',') if l.isdigit()]
        
        is_paid = request.args.get('is_paid', default=None, type=int)
        order_by = request.args.get('order_by', default='num_subscribers', type=str)
        order_direction = request.args.get('order_direction', default='desc', type=str)

        courses_paginate = get_courses(page, per_page, subject, level, is_paid, order_by, order_direction)
        courses_number = len(courses_paginate['courses'])
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully fetched {courses_number} courses',
            'data': courses_paginate
        }), 200
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': f'Validation error: {e.message}',
            'data': {}
        }), 400
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
        
# Colaborative test
@course_bp.route('/recommender2', methods=['GET'])
def get_recommended_courses_2_route():
    try:
        user_id = request.args.get('user_id', default='user_1', type=str)
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
        
        courses = get_recommended_courses_by_user_id(user_id, n)
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully fetched {len(courses)} recommended courses for user ID {user_id}',
            'data': courses
            }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching recommended courses for user ID {user_id}: {str(e)}',
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
