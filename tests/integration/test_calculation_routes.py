import uuid

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def register_test_user() -> int:
    """Register a unique user and return the new user ID."""
    unique = uuid.uuid4().hex[:8]

    response = client.post(
        "/users/register",
        json={
            "username": f"calc_user_{unique}",
            "email": f"calc_user_{unique}@example.com",
            "password": "Password123!",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_calculation_bread_routes():
    """
    Test Add, Browse, Read, Edit, and Delete calculation routes.
    """
    user_id = register_test_user()

    # ADD: Create a calculation.
    create_response = client.post(
        "/calculations",
        json={
            "a": 15,
            "b": 5,
            "type": "Add",
            "user_id": user_id,
        },
    )

    assert create_response.status_code == 201

    created = create_response.json()
    calculation_id = created["id"]

    assert created["a"] == 15
    assert created["b"] == 5
    assert created["type"] == "Add"
    assert created["result"] == 20
    assert created["user_id"] == user_id

    # BROWSE: Confirm the calculation appears in the list.
    browse_response = client.get("/calculations")

    assert browse_response.status_code == 200

    calculations = browse_response.json()

    assert any(
        calculation["id"] == calculation_id
        for calculation in calculations
    )

    # READ: Retrieve the calculation by ID.
    read_response = client.get(
        f"/calculations/{calculation_id}"
    )

    assert read_response.status_code == 200

    retrieved = read_response.json()

    assert retrieved["id"] == calculation_id
    assert retrieved["result"] == 20

    # EDIT: Change the operands and calculation type.
    update_response = client.put(
        f"/calculations/{calculation_id}",
        json={
            "a": 20,
            "b": 10,
            "type": "Multiply",
            "user_id": user_id,
        },
    )

    assert update_response.status_code == 200

    updated = update_response.json()

    assert updated["id"] == calculation_id
    assert updated["a"] == 20
    assert updated["b"] == 10
    assert updated["type"] == "Multiply"
    assert updated["result"] == 200

    # DELETE: Remove the calculation.
    delete_response = client.delete(
        f"/calculations/{calculation_id}"
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    # Confirm the deleted record is no longer available.
    missing_response = client.get(
        f"/calculations/{calculation_id}"
    )

    assert missing_response.status_code == 404
    assert missing_response.json()["error"] == (
        "Calculation not found"
    )


def test_create_calculation_with_invalid_type():
    user_id = register_test_user()

    response = client.post(
        "/calculations",
        json={
            "a": 10,
            "b": 5,
            "type": "InvalidOperation",
            "user_id": user_id,
        },
    )

    assert response.status_code == 422
    assert "error" in response.json()


def test_create_calculation_with_division_by_zero():
    user_id = register_test_user()

    response = client.post(
        "/calculations",
        json={
            "a": 10,
            "b": 0,
            "type": "Divide",
            "user_id": user_id,
        },
    )

    assert response.status_code == 422
    assert "Division by zero is not allowed" in (
        response.json()["error"]
    )


def test_create_calculation_with_missing_user():
    response = client.post(
        "/calculations",
        json={
            "a": 10,
            "b": 5,
            "type": "Add",
            "user_id": 999999,
        },
    )

    assert response.status_code == 404
    assert response.json()["error"] == "User not found"


def test_read_missing_calculation():
    response = client.get("/calculations/999999")

    assert response.status_code == 404
    assert response.json()["error"] == (
        "Calculation not found"
    )


def test_update_missing_calculation():
    user_id = register_test_user()

    response = client.put(
        "/calculations/999999",
        json={
            "a": 10,
            "b": 5,
            "type": "Add",
            "user_id": user_id,
        },
    )

    assert response.status_code == 404
    assert response.json()["error"] == (
        "Calculation not found"
    )


def test_delete_missing_calculation():
    response = client.delete("/calculations/999999")

    assert response.status_code == 404
    assert response.json()["error"] == (
        "Calculation not found"
    )