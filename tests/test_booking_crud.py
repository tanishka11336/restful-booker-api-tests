import pytest
from jsonschema import validate

from utils.data_reader import load_json
from utils.schemas import BOOKING_ID_LIST_SCHEMA, BOOKING_SCHEMA, CREATE_BOOKING_SCHEMA

VALID_BOOKINGS = load_json("bookings.json")["valid_bookings"]


def strip_id(case: dict) -> dict:
    return {k: v for k, v in case.items() if k != "id"}


@pytest.mark.smoke
def test_get_all_booking_ids(client):
    response = client.get_booking_ids()
    assert response.status_code == 200
    validate(response.json(), BOOKING_ID_LIST_SCHEMA)
    assert len(response.json()) > 0


@pytest.mark.regression
@pytest.mark.parametrize("case", VALID_BOOKINGS, ids=[c["id"] for c in VALID_BOOKINGS])
def test_create_booking_data_driven(client, token, case):
    payload = strip_id(case)
    response = client.create_booking(payload)
    assert response.status_code == 200

    body = response.json()
    validate(body, CREATE_BOOKING_SCHEMA)
    assert body["booking"] == payload

    client.delete_booking(body["bookingid"], token)  # clean up


@pytest.mark.smoke
def test_get_booking_by_id(client, created_booking):
    response = client.get_booking(created_booking["id"])
    assert response.status_code == 200
    validate(response.json(), BOOKING_SCHEMA)
    assert response.json() == created_booking["payload"]


@pytest.mark.regression
def test_created_booking_appears_in_booking_list(client, created_booking):
    response = client.get_booking_ids()
    ids = [item["bookingid"] for item in response.json()]
    assert created_booking["id"] in ids


@pytest.mark.regression
def test_filter_bookings_by_name(client, created_booking):
    payload = created_booking["payload"]
    response = client.get_booking_ids(firstname=payload["firstname"], lastname=payload["lastname"])
    assert response.status_code == 200
    ids = [item["bookingid"] for item in response.json()]
    assert created_booking["id"] in ids


@pytest.mark.regression
def test_full_update_booking(client, token, created_booking):
    updated = dict(created_booking["payload"], firstname="Updated", totalprice=999,
                   depositpaid=False, additionalneeds="Dinner")
    response = client.update_booking(created_booking["id"], updated, token)
    assert response.status_code == 200
    assert response.json() == updated

    # Verify persistence with a separate GET
    assert client.get_booking(created_booking["id"]).json() == updated


@pytest.mark.regression
def test_partial_update_booking_changes_only_given_fields(client, token, created_booking):
    response = client.partial_update_booking(
        created_booking["id"], {"firstname": "Patched", "lastname": "User"}, token)
    assert response.status_code == 200

    body = response.json()
    assert body["firstname"] == "Patched"
    assert body["lastname"] == "User"
    # untouched fields must be unchanged
    assert body["totalprice"] == created_booking["payload"]["totalprice"]
    assert body["bookingdates"] == created_booking["payload"]["bookingdates"]


@pytest.mark.regression
def test_delete_booking(client, token, booking_payload):
    booking_id = client.create_booking(booking_payload).json()["bookingid"]

    delete_response = client.delete_booking(booking_id, token)
    assert delete_response.status_code == 201  # Restful-Booker returns 201 for DELETE

    assert client.get_booking(booking_id).status_code == 404
