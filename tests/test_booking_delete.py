import pytest


@pytest.mark.delete
def test_delete_booking_then_get_returns_not_found(api_client, created_booking, auth_headers):
    booking_id, _ = created_booking
    response = api_client.delete(f"/booking/{booking_id}", headers=auth_headers)
    assert response.status_code == 201, response.text
    get_response = api_client.get(f"/booking/{booking_id}")
    assert get_response.status_code == 404, get_response.text


@pytest.mark.delete
def test_delete_nonexistent_booking_returns_error(api_client, auth_headers):
    response = api_client.delete("/booking/-1", headers=auth_headers)
    assert response.status_code >= 400, (
        f"DELETE unexpectedly succeeded for nonexistent ID; "
        f"status={response.status_code}, body={response.text}"
    )


@pytest.mark.delete
def test_delete_already_deleted_booking_returns_error(
    api_client, created_booking, auth_headers
):
    booking_id, _ = created_booking
    first_response = api_client.delete(
        f"/booking/{booking_id}", headers=auth_headers
    )
    assert first_response.status_code == 201, first_response.text
    second_response = api_client.delete(
        f"/booking/{booking_id}", headers=auth_headers
    )
    assert second_response.status_code >= 400, (
        f"Second DELETE unexpectedly succeeded; status={second_response.status_code}, "
        f"body={second_response.text}"
    )
    get_response = api_client.get(f"/booking/{booking_id}")
    assert get_response.status_code == 404, get_response.text


@pytest.mark.delete
def test_delete_with_invalid_token_preserves_booking(api_client, created_booking):
    booking_id, original = created_booking
    response = api_client.delete(
        f"/booking/{booking_id}", headers={"Cookie": "token=invalid-token"}
    )
    assert response.status_code in (401, 403), (
        f"Expected unauthorized DELETE; status={response.status_code}, body={response.text}"
    )
    current = api_client.get(f"/booking/{booking_id}")
    assert current.status_code == 200, current.text
    assert current.json() == original, (
        f"Unauthorized DELETE changed booking; response status={response.status_code}, "
        f"body={response.text}"
    )
