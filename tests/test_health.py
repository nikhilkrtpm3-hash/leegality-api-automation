import pytest

@pytest.mark.smoke
def test_health_check(api_client):
    response = api_client.get("/ping")
    # Restful Booker commonly returns 201 for /ping; verify against current sandbox.
    assert response.status_code == 201, f"Unexpected health response: {response.status_code} {response.text}"
