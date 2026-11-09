"""Environment configuration for the Restful Booker test suite."""
import os

BASE_URL = os.getenv("BASE_URL", "https://restful-booker.herokuapp.com").rstrip("/")
USERNAME = os.getenv("API_USERNAME", "admin")
PASSWORD = os.getenv("API_PASSWORD", "password123")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "15"))
