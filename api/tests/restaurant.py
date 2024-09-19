import os
from fastapi.testclient import TestClient

from api.dependencies.state import get_state
from api.state import State
from api import app

import jwt


def test_restaurant(state_fixture: State):
    app.dependency_overrides[get_state] = lambda: state_fixture
    test_client = TestClient(app)

    response = test_client.post(
        "/merchants/register",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "email": "test@gmail.com",
            "password": "password",
        },
    )

    assert response.status_code == 200

    merchant_id = jwt.decode(  # type:ignore
        response.json()["jwt_token"],
        state_fixture.jwt_secret,
        algorithms=["HS256"],
    )["merchant_id"]
    merchant_token = response.json()["jwt_token"]

    response = test_client.post(
        "/restaurants",
        json={
            "name": "Test Restaurant",
            "address": "123 Test St",
            "location": {
                "lat": 123,
                "lng": 123,
            },
        },
        headers={"Authorization": f"Bearer {merchant_token}"},
    )

    restaurant_id: int = response.json()
    assert response.status_code == 200

    # test restaurant conflicting
    failed_respone = test_client.post(
        "/restaurants",
        json={
            "name": "Test Restaurant",
            "address": "456 Test St",
            "location": {
                "lat": 456,
                "lng": 456,
            },
        },
        headers={"Authorization": f"Bearer {merchant_token}"},
    )

    assert failed_respone.status_code == 409

    response = test_client.get(
        f"/restaurants/{response.json()}",
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Test Restaurant"
    assert response.json()["address"] == "123 Test St"
    assert response.json()["location"] == {
        "lat": 123,
        "lng": 123,
    }
    assert response.json()["merchant_id"] == merchant_id
    assert response.json()["id"] == restaurant_id

    file_path = os.path.join(os.getcwd(), "api", "tests", "assets", "test.jpg")

    # image should be not found
    failed_response = test_client.get(
        f"/restaurants/{restaurant_id}/image",
    )

    assert failed_response.status_code == 404

    with open(file_path, "rb") as file:
        # test restaurant image upload
        response = test_client.put(
            f"/restaurants/{restaurant_id}/image",
            files={"image": file},
            headers={"Authorization": f"Bearer {merchant_token}"},
        )

        assert response.status_code == 200

        # test restaurant image retrieval
        response = test_client.get(
            f"/restaurants/{restaurant_id}/image",
        )

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "image/jpeg"

        with open(file_path, "rb") as file:
            assert response.content == file.read()

    # test uploading a non-image file
    file_path = os.path.join(os.getcwd(), "api", "tests", "assets", "test.txt")

    with open(file_path, "rb") as file:
        response = test_client.put(
            f"/restaurants/{restaurant_id}/image",
            files={"image": file},
            headers={"Authorization": f"Bearer {merchant_token}"},
        )

        assert response.status_code == 400

    # creates a new merchant and try to upload an image to the restaurant
    # that the merchant does not own
    response = test_client.post(
        "/merchants/register",
        json={
            "first_name": "James",
            "last_name": "Smith",
            "username": "james",
            "email": "james@gmail.com",
            "password": "password",
        },
    )

    assert response.status_code == 200

    merchant_id = jwt.decode(  # type:ignore
        response.json()["jwt_token"],
        state_fixture.jwt_secret,
        algorithms=["HS256"],
    )["merchant_id"]
    merchant_token = response.json()["jwt_token"]

    file_path = os.path.join(os.getcwd(), "api", "tests", "assets", "test.jpg")

    with open(file_path, "rb") as file:
        response = test_client.put(
            f"/restaurants/{restaurant_id}/image",
            files={"image": file},
            headers={"Authorization": f"Bearer {merchant_token}"},
        )

        assert response.status_code == 403
