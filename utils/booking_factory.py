"""Booking payload factory. Dates are generated relative to execution date."""
from datetime import date, timedelta
from uuid import uuid4


def create_booking_payload(totalprice=150, checkin_offset=None, stay_length=3):
    unique = uuid4().hex[:8]
    if checkin_offset is None:
        checkin_offset = int(unique, 16) % 3650 + 10
    checkin = date.today() + timedelta(days=checkin_offset)
    checkout = checkin + timedelta(days=stay_length)
    return {
        "firstname": f"QA{unique}",
        "lastname": f"Automation{unique}",
        "totalprice": totalprice,
        "depositpaid": True,
        "bookingdates": {
            "checkin": checkin.isoformat(),
            "checkout": checkout.isoformat(),
        },
        "additionalneeds": "Breakfast",
    }


def create_booking_payload_with_dates(checkin, checkout, totalprice=150):
    payload = create_booking_payload(totalprice=totalprice)
    payload["bookingdates"] = {"checkin": checkin, "checkout": checkout}
    return payload
