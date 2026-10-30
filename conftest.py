import pytest

from utils.api_client import BookerClient
from utils.data_reader import load_json


def pytest_addoption(parser):
    parser.addoption("--base-url", action="store", default="https://restful-booker.herokuapp.com",
                     help="API base URL")
    parser.addoption("--username", action="store", default="admin", help="Auth username")
    parser.addoption("--password", action="store", default="password123", help="Auth password")


@pytest.fixture(scope="session")
def client(request) -> BookerClient:
    return BookerClient(request.config.getoption("--base-url"))


@pytest.fixture(scope="session")
def token(client, request) -> str:
    """Auth token shared by the whole session (one login, many tests)."""
    response = client.create_token(request.config.getoption("--username"),
                                   request.config.getoption("--password"))
    assert response.status_code == 200
    value = response.json().get("token")
    assert value, f"No token returned: {response.text}"
    return value


@pytest.fixture
def booking_payload() -> dict:
    """A known-good booking body (copy, so tests can modify it safely)."""
    data = dict(load_json("bookings.json")["valid_bookings"][0])
    data.pop("id")
    return data


@pytest.fixture
def created_booking(client, token, booking_payload):
    """Create a booking for the test, then delete it afterwards (clean test data)."""
    response = client.create_booking(booking_payload)
    assert response.status_code == 200, response.text
    booking_id = response.json()["bookingid"]
    yield {"id": booking_id, "payload": booking_payload}
    client.delete_booking(booking_id, token)
