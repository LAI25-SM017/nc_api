register_request_schema = {
    "type": "object",
    "properties": {
        "username": {
            "type": "string",
            "maxLength": 50,
            "description": "The username of the user."
        },
        "email": {
            "type": "string",
            "format": "email",
            "maxLength": 100,
            "description": "The email address of the user."
        },
        "password": {
            "type": "string",
            "maxLength": 255,
            "description": "The password of the user."
        }
    },
    "required": ["username", "email", "password"],
    "additionalProperties": False
}