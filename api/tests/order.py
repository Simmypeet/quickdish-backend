from copy import deepcopy
from typing import Any
from fastapi.testclient import TestClient
from api.dependencies.state import get_state
from api.state import State
from api import app

import jwt


def test_order(state_fixture: State):
    app.dependency_overrides[get_state] = lambda: state_fixture
    test_client = TestClient(app)

    # create a customer
    customer_register_response = test_client.post(
        "/customers/register",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "email": "johndoe@test.com",
            "password": "password",
        },
    )

    assert customer_register_response.status_code == 200

    customer_jwt: str = customer_register_response.json()["jwt_token"]
    _ = jwt.decode(  # type: ignore
        customer_register_response.json()["jwt_token"],
        state_fixture.jwt_secret,
        algorithms=["HS256"],
    )["customer_id"]

    # create a merchant
    merchant_register_response = test_client.post(
        "/merchants/register",
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "username": "janedoe",
            "email": "janedoe@test.com",
            "password": "password",
        },
    )

    assert merchant_register_response.status_code == 200

    _: str = merchant_register_response.json()["jwt_token"]
    _ = jwt.decode(  # type: ignore
        merchant_register_response.json()["jwt_token"],
        state_fixture.jwt_secret,
        algorithms=["HS256"],
    )["merchant_id"]

    # create a steak restaurant
    restaurant_create_response = test_client.post(
        "/restaurants/",
        json={
            "name": "Steak House",
            "address": "address",
            "location": {
                "lat": 0,
                "lng": 0,
            },
        },
        headers={
            "Authorization": f"Bearer {merchant_register_response.json()['jwt_token']}"
        },
    )

    assert restaurant_create_response.status_code == 200

    steak_restaurant_id: int = restaurant_create_response.json()

    # create a steak menu
    steak_create_response = test_client.post(
        f"/restaurants/{steak_restaurant_id}/menus",
        json={
            "name": "steak",
            "description": "a juicy steak",
            "price": 10,
            "estimated_prep_time": 10,
        },
        headers={
            "Authorization": f"Bearer {merchant_register_response.json()['jwt_token']}"
        },
    )

    assert steak_create_response.status_code == 200

    steak_id: int = steak_create_response.json()

    # create a customization for the steak
    wellness_create_response = test_client.post(
        f"/restaurants/menus/{steak_id}/customizations",
        json={
            "title": "Wellness",
            "description": "How would you like your steak?",
            "unique": True,
            "required": True,
            "options": [
                {"name": "Rare", "extra_price": 0.0, "description": None},
                {"name": "Medium", "extra_price": 0.0, "description": None},
                {"name": "Well-Done", "extra_price": 0.0, "description": None},
            ],
        },
        headers={
            "Authorization": f"Bearer {merchant_register_response.json()['jwt_token']}"
        },
    )

    assert wellness_create_response.status_code == 200

    # create a burger restaurant
    restaurant_create_response = test_client.post(
        "/restaurants/",
        json={
            "name": "Burger House",
            "address": "address",
            "location": {
                "lat": 0,
                "lng": 0,
            },
        },
        headers={
            "Authorization": f"Bearer {merchant_register_response.json()['jwt_token']}"
        },
    )

    assert restaurant_create_response.status_code == 200

    burger_restaurant_id: int = restaurant_create_response.json()

    # create a steak menu
    burger_create_response = test_client.post(
        f"/restaurants/{burger_restaurant_id}/menus",
        json={
            "name": "steak",
            "description": "a juicy steak",
            "price": 10,
            "estimated_prep_time": 10,
        },
        headers={
            "Authorization": f"Bearer {merchant_register_response.json()['jwt_token']}"
        },
    )

    assert burger_create_response.status_code == 200

    burger_id: int = burger_create_response.json()

    sauce_create_response = test_client.post(
        f"/restaurants/menus/{burger_id}/customizations",
        json={
            "title": "Sauce",
            "description": "What sauce would you like?",
            "unique": False,
            "required": False,
            "options": [
                {"name": "Ketchup", "extra_price": 0.0, "description": None},
                {"name": "Mustard", "extra_price": 0.0, "description": None},
                {"name": "Mayo", "extra_price": 0.0, "description": None},
            ],
        },
        headers={
            "Authorization": f"Bearer {merchant_register_response.json()['jwt_token']}"
        },
    )

    assert sauce_create_response.status_code == 200

    burger_customiozations = test_client.get(
        f"/restaurants/menus/{burger_id}/customizations",
    )

    assert burger_customiozations.status_code == 200

    source = burger_customiozations.json()[0]

    steak_customizations = test_client.get(
        f"/restaurants/menus/{steak_id}/customizations",
    )

    assert steak_customizations.status_code == 200

    wellness = steak_customizations.json()[0]

    steak_order: dict[Any, Any] = {
        "restaurant_id": steak_restaurant_id,
        "items": [
            {
                "menu_id": steak_id,
                "quantity": 1,
                "extra_requests": "no salt",
                "options": [
                    {"option_id": wellness["options"][0]["id"]},
                ],
            }
        ],
    }

    order_response = test_client.post(
        "/orders/",
        json=steak_order,
        headers={"Authorization": f"Bearer {customer_jwt}"},
    )

    assert order_response.status_code == 200

    quantity_zero_order: dict[Any, Any] = deepcopy(steak_order)
    quantity_zero_order["items"][0]["quantity"] = 0

    quantity_zero_order_response = test_client.post(
        "/orders/",
        json=quantity_zero_order,
        headers={"Authorization": f"Bearer {customer_jwt}"},
    )

    assert quantity_zero_order_response.status_code == 400
    assert quantity_zero_order_response.json() == {
        "detail": {
            "error": f"menu with id {steak_id} must have a quantity of at least 1"
        }
    }

    restaurant_mismatched_order: dict[Any, Any] = {
        "restaurant_id": steak_restaurant_id,
        "items": [
            {
                "menu_id": burger_id,
                "quantity": 1,
                "extra_requests": "no salt",
                "options": [],
            }
        ],
    }

    restaurant_mismatched_order_response = test_client.post(
        "/orders/",
        json=restaurant_mismatched_order,
        headers={"Authorization": f"Bearer {customer_jwt}"},
    )

    assert restaurant_mismatched_order_response.status_code == 400

    option_mismatched_order: dict[Any, Any] = deepcopy(steak_order)
    option_mismatched_order["items"][0]["options"].append(
        {"option_id": source["options"][0]["id"]}
    )

    option_mismatched_order_response = test_client.post(
        "/orders/",
        json=option_mismatched_order,
        headers={"Authorization": f"Bearer {customer_jwt}"},
    )

    assert option_mismatched_order_response.status_code == 400
    assert option_mismatched_order_response.json() == {
        "detail": {
            "error": f"the option with id {source['options'][0]['id']} is not in menu with id {steak_id}"
        }
    }

    missing_option_order: dict[Any, Any] = deepcopy(steak_order)
    missing_option_order["items"][0]["options"] = []

    missing_option_order_response = test_client.post(
        "/orders/",
        json=missing_option_order,
        headers={"Authorization": f"Bearer {customer_jwt}"},
    )

    assert missing_option_order_response.status_code == 400
    assert missing_option_order_response.json() == {
        "detail": {
            "error": f"menu with id {steak_id} requires customization with id {wellness['id']}"
        }
    }

    more_than_one_option_order: dict[Any, Any] = deepcopy(steak_order)
    more_than_one_option_order["items"][0]["options"].append(
        {"option_id": wellness["options"][1]["id"]}
    )

    more_than_one_option_order_response = test_client.post(
        "/orders/",
        json=more_than_one_option_order,
        headers={"Authorization": f"Bearer {customer_jwt}"},
    )

    assert more_than_one_option_order_response.status_code == 400
    assert more_than_one_option_order_response.json() == {
        "detail": {
            "error": f"menu with id {steak_id} requires customization with id {wellness['id']} to be unique"
        }
    }
