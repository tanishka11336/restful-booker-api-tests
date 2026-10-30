import pytest

from utils.data_reader import load_json

INVALID_BOOKINGS = load_json("bookings.json")["invalid_bookings"]


@pytest.mark.negative
def test_get_nonexistent_booking_returns_404(client):
    assert client.get_booking(99999999).status_code == 404


@pytest.mark.negative
@pytest.mark.parametrize("case", INVALID_BOOKINGS, ids=[c["id"] for c in INVALID_BOOKINGS])
def test_create_booking_with_missing_fields_is_rejected(client, case):
    response = client.create_booking(case["payload"])
    # Restful-Booker answers 500 for malformed bodies; any 4xx/5xx proves it was rejected.
    assert response.status_code >= 400


@pytest.mark.negative
def test_update_without_token_is_forbidden(client, created_booking):
    response = client.update_booking(created_booking["id"], created_booking["payload"], token=None)
    assert response.status_code == 403


@pytest.mark.negative
def test_update_with_invalid_token_is_forbidden(client, created_booking):
    response = client.update_booking(created_booking["id"], created_booking["payload"], token="invalid")
    assert response.status_code == 403


@pytest.mark.negative
def test_delete_without_token_is_forbidden(client, created_booking):
    assert client.delete_booking(created_booking["id"], token=None).status_code == 403
    # booking must still exist
    assert client.get_booking(created_booking["id"]).status_code == 200


@pytest.mark.regression
def test_response_time_is_acceptable(client):
    response = client.get_booking_ids()
    assert response.elapsed.total_seconds() < 5
