import pytest
from config.config import USERNAME, PASSWORD


@pytest.mark.auth
def test_auth_valid_credentials_returns_token(api_client):
    response = api_client.post("/auth", json={"username": USERNAME, "password": PASSWORD})
    assert response.status_code == 200, response.text
    assert isinstance(response.json().get("token"), str)
    assert response.json()["token"]


@pytest.mark.auth
@pytest.mark.parametrize("credentials", [
    {"username": "wrong-user", "password": "password123"},
    {"username": "admin", "password": "wrong-password"},
    {},
])
def test_auth_invalid_credentials_rejected(api_client, credentials):
    response = api_client.post("/auth", json=credentials)
    assert response.status_code == 200, (
        "Restful Booker may return 200 with a reason field for invalid auth; "
        f"inspect response: {response.text}"
    )
    body = response.json()
    assert not body.get("token"), f"Invalid credentials unexpectedly issued token: {body}"
    assert body.get("reason"), f"Expected auth failure reason: {body}"
