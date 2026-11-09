import pytest
from jsonschema import validate

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
                "checkin": {"type": "string"},
                "checkout": {"type": "string"},
            },
        },
        "additionalneeds": {"type": ["string", "null"]},
    },
}


@pytest.mark.contract
def test_booking_response_matches_schema(api_client, created_booking):
    booking_id, _ = created_booking
    response = api_client.get(f"/booking/{booking_id}")
    assert response.status_code == 200, response.text
    validate(instance=response.json(), schema=BOOKING_SCHEMA)
