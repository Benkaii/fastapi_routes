import uuid

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def create_unique_user() -> dict[str, str]:
    """Create unique test credentials to prevent duplicate-user conflicts."""
    unique = uuid.uuid4().hex[:8]

    return {
        "username": f"user_{unique}",
        "email": f"user_{unique}@example.com",
        "password": "Password123!",
    }


def test_register_user():
    user_data = create_unique_user()

    response = client.post(
        "/users/register",
        json=user_data,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "created_at" in data

    # Sensitive password information must never be returned.
    assert "password" not in data
    assert "password_hash" not in data


def test_login_user_with_valid_credentials():
    user_data = create_unique_user()

    register_response = client.post(
        "/users/register",
        json=user_data,
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/users/login",
        json={
            "username": user_data["username"],
            "password": user_data["password"],
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "password_hash" not in data


def test_login_user_with_invalid_password():
    user_data = create_unique_user()

    register_response = client.post(
        "/users/register",
        json=user_data,
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/users/login",
        json={
            "username": user_data["username"],
            "password": "WrongPassword123!",
        },
    )

    assert login_response.status_code == 401
    assert login_response.json()["error"] == (
        "Invalid username or password"
    )


def test_duplicate_username():
    user_data = create_unique_user()

    first_response = client.post(
        "/users/register",
        json=user_data,
    )

    assert first_response.status_code == 201

    duplicate_response = client.post(
        "/users/register",
        json={
            "username": user_data["username"],
            "email": f"different_{user_data['email']}",
            "password": "Password123!",
        },
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["error"] == (
        "Username already exists"
    )


def test_read_user():
    user_data = create_unique_user()

    register_response = client.post(
        "/users/register",
        json=user_data,
    )

    assert register_response.status_code == 201

    response = client.get(
        f"/users/{user_data['username']}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]


def test_read_missing_user():
    response = client.get(
        f"/users/missing_{uuid.uuid4().hex}"
    )

    assert response.status_code == 404
    assert response.json()["error"] == "User not found"