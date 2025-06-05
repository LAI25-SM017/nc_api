create_preference_request_schema = {
    "type": "object",
    "properties": {
        "subject": {
            "type": "array",
            "items": {
                "type": "string",
                "maxLength": 50,
                "description": "A subject preference of the user."
            },
        },
        "level": {
            "type": "array",
            "items": {
                "type": "string",
                "maxLength": 50,
                "description": "A level preference of the user."
            },
        },
    },
    "required": ["subject", "level"],
    "additionalProperties": False
}