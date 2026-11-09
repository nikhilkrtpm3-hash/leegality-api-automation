# Restful Booker API Automation

## Overview
Pytest-based API automation for the Restful Booker sandbox. The suite covers the endpoints in the assignment: health check, booking list/filter, booking read/create/PUT/PATCH/DELETE, and authentication.

## Stack
Python, Pytest, Requests, pytest-html, Allure Pytest, JSON Schema.

## Coverage
- Core create → read → PUT → PATCH → delete journey
- Auth token retrieval plus invalid-token PUT/PATCH/DELETE checks that verify booking state is preserved
- PATCH field-level update and preservation checks
- Booking list filters by first name, last name, check-in, checkout, and combined criteria
- Negative/boundary tests: missing required fields, wrong types, negative/zero price, invalid date formats, checkout before check-in, empty payloads, and non-existent IDs
- Booking response schema validation
- Dynamically generated unique names and varied dates; accepted malformed POST bookings are registered for fixture cleanup

## Environment and shared API
The sandbox is shared and resets periodically. Tests create their own booking records and do not rely on seeded IDs. A fixture attempts cleanup after tests. Avoid running destructive tests concurrently against the same record. The public service may have cold starts or transient availability issues; timeout is configurable through `REQUEST_TIMEOUT`. Retries should be limited to transient transport/server errors and must not hide assertion failures.

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
pytest
pytest -m smoke
pytest -m negative
```

## HTML report
```bash
pytest --html=reports/report.html --self-contained-html
```

## Allure report
```bash
pytest --alluredir=reports/allure-results
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

## Defects
Reproduced API defects and observations belong in `docs/BUGS.md`, with severity or investigation status, request details, actual response, expected behavior, reproduction steps, and impact. Negative tests intentionally fail when the sandbox accepts malformed data or returns an unexpected server error.

The invalid-date and check-in-filter tests for the currently documented sandbox findings are marked `xfail(strict=True)` so they report known behavior without masking a future fix. A passing result is reported as an unexpected pass and should prompt review of the corresponding defect report. Other negative tests continue to fail when they expose an unclassified defect.

## Limitations
This is a shared public sandbox, not a dedicated environment. It may reset data and exhibit variable response times. The suite is functional API regression coverage, not a production-scale performance test. Confirm expected response behavior against the current API documentation and record observed sandbox deviations.
