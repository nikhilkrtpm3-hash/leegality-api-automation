"""Shared fixtures. Tests create their own records and attempt cleanup."""
import pytest
from config.config import USERNAME, PASSWORD
from utils.api_client import APIClient
from utils.booking_factory import create_booking_payload


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_token(api_client):
    response = api_client.post("/auth", json={
        "username": USERNAME,
        "password": PASSWORD,
    })
    assert response.status_code == 200, (
        f"Auth failed: status={response.status_code}, body={response.text}"
    )
    token = response.json().get("token")
    assert token, f"Token missing from auth response: {response.text}"
    return token


@pytest.fixture
def auth_headers(auth_token):
    return {"Cookie": f"token={auth_token}"}


@pytest.fixture
def booking_cleanup(api_client, auth_headers):
    booking_ids = []

    def register(booking_id):
        booking_ids.append(booking_id)

    yield register
    for booking_id in booking_ids:
        # Best-effort cleanup. Avoid masking the test's original failure.
        try:
            api_client.delete(f"/booking/{booking_id}", headers=auth_headers)
        except Exception:
            pass


@pytest.fixture
def created_booking(api_client, booking_cleanup):
    payload = create_booking_payload()
    response = api_client.post("/booking", json=payload)
    assert response.status_code == 200, (
        f"Create booking failed: status={response.status_code}, body={response.text}"
    )
    body = response.json()
    booking_id = body.get("bookingid")
    assert booking_id is not None, f"bookingid missing: {response.text}"
    booking_cleanup(booking_id)
    yield booking_id, payload
