# Defect Reports

The following behaviors were reproduced against the configured Restful Booker sandbox by the pytest suite. Booking IDs and generated names in response examples are run values and may differ on subsequent runs.

## BUG-001 — Negative booking totals are accepted

- **Severity:** High
- **Endpoint:** `POST /booking`
- **Preconditions:** None.
- **Request payload:**
  ```json
  {
    "firstname": "QAc305798e",
    "lastname": "Automationc305798e",
    "totalprice": -100,
    "depositpaid": true,
    "bookingdates": {
      "checkin": "2027-01-31",
      "checkout": "2027-02-03"
    },
    "additionalneeds": "Breakfast"
  }
  ```
- **Actual status:** `200`
- **Actual response:**
  ```json
  {
    "bookingid": 5172,
    "booking": {
      "firstname": "QAc305798e",
      "lastname": "Automationc305798e",
      "totalprice": -100,
      "depositpaid": true,
      "bookingdates": {
        "checkin": "2027-01-31",
        "checkout": "2027-02-03"
      },
      "additionalneeds": "Breakfast"
    }
  }
  ```
- **Expected:** Reject a negative total price with a client validation response.
- **Actual behavior:** A booking is created with `totalprice: -100`.
- **Reproduction:** Send the payload above to `POST /booking`; the test captures and cleans up the returned booking.
- **Impact:** Invalid negative financial values can be persisted as booking totals.

## BUG-002 — Checkout before check-in is accepted

- **Severity:** High
- **Endpoint:** `POST /booking`
- **Preconditions:** None.
- **Request payload:**
  ```json
  {
    "firstname": "QAce7e81ee",
    "lastname": "Automationce7e81ee",
    "totalprice": 150,
    "depositpaid": true,
    "bookingdates": {
      "checkin": "2027-01-20",
      "checkout": "2027-01-10"
    },
    "additionalneeds": "Breakfast"
  }
  ```
- **Actual status:** `200`
- **Actual response:**
  ```json
  {
    "bookingid": 26,
    "booking": {
      "firstname": "QAce7e81ee",
      "lastname": "Automationce7e81ee",
      "totalprice": 150,
      "depositpaid": true,
      "bookingdates": {
        "checkin": "2027-01-20",
        "checkout": "2027-01-10"
      },
      "additionalneeds": "Breakfast"
    }
  }
  ```
- **Expected:** Reject a checkout date earlier than check-in.
- **Actual behavior:** A booking with the invalid date range is created.
- **Reproduction:** Send the payload above to `POST /booking`; the test captures and cleans up the returned booking.
- **Impact:** Impossible stay ranges can be stored.

## BUG-003 — Missing booking fields cause server errors

- **Severity:** Medium
- **Endpoint:** `POST /booking`
- **Preconditions:** None.
- **Request payload:** A valid generated booking payload with one required field omitted. For example, the `bookingdates` case contains:
  ```json
  {
    "firstname": "QA<generated>",
    "lastname": "Automation<generated>",
    "totalprice": 150,
    "depositpaid": true,
    "additionalneeds": "Breakfast"
  }
  ```
  The same test independently omitted `depositpaid`, `firstname`, `lastname`, and `totalprice`; an empty JSON object was also tested.
- **Actual status:** `500`
- **Actual response:** `Internal Server Error`
- **Expected:** Reject invalid input with a client validation response such as `400` or `422`.
- **Actual behavior:** Requests missing required fields, including `{}`, produce a server error.
- **Reproduction:** Submit `{}` or submit a complete booking payload with one of the fields listed above removed.
- **Impact:** Invalid client input causes server-side failures instead of controlled validation responses.

## BUG-004 — Invalid field types are silently coerced

- **Severity:** Medium
- **Endpoint:** `POST /booking`
- **Preconditions:** None.
- **Request payloads:**
  ```json
  {
    "firstname": "QAb81b66ee",
    "lastname": "Automationb81b66ee",
    "totalprice": "not-a-number",
    "depositpaid": true,
    "bookingdates": {
      "checkin": "2027-05-29",
      "checkout": "2027-06-01"
    },
    "additionalneeds": "Breakfast"
  }
  ```
  Separately, a valid generated payload with `firstname: "QA4725c37e"`, `lastname: "Automation4725c37e"`, `totalprice: 150`, `depositpaid: "not-a-boolean"`, dates `2027-08-15` through `2027-08-18`, and `additionalneeds: "Breakfast"` was sent.
- **Actual status:** `200` for both.
- **Actual responses:**
  - Invalid total price:
    ```json
    {
      "bookingid": 119,
      "booking": {
        "firstname": "QAb81b66ee",
        "lastname": "Automationb81b66ee",
        "totalprice": null,
        "depositpaid": true,
        "bookingdates": {
          "checkin": "2027-05-29",
          "checkout": "2027-06-01"
        },
        "additionalneeds": "Breakfast"
      }
    }
    ```
  - Invalid deposit flag:
    ```json
    {
      "bookingid": 130,
      "booking": {
        "firstname": "QA4725c37e",
        "lastname": "Automation4725c37e",
        "totalprice": 150,
        "depositpaid": true,
        "bookingdates": {
          "checkin": "2027-08-15",
          "checkout": "2027-08-18"
        },
        "additionalneeds": "Breakfast"
      }
    }
    ```
- **Expected:** Reject values with types that do not match the booking contract.
- **Actual behavior:** The API accepts both requests and coerces the invalid fields.
- **Reproduction:** Send either payload to `POST /booking`; the tests capture and clean up returned bookings.
- **Impact:** Incorrect or unintended values may be stored without the caller being informed.

## BUG-005 — Invalid booking dates are accepted and normalized

- **Severity:** Medium
- **Endpoint:** `POST /booking`
- **Preconditions:** None.
- **Request payloads:**
  - Check-in case: `firstname: "QA185df865"`, `lastname: "Automation185df865"`, `totalprice: 150`, `depositpaid: true`, `bookingdates: {"checkin": "not-a-date", "checkout": "2027-09-24"}`, and `additionalneeds: "Breakfast"`.
  - Checkout case: `firstname: "QAe2cdfa8c"`, `lastname: "Automatione2cdfa8c"`, `totalprice: 150`, `depositpaid: true`, `bookingdates: {"checkin": "2026-12-05", "checkout": "not-a-date"}`, and `additionalneeds: "Breakfast"`.
- **Actual status:** `200` for each case.
- **Actual responses:**
  - Invalid check-in:
    ```json
    {
      "bookingid": 151,
      "booking": {
        "firstname": "QA185df865",
        "lastname": "Automation185df865",
        "totalprice": 150,
        "depositpaid": true,
        "bookingdates": {
          "checkin": "0NaN-aN-aN",
          "checkout": "2027-09-24"
        },
        "additionalneeds": "Breakfast"
      }
    }
    ```
  - Invalid checkout:
    ```json
    {
      "bookingid": 170,
      "booking": {
        "firstname": "QAe2cdfa8c",
        "lastname": "Automatione2cdfa8c",
        "totalprice": 150,
        "depositpaid": true,
        "bookingdates": {
          "checkin": "2026-12-05",
          "checkout": "0NaN-aN-aN"
        },
        "additionalneeds": "Breakfast"
      }
    }
    ```
- **Expected:** Reject invalid date formats with a client validation response.
- **Actual behavior:** Both requests create bookings and return malformed normalized dates.
- **Reproduction:** Submit each malformed date in a booking payload to `POST /booking`; the tests capture and clean up returned bookings.
- **Impact:** Persisted malformed dates can break later filtering or booking operations.

## Observation — Booking date filters omit dynamically created records

- **Status:** Observation; behavior needs investigation against the sandbox's current date-filter semantics.
- **Endpoint:** `GET /booking`
- **Preconditions:** Create a booking using the test factory, which generates unique names and dates, then filter by its exact check-in date.
- **Request:** `GET /booking?checkin=2033-04-29`
- **Actual status/body:** `200`, `[]`; the dynamically created booking ID `819` was not present.
- **Combined filter observation:** Querying with `firstname=QA2ffaf51f`, `lastname=Automation2ffaf51f`, `checkin=2030-04-25`, and `checkout=2030-04-28` returned `200` with `[]` for the created booking ID `851`.
- **Expected:** Where these documented filters are supported, a created booking matching its exact filter values should be included.
- **Reproduction:** Run `test_list_booking_filter_by_booking_date[checkin]` or `test_list_booking_combined_filters_match_created_record`; names and dates are generated dynamically.
- **Impact:** Date-filter results may not include bookings matching their stored date values.
