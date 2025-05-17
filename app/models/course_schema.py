# Define the schema for validation
add_courses_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "course_id": {
                "type": "integer",
                "description": "The unique integer ID of the course."
            },
            "course_title": {
                "type": "string",
                "maxLength": 100,
                "description": "The title of the course."
            },
            "url": {
                "type": "string",
                "maxLength": 255,
                "description": "The URL of the course."
            },
            "is_paid": {
                "type": "boolean",
                "description": "Whether the course is paid or not."
            },
            "price": {
                "type": "integer",
                "description": "The price of the course."
            },
            "num_subscribers": {
                "type": "integer",
                "description": "Number of subscribers for the course."
            },
            "num_reviews": {
                "type": "integer",
                "description": "Number of reviews for the course."
            },
            "num_lectures": {
                "type": "integer",
                "description": "Number of lectures in the course."
            },
            "level": {
                "type": "string",
                "maxLength": 50,
                "description": "The level of the course."
            },
            "content_duration": {
                "type": "number",
                "description": "Duration of the course content in hours."
            },
            "published_timestamp": {
                "type": "string",
                "maxLength": 50,
                "description": "The published timestamp of the course."
            },
            "subject": {
                "type": "string",
                "maxLength": 50,
                "description": "The subject of the course."
            }
        },
        "required": [
            "course_id",
            "course_title",
            "url",
            "is_paid",
            "price",
            "num_subscribers",
            "num_reviews",
            "num_lectures",
            "level",
            "content_duration",
            "published_timestamp",
            "subject"
        ],
        "additionalProperties": False
    },
    "minItems": 1,
}