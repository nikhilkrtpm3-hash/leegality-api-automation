from datetime import date, timedelta

import pytest
from utils.booking_factory import create_booking_payload


@pytest.mark.update
def test_put_booking_updates_full_object(api_client, created_booking, auth_headers):
    booking_id, _ = created_booking
    payload = create_booking_payload(totalprice=275)
    payload["firstname"] = "PUTUpdated"
    response = api_client.put(f"/booking/{booking_id}", json=payload, headers=auth_headers)
    assert response.status_code == 200, response.text
    assert response.json() == payload
    current = api_client.get(f"/booking/{booking_id}")
    assert current.status_code == 200, current.text
    assert current.json() == payload


@pytest.mark.update
def test_patch_booking_changes_only_requested_field(api_client, created_booking, auth_headers):
    booking_id, original = created_booking
    patch = {"firstname": "PATCHUpdated"}
    response = api_client.patch(f"/booking/{booking_id}", json=patch, headers=auth_headers)
    assert response.status_code == 200, response.text
    assert response.json()["firstname"] == patch["firstname"], response.text
    updated = api_client.get(f"/booking/{booking_id}")
    assert updated.status_code == 200, updated.text
    body = updated.json()
    assert body["firstname"] == patch["firstname"]
    for field in ("lastname", "totalprice", "depositpaid", "bookingdates", "additionalneeds"):
        assert body[field] == original[field], f"PATCH unexpectedly changed {field}"


@pytest.mark.update
@pytest.mark.parametrize("field", ["lastname", "totalprice", "depositpaid", "bookingdates"])
def test_patch_changes_only_requested_field(api_client, created_booking, auth_headers, field):
    booking_id, original = created_booking
    replacement = {
        "lastname": "PATCHedLastname",
        "totalprice": original["totalprice"] + 1,
        "depositpaid": not original["depositpaid"],
        "bookingdates": {
            "checkin": (date.today() + timedelta(days=20)).isoformat(),
            "checkout": (date.today() + timedelta(days=23)).isoformat(),
        },
    }[field]
    patch = {field: replacement}
    response = api_client.patch(f"/booking/{booking_id}", json=patch, headers=auth_headers)
    assert response.status_code == 200, response.text
    assert response.json()[field] == replacement, response.text

    updated = api_client.get(f"/booking/{booking_id}")
    assert updated.status_code == 200, updated.text
    body = updated.json()
    assert body[field] == replacement
    for unchanged_field, value in original.items():
        if unchanged_field != field:
            assert body[unchanged_field] == value, (
                f"PATCH of {field} unexpectedly changed {unchanged_field}"
            )


@pytest.mark.update
def test_put_with_invalid_token_does_not_modify_booking(api_client, created_booking):
    booking_id, original = created_booking
    replacement = create_booking_payload(totalprice=original["totalprice"] + 100)
    response = api_client.put(
        f"/booking/{booking_id}",
        json=replacement,
        headers={"Cookie": "token=invalid-token"},
    )
    assert response.status_code in (401, 403), (
        f"Expected unauthorized PUT; status={response.status_code}, body={response.text}"
    )

    current = api_client.get(f"/booking/{booking_id}")
    assert current.status_code == 200, current.text
    assert current.json() == original, (
        f"Unauthorized PUT changed booking; response status={response.status_code}, "
        f"body={response.text}"
    )


@pytest.mark.update
def test_patch_with_invalid_token_does_not_modify_booking(api_client, created_booking):
    booking_id, original = created_booking
    response = api_client.patch(
        f"/booking/{booking_id}",
        json={"firstname": "UnauthorizedPatch"},
        headers={"Cookie": "token=invalid-token"},
    )
    assert response.status_code in (401, 403), (
        f"Expected unauthorized PATCH; status={response.status_code}, body={response.text}"
    )

    current = api_client.get(f"/booking/{booking_id}")
    assert current.status_code == 200, current.text
    assert current.json() == original, (
        f"Unauthorized PATCH changed booking; response status={response.status_code}, "
        f"body={response.text}"
    )


@pytest.mark.update
def test_put_nonexistent_booking_does_not_create_record(api_client, auth_headers):
    booking_id = -1
    payload = create_booking_payload()
    response = api_client.put(
        f"/booking/{booking_id}", json=payload, headers=auth_headers
    )
    assert response.status_code >= 400, (
        f"PUT unexpectedly succeeded for nonexistent ID; "
        f"status={response.status_code}, body={response.text}"
    )
    current = api_client.get(f"/booking/{booking_id}")
    assert current.status_code == 404, current.text


@pytest.mark.update
@pytest.mark.parametrize("missing_field", [
    "firstname", "lastname", "totalprice", "depositpaid", "bookingdates"
])
def test_put_missing_required_field_is_rejected(
    api_client, created_booking, auth_headers, missing_field
):
    booking_id, _ = created_booking
    payload = create_booking_payload()
    payload.pop(missing_field)
    response = api_client.put(
        f"/booking/{booking_id}", json=payload, headers=auth_headers
    )
    assert response.status_code in (400, 422), (
        f"Expected validation rejection when PUT is missing {missing_field}; "
        f"status={response.status_code}, body={response.text}"
    )


@pytest.mark.update
@pytest.mark.parametrize(
    "body_kwargs",
    [{"json": {}}, {"data": ""}],
    ids=["empty-json-object", "empty-request-body"],
)
def test_put_empty_payload_is_rejected(
    api_client, created_booking, auth_headers, body_kwargs
):
    booking_id, _ = created_booking
    headers = {**auth_headers, "Content-Type": "application/json"}
    response = api_client.put(
        f"/booking/{booking_id}", headers=headers, **body_kwargs
    )
    assert response.status_code in (400, 422), (
        f"Expected empty PUT payload rejection; "
        f"status={response.status_code}, body={response.text}"
    )


@pytest.mark.update
@pytest.mark.parametrize(
    "body_kwargs",
    [{"json": {}}, {"data": ""}],
    ids=["empty-json-object", "empty-request-body"],
)
def test_patch_empty_payload_captures_api_response(
    api_client, created_booking, auth_headers, body_kwargs
):
    booking_id, original = created_booking
    headers = {**auth_headers, "Content-Type": "application/json"}
    response = api_client.patch(
        f"/booking/{booking_id}", headers=headers, **body_kwargs
    )
    assert response.status_code in (200, 400, 422), (
        f"Unexpected empty PATCH response; "
        f"status={response.status_code}, body={response.text}"
    )
    if response.status_code < 300:
        current = api_client.get(f"/booking/{booking_id}")
        assert current.status_code == 200, current.text
        assert current.json() == original, "Empty PATCH changed booking data"


@pytest.mark.update
def test_patch_nonexistent_booking_does_not_create_record(api_client, auth_headers):
    booking_id = -1
    response = api_client.patch(
        f"/booking/{booking_id}",
        json={"firstname": "NoSuchBooking"},
        headers=auth_headers,
    )
    assert response.status_code >= 400, (
        f"PATCH unexpectedly succeeded for nonexistent ID; "
        f"status={response.status_code}, body={response.text}"
    )
    current = api_client.get(f"/booking/{booking_id}")
    assert current.status_code == 404, current.text


@pytest.mark.update
def test_patch_unsupported_field_does_not_change_booking(api_client, created_booking, auth_headers):
    booking_id, original = created_booking
    response = api_client.patch(
        f"/booking/{booking_id}",
        json={"unsupported_field": "ignored"},
        headers=auth_headers,
    )
    assert response.status_code in (200, 400, 422), (
        f"Unexpected unsupported-field PATCH response; "
        f"status={response.status_code}, body={response.text}"
    )
    if response.status_code < 300:
        current = api_client.get(f"/booking/{booking_id}")
        assert current.status_code == 200, current.text
        assert current.json() == original, "Unsupported PATCH field changed booking data"
