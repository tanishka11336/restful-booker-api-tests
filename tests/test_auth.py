import pytest
from jsonschema import validate

from utils.schemas import TOKEN_SCHEMA


@pytest.mark.smoke
def test_health_check(client):
    response = client.health_check()
    assert response.status_code == 201  # Restful-Booker returns 201 "Created" for /ping


@pytest.mark.smoke
def test_create_token_with_valid_credentials(client):
    response = client.create_token("admin", "password123")
    assert response.status_code == 200
    validate(response.json(), TOKEN_SCHEMA)


@pytest.mark.negative
@pytest.mark.parametrize(
    "username, password",
    [("admin", "wrong"), ("wrong", "password123"), ("", ""), ("admin", "")],
    ids=["wrong_password", "wrong_username", "both_empty", "empty_password"],
)
def test_create_token_with_invalid_credentials(client, username, password):
    response = client.create_token(username, password)
    # The API answers 200 but with a failure reason and no token.
    assert response.status_code == 200
    body = response.json()
    assert "token" not in body
    assert body.get("reason") == "Bad credentials"
