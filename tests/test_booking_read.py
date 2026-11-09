import pytest


def assert_booking_id_list(response):
    assert response.status_code == 200, response.text
    body = response.json()
    assert isinstance(body, list), f"Expected booking ID list, got: {response.text}"
    assert all(
        isinstance(item, dict) and isinstance(item.get("bookingid"), int)
        for item in body
    ), f"Unexpected booking ID response format: {response.text}"
    return body


@pytest.mark.read
def test_get_created_booking_matches_payload(api_client, created_booking):
    booking_id, payload = created_booking
    response = api_client.get(f"/booking/{booking_id}")
    assert response.status_code == 200, response.text
    assert response.json() == payload


@pytest.mark.read
def test_list_booking_ids_has_expected_shape(api_client):
    response = api_client.get("/booking")
    assert response.status_code == 200, response.text
    body = response.json()
    assert isinstance(body, list)
    for item in body:
        assert isinstance(item, dict)
        assert isinstance(item.get("bookingid"), int)


@pytest.mark.read
def test_list_booking_filter_by_firstname(api_client, created_booking):
    booking_id, payload = created_booking
    response = api_client.get("/booking", params={"firstname": payload["firstname"]})
    results = assert_booking_id_list(response)
    ids = [item["bookingid"] for item in results]
    assert booking_id in ids
    for result in results:
        booking_response = api_client.get(f"/booking/{result['bookingid']}")
        assert booking_response.status_code == 200, booking_response.text
        assert booking_response.json()["firstname"] == payload["firstname"], (
            f"Firstname filter returned a nonmatching booking ID {result['bookingid']}"
        )


@pytest.mark.read
def test_list_booking_filter_by_lastname(api_client, created_booking):
    booking_id, payload = created_booking
    response = api_client.get("/booking", params={"lastname": payload["lastname"]})
    results = assert_booking_id_list(response)
    ids = [item["bookingid"] for item in results]
    assert booking_id in ids
    for result in results:
        booking_response = api_client.get(f"/booking/{result['bookingid']}")
        assert booking_response.status_code == 200, booking_response.text
        assert booking_response.json()["lastname"] == payload["lastname"], (
            f"Lastname filter returned a nonmatching booking ID {result['bookingid']}"
        )


@pytest.mark.read
@pytest.mark.parametrize(
    "date_field",
    [
        pytest.param(
            "checkin",
            marks=pytest.mark.xfail(
                strict=True,
                reason="Known sandbox observation: check-in date filter omits created bookings",
            ),
        ),
        "checkout",
    ],
)
def test_list_booking_filter_by_booking_date(api_client, created_booking, date_field):
    booking_id, payload = created_booking
    date_value = payload["bookingdates"][date_field]
    response = api_client.get("/booking", params={date_field: date_value})
    results = assert_booking_id_list(response)
    ids = [item["bookingid"] for item in results]
    assert booking_id in ids, (
        f"Date filter {date_field}={date_value} omitted created booking; "
        f"response={response.text}"
    )
    booking_response = api_client.get(f"/booking/{booking_id}")
    assert booking_response.status_code == 200, booking_response.text
    assert booking_response.json()["bookingdates"][date_field] == date_value


@pytest.mark.read
def test_list_booking_combined_filters_match_created_record(api_client, created_booking):
    booking_id, payload = created_booking
    params = {
        "firstname": payload["firstname"],
        "lastname": payload["lastname"],
        "checkin": payload["bookingdates"]["checkin"],
        "checkout": payload["bookingdates"]["checkout"],
    }
    response = api_client.get("/booking", params=params)
    results = assert_booking_id_list(response)
    ids = [item["bookingid"] for item in results]
    assert booking_id in ids, (
        f"Combined filters omitted created booking; params={params}, response={response.text}"
    )
