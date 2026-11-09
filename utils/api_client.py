"""Small reusable Requests client with timeout and request/response diagnostics."""
import requests
from config.config import BASE_URL, REQUEST_TIMEOUT


class APIClient:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = BASE_URL
        self.timeout = REQUEST_TIMEOUT

    def request(self, method, endpoint, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return self.session.request(method, f"{self.base_url}{endpoint}", **kwargs)

    def get(self, endpoint, **kwargs):
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint, **kwargs):
        return self.request("PUT", endpoint, **kwargs)

    def patch(self, endpoint, **kwargs):
        return self.request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self.request("DELETE", endpoint, **kwargs)


def response_details(response):
    """Safe diagnostics; callers should never attach auth tokens."""
    try:
        body = response.text
    except Exception:
        body = "<response body unavailable>"
    return (
        f"Request: {response.request.method} {response.url}\n"
        f"Request body: {response.request.body}\n"
        f"Response status: {response.status_code}\n"
        f"Response body: {body}"
    )
