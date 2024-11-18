import os
from typing import Any
from fastapi.testclient import TestClient

from api.configuration import Configuration
from api.dependencies.configuration import get_configuration
from api import app

import jwt


def test_restaurant(configuration_fixture: Configuration):
    app.dependency_overrides[get_configuration] = lambda: configuration_fixture
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
        configuration_fixture.jwt_secret,
        algorithms=["HS256"],
    )["merchant_id"]
    merchant_token = response.json()["jwt_token"]

    response = test_client.post(
        "/canteens/add_canteen",
        json={
            "name": "Test Canteen",
            "address": "123 Test St",
            "latitude": 123,
            "longitude": 123,
        },
        headers={"Authorization": f"Bearer {merchant_token}"},
    )

    assert response.status_code == 200
    canteen_id = response.json()["id"]

    response = test_client.post(
        "/restaurants",
        json={
            "name": "Test Restaurant",
            "address": "123 Test St",
            "canteen_id": canteen_id,
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
    failed_response = test_client.post(
        "/restaurants",
        json={
            "name": "Test Restaurant",
            "address": "456 Test St",
            "canteen_id": canteen_id,
            "location": {
                "lat": 456,
                "lng": 456,
            },
        },
        headers={"Authorization": f"Bearer {merchant_token}"},
    )

    assert failed_response.status_code == 409

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
    assert not response.json()["open"]

    file_path = os.path.join(os.getcwd(), "api", "tests", "assets", "test.jpg")

    # image should be not found
    failed_response = test_client.get(
        f"/restaurants/{restaurant_id}/image",
    )

    assert failed_response.status_code == 204

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

    unauthorized_merchant_token = response.json()["jwt_token"]

    file_path = os.path.join(os.getcwd(), "api", "tests", "assets", "test.jpg")

    with open(file_path, "rb") as file:
        response = test_client.put(
            f"/restaurants/{restaurant_id}/image",
            files={"image": file},
            headers={"Authorization": f"Bearer {unauthorized_merchant_token}"},
        )

        assert response.status_code == 403

    response = test_client.post(
        f"/restaurants/{restaurant_id}/menus",
        json={
            "name": "Steak",
            "description": "A juicy steak",
            "price": 300.0,
            "estimated_prep_time": 30,
        },
        headers={"Authorization": f"Bearer {merchant_token}"},
    )

    assert response.status_code == 200

    menu_id: int = response.json()

    # test menu conflicting
    failed_response = test_client.post(
        f"/restaurants/{restaurant_id}/menus",
        json={
            "name": "Steak",
            "description": "A less juicy steak",
            "price": 150.0,
            "estimated_prep_time": 15,
        },
        headers={"Authorization": f"Bearer {merchant_token}"},
    )

    assert failed_response.status_code == 409

    # test unauthorized merchant
    failed_response = test_client.post(
        f"/restaurants/{restaurant_id}/menus",
        json={
            "name": "Steak",
            "description": "A less juicy steak",
            "price": 150.0,
            "estimated_prep_time": 15,
        },
        headers={"Authorization": f"Bearer {unauthorized_merchant_token}"},
    )

    assert failed_response.status_code == 403

    # test get menu
    response = test_client.get(
        f"restaurants/menus/{menu_id}",
    )

    assert response.status_code == 200

    assert response.json()["name"] == "Steak"
    assert response.json()["description"] == "A juicy steak"
    assert response.json()["price"] == "300.00"
    assert response.json()["estimated_prep_time"] == 30
    assert response.json()["id"] == menu_id

    steak_menu_json = response.json()

    response = test_client.get(
        f"restaurants/{restaurant_id}/menus",
    )

    assert response.status_code == 200
    assert response.json() == [steak_menu_json]

    # create a new customization
    customization_json: dict[str, Any] = {
        "title": "Wellness",
        "description": "Choose your wellness",
        "unique": True,
        "required": True,
        "options": [
            {
                "name": "Medium",
                "description": "Medium wellness",
                "extra_price": 0.0,
            },
            {
                "name": "Rare",
                "description": None,
                "extra_price": None,
            },
        ],
    }
    response = test_client.post(
        f"/restaurants/menus/{menu_id}/customizations",
        json=customization_json,
        headers={"Authorization": f"Bearer {merchant_token}"},
    )

    assert response.status_code == 200
    customization_id: int = response.json()

    failed_response = test_client.post(
        f"/restaurants/menus/{menu_id}/customizations",
        json=customization_json,
        headers={"Authorization": f"Bearer {merchant_token}"},
    )

    assert failed_response.status_code == 409

    response = test_client.get(
        f"/restaurants/menus/{menu_id}/customizations",
    )

    assert response.status_code == 200
    assert len(response.json()) == 1

    customization = response.json()[0]

    assert customization["title"] == "Wellness"
    assert customization["description"] == "Choose your wellness"
    assert customization["unique"]
    assert customization["required"]
    assert customization["id"] == customization_id
    assert customization["menu_id"] == menu_id

    assert len(customization["options"]) == 2

    assert customization["options"][0]["name"] == "Medium"
    assert customization["options"][0]["description"] == "Medium wellness"
    assert customization["options"][0]["extra_price"] == "0.00"

    assert customization["options"][1]["name"] == "Rare"
    assert customization["options"][1]["description"] is None
    assert customization["options"][1]["extra_price"] is None

    faulty_options: dict[str, Any] = {
        "title": "Sauce",
        "description": "Choose your sauce",
        "unique": False,
        "required": False,
        "options": [
            {
                "name": "Barbecue",
                "description": "Barbecue sauce",
                "extra_price": 0.0,
            },
            {
                "name": "Barbecue",
                "description": "Barbecue sauce",
                "extra_price": 0.0,
            },
        ],
    }

    failed_response = test_client.post(
        f"/restaurants/menus/{menu_id}/customizations",
        json=faulty_options,
        headers={"Authorization": f"Bearer {merchant_token}"},
    )

    assert failed_response.status_code == 409

    sauce_options: dict[str, Any] = {
        "title": "Sauce",
        "description": "Choose your sauce",
        "unique": False,
        "required": False,
        "options": [
            {
                "name": "Barbecue",
                "description": "Barbecue sauce",
                "extra_price": 0.0,
            },
            {
                "name": "Ketchup",
                "description": "Ketchup sauce",
                "extra_price": 0.0,
            },
        ],
    }

    # unauthorized merchant
    failed_response = test_client.post(
        f"/restaurants/menus/{menu_id}/customizations",
        json=sauce_options,
        headers={"Authorization": f"Bearer {unauthorized_merchant_token}"},
    )

    assert failed_response.status_code == 403

    # open restaurant
    response = test_client.put(
        f"/restaurants/{restaurant_id}/open",
        headers={"Authorization": f"Bearer {merchant_token}"},
    )

    assert response.status_code == 200

    response = test_client.get(
        f"/restaurants/{restaurant_id}",
    )

    assert response.status_code == 200
    assert response.json()["open"]

    # close restaurant
    response = test_client.put(
        f"/restaurants/{restaurant_id}/close",
        headers={"Authorization": f"Bearer {merchant_token}"},
    )

    assert response.status_code == 200

    # test unauthorized merchant
    failed_response = test_client.put(
        f"/restaurants/{restaurant_id}/open",
        headers={"Authorization": f"Bearer{unauthorized_merchant_token}"},
    )

    assert failed_response.status_code == 403

    response = test_client.get(
        f"/restaurants/{restaurant_id}",
    )

    assert response.status_code == 200
    assert not response.json()["open"]
