import pytest
from utils.booking_factory import create_booking_payload


@pytest.mark.create
@pytest.mark.smoke
def test_create_booking_returns_id_and_matching_booking(api_client):
    payload = create_booking_payload()
    response = api_client.post("/booking", json=payload)
    assert response.status_code == 200, response.text
    body = response.json()
    assert isinstance(body.get("bookingid"), int)
    assert body.get("booking") == payload
    # Cleanup the record created by this standalone test.
    token_response = api_client.post("/auth", json={"username": "admin", "password": "password123"})
    token = token_response.json().get("token")
    if token:
        api_client.delete(f"/booking/{body['bookingid']}", headers={"Cookie": f"token={token}"})
