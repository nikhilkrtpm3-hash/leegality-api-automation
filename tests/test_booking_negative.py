import pytest
from utils.booking_factory import create_booking_payload, create_booking_payload_with_dates


def register_response_booking(response, booking_cleanup):
    if response.status_code == 200:
        body = response.json()
        booking_id = body.get("bookingid")
        if booking_id is not None:
            booking_cleanup(booking_id)


@pytest.mark.negative
def test_negative_totalprice_should_be_rejected(api_client, booking_cleanup):
    payload = create_booking_payload(totalprice=-100)
    response = api_client.post("/booking", json=payload)
    register_response_booking(response, booking_cleanup)
    assert response.status_code in (400, 422), (
        f"Expected validation rejection for negative price; actual={response.status_code}, "
        f"body={response.text}. If accepted, record as a defect."
    )


@pytest.mark.negative
def test_checkout_before_checkin_should_be_rejected(api_client, booking_cleanup):
    payload = create_booking_payload_with_dates("2027-01-20", "2027-01-10")
    response = api_client.post("/booking", json=payload)
    register_response_booking(response, booking_cleanup)
    assert response.status_code in (400, 422), (
        f"Expected validation rejection for checkout before check-in; "
        f"actual={response.status_code}, body={response.text}. If accepted, record as a defect."
    )


@pytest.mark.negative
def test_zero_price_boundary(api_client, booking_cleanup):
    payload = create_booking_payload(totalprice=0)
    response = api_client.post("/booking", json=payload)
    register_response_booking(response, booking_cleanup)
    assert response.status_code in (200, 400, 422), response.text
    if response.status_code == 200:
        body = response.json()
        assert body.get("booking", {}).get("totalprice") == 0


@pytest.mark.negative
@pytest.mark.parametrize("missing_field", [
    "bookingdates",
    "depositpaid",
    "firstname",
    "lastname",
    "totalprice",
])
def test_missing_required_booking_field_is_rejected(
    api_client, booking_cleanup, missing_field
):
    payload = create_booking_payload()
    payload.pop(missing_field)
    response = api_client.post("/booking", json=payload)
    register_response_booking(response, booking_cleanup)
    assert response.status_code in (400, 422), (
        f"Expected validation rejection when missing {missing_field}; "
        f"status={response.status_code}, body={response.text}"
    )


@pytest.mark.negative
def test_empty_booking_payload_is_rejected(api_client):
    response = api_client.post("/booking", json={})
    assert response.status_code in (400, 422), (
        f"Expected empty-payload validation; status={response.status_code}, "
        f"body={response.text}"
    )


@pytest.mark.negative
def test_wrong_totalprice_type_should_be_rejected(api_client, booking_cleanup):
    payload = create_booking_payload()
    payload["totalprice"] = "not-a-number"
    response = api_client.post("/booking", json=payload)
    register_response_booking(response, booking_cleanup)
    assert response.status_code in (400, 422), (
        f"Expected type validation; actual={response.status_code}, body={response.text}"
    )


@pytest.mark.negative
def test_wrong_depositpaid_type_should_be_rejected(api_client, booking_cleanup):
    payload = create_booking_payload()
    payload["depositpaid"] = "not-a-boolean"
    response = api_client.post("/booking", json=payload)
    register_response_booking(response, booking_cleanup)
    assert response.status_code in (400, 422), (
        f"Expected depositpaid type validation; "
        f"status={response.status_code}, body={response.text}"
    )


@pytest.mark.negative
@pytest.mark.xfail(
    strict=True,
    reason="Known sandbox defect BUG-005: malformed booking dates are accepted",
)
@pytest.mark.parametrize("invalid_field", ["checkin", "checkout"])
def test_invalid_booking_date_format_should_be_rejected(
    api_client, booking_cleanup, invalid_field
):
    payload = create_booking_payload()
    payload["bookingdates"][invalid_field] = "not-a-date"
    response = api_client.post("/booking", json=payload)
    register_response_booking(response, booking_cleanup)
    assert response.status_code in (400, 422), (
        f"Expected {invalid_field} date validation; "
        f"status={response.status_code}, body={response.text}"
    )


@pytest.mark.negative
def test_nonexistent_booking_returns_not_found(api_client):
    response = api_client.get("/booking/-1")
    assert response.status_code == 404, response.text


@pytest.mark.negative
def test_put_without_auth_is_rejected(api_client, created_booking):
    booking_id, payload = created_booking
    response = api_client.put(f"/booking/{booking_id}", json=payload)
    assert response.status_code in (401, 403), (
        f"Expected unauthorized write; actual={response.status_code}, body={response.text}"
    )


@pytest.mark.negative
def test_patch_without_auth_is_rejected(api_client, created_booking):
    booking_id, _ = created_booking
    response = api_client.patch(f"/booking/{booking_id}", json={"firstname": "Unauthorized"})
    assert response.status_code in (401, 403), (
        f"Expected unauthorized write; actual={response.status_code}, body={response.text}"
    )


@pytest.mark.negative
def test_delete_without_auth_is_rejected(api_client, created_booking):
    booking_id, _ = created_booking
    response = api_client.delete(f"/booking/{booking_id}")
    assert response.status_code in (401, 403), (
        f"Expected unauthorized delete; actual={response.status_code}, body={response.text}"
    )
