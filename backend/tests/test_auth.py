import os
import tempfile
import pytest
from backend.app import create_app
from backend.extensions import db


@pytest.fixture(scope="module")
def test_client():
    os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def test_register_and_login(test_client):
    register_payload = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "SecurePassword123",
        "role": "User",
    }
    response = test_client.post(
        "/api/auth/register",
        json=register_payload,
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["user"]["username"] == "testuser"

    login_payload = {
        "username": "testuser",
        "password": "SecurePassword123",
    }
    login_response = test_client.post(
        "/api/auth/login",
        json=login_payload,
    )
    assert login_response.status_code == 200
    token_data = login_response.get_json()
    assert "access_token" in token_data


def test_login_with_invalid_password(test_client):
    login_payload = {
        "username": "testuser",
        "password": "WrongPassword",
    }
    response = test_client.post(
        "/api/auth/login",
        json=login_payload,
    )
    assert response.status_code == 401
