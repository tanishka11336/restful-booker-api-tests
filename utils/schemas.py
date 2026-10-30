"""JSON schemas used for response contract validation."""

BOOKING_SCHEMA = {
    "type": "object",
    "required": ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"],
    "properties": {
        "firstname": {"type": "string"},
        "lastname": {"type": "string"},
        "totalprice": {"type": "number"},
        "depositpaid": {"type": "boolean"},
        "bookingdates": {
            "type": "object",
            "required": ["checkin", "checkout"],
            "properties": {
                "checkin": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
                "checkout": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
            },
        },
        "additionalneeds": {"type": "string"},
    },
}

CREATE_BOOKING_SCHEMA = {
    "type": "object",
    "required": ["bookingid", "booking"],
    "properties": {
        "bookingid": {"type": "integer"},
        "booking": BOOKING_SCHEMA,
    },
}

BOOKING_ID_LIST_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["bookingid"],
        "properties": {"bookingid": {"type": "integer"}},
    },
}

TOKEN_SCHEMA = {
    "type": "object",
    "required": ["token"],
    "properties": {"token": {"type": "string", "minLength": 1}},
}
