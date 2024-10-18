from copy import deepcopy
from typing import Any
from fastapi.testclient import TestClient
from api.configuration import Configuration
from api.dependencies.configuration import get_configuration
from api import app

import jwt


def test_order(configuration_fixture: Configuration):
    app.dependency_overrides[get_configuration] = lambda: configuration_fixture
    test_client = TestClient(app)

    # create a customer
    first_customer_register_response = test_client.post(
        "/customers/register",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "email": "johndoe@test.com",
            "password": "password",
        },
    )

    assert first_customer_register_response.status_code == 200

    first_customer_jwt: str = first_customer_register_response.json()[
        "jwt_token"
    ]
    first_customer_id = jwt.decode(  # type: ignore
        first_customer_register_response.json()["jwt_token"],
        configuration_fixture.jwt_secret,
        algorithms=["HS256"],
    )["customer_id"]

    second_customer_register_response = test_client.post(
        "/customers/register",
        json={
            "first_name": "Jake",
            "last_name": "Doe",
            "username": "jakedoe",
            "email": "jakedoe@test.com",
            "password": "password",
        },
    )

    assert second_customer_register_response.status_code == 200

    second_customer_jwt: str = second_customer_register_response.json()[
        "jwt_token"
    ]
    _second_customer_id = jwt.decode(  # type: ignore
        second_customer_register_response.json()["jwt_token"],
        configuration_fixture.jwt_secret,
        algorithms=["HS256"],
    )["customer_id"]

    # create a merchant
    first_merchant_register_response = test_client.post(
        "/merchants/register",
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "username": "janedoe",
            "email": "janedoe@test.com",
            "password": "password",
        },
    )

    assert first_merchant_register_response.status_code == 200

    first_merchant_jwt: str = first_merchant_register_response.json()[
        "jwt_token"
    ]

    _first_merchant_id = jwt.decode(  # type: ignore
        first_merchant_register_response.json()["jwt_token"],
        configuration_fixture.jwt_secret,
        algorithms=["HS256"],
    )["merchant_id"]

    second_merchant_register_response = test_client.post(
        "/merchants/register",
        json={
            "first_name": "Jack",
            "last_name": "Doe",
            "username": "jackdoe",
            "email": "jackdoe@test.com",
            "password": "password",
        },
    )

    assert second_merchant_register_response.status_code == 200

    second_merchant_jwt: str = second_merchant_register_response.json()[
        "jwt_token"
    ]

    _second_merchant_id = jwt.decode(  # type: ignore
        second_merchant_register_response.json()["jwt_token"],
        configuration_fixture.jwt_secret,
        algorithms=["HS256"],
    )["merchant_id"]

    # create a steak restaurant
    steak_restaurant_create_response = test_client.post(
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
            "Authorization": f"Bearer {first_merchant_register_response.json()['jwt_token']}"
        },
    )

    assert steak_restaurant_create_response.status_code == 200

    steak_restaurant_id: int = steak_restaurant_create_response.json()

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
            "Authorization": f"Bearer {first_merchant_register_response.json()['jwt_token']}"
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
        headers={"Authorization": f"Bearer {first_merchant_jwt}"},
    )

    assert wellness_create_response.status_code == 200

    # create a burger restaurant
    burger_restaurant_create_resoponse = test_client.post(
        "/restaurants/",
        json={
            "name": "Burger House",
            "address": "address",
            "location": {
                "lat": 0,
                "lng": 0,
            },
        },
        headers={"Authorization": f"Bearer {second_merchant_jwt}"},
    )

    assert burger_restaurant_create_resoponse.status_code == 200

    burger_restaurant_id: int = burger_restaurant_create_resoponse.json()

    # create a burger menu
    burger_create_response = test_client.post(
        f"/restaurants/{burger_restaurant_id}/menus",
        json={
            "name": "steak",
            "description": "a juicy steak",
            "price": 10,
            "estimated_prep_time": 10,
        },
        headers={"Authorization": f"Bearer {second_merchant_jwt}"},
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
        headers={"Authorization": f"Bearer {second_merchant_jwt}"},
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

    restaurant_closed_response = test_client.post(
        "/orders/",
        json=steak_order,
        headers={"Authorization": f"Bearer {first_customer_jwt}"},
    )

    assert restaurant_closed_response.status_code == 409
    assert restaurant_closed_response.json() == {
        "detail": {"error": "restaurant is closed"}
    }

    restaurant_open_response = test_client.put(
        f"/restaurants/{steak_restaurant_id}/open",
        headers={"Authorization": f"Bearer {first_merchant_jwt}"},
    )

    assert restaurant_open_response.status_code == 200

    first_order_response = test_client.post(
        "/orders/",
        json=steak_order,
        headers={"Authorization": f"Bearer {first_customer_jwt}"},
    )

    assert first_order_response.status_code == 200

    restaurant_open_response = test_client.put(
        f"/restaurants/{burger_restaurant_id}/open",
        headers={"Authorization": f"Bearer {second_merchant_jwt}"},
    )

    assert restaurant_open_response.status_code == 200

    burger_order: dict[Any, Any] = {
        "restaurant_id": burger_restaurant_id,
        "items": [
            {
                "menu_id": burger_id,
                "quantity": 1,
                "extra_requests": "no salt",
                "options": [
                    {"option_id": source["options"][0]["id"]},
                ],
            }
        ],
    }

    second_order_response = test_client.post(
        "/orders/",
        json=burger_order,
        headers={"Authorization": f"Bearer {second_customer_jwt}"},
    )

    assert second_order_response.status_code == 200

    quantity_zero_order: dict[Any, Any] = deepcopy(steak_order)
    quantity_zero_order["items"][0]["quantity"] = 0

    quantity_zero_order_response = test_client.post(
        "/orders/",
        json=quantity_zero_order,
        headers={"Authorization": f"Bearer {first_customer_jwt}"},
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
        headers={"Authorization": f"Bearer {first_customer_jwt}"},
    )

    assert restaurant_mismatched_order_response.status_code == 400

    option_mismatched_order: dict[Any, Any] = deepcopy(steak_order)
    option_mismatched_order["items"][0]["options"].append(
        {"option_id": source["options"][0]["id"]}
    )

    option_mismatched_order_response = test_client.post(
        "/orders/",
        json=option_mismatched_order,
        headers={"Authorization": f"Bearer {first_customer_jwt}"},
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
        headers={"Authorization": f"Bearer {first_customer_jwt}"},
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
        headers={"Authorization": f"Bearer {first_customer_jwt}"},
    )

    assert more_than_one_option_order_response.status_code == 400
    assert more_than_one_option_order_response.json() == {
        "detail": {
            "error": f"menu with id {steak_id} requires customization with id {wellness['id']} to be unique"
        }
    }

    customer_get_orders_response = test_client.get(
        "/orders/",
        headers={"Authorization": f"Bearer {first_customer_jwt}"},
    )

    assert customer_get_orders_response.status_code == 200
    assert len(customer_get_orders_response.json()) == 1
    assert (
        customer_get_orders_response.json()[0]["customer_id"]
        == first_customer_id
    )
    assert (
        customer_get_orders_response.json()[0]["status"]["type"] == "ORDERED"
    )
    assert (
        customer_get_orders_response.json()[0]["restaurant_id"]
        == steak_restaurant_id
    )
    assert (
        customer_get_orders_response.json()[0]["items"][0]["menu_id"]
        == steak_id
    )

    customer_get_orders_response = test_client.get(
        f"/orders/?restaurant_id={burger_restaurant_id}",
        headers={"Authorization": f"Bearer {first_customer_jwt}"},
    )

    assert customer_get_orders_response.status_code == 200
    assert len(customer_get_orders_response.json()) == 0

    customer_get_orders_response = test_client.get(
        "/orders/?status=READY",
        headers={"Authorization": f"Bearer {first_customer_jwt}"},
    )

    assert customer_get_orders_response.status_code == 200
    assert len(customer_get_orders_response.json()) == 0

    customer_get_orders_response = test_client.get(
        f"/orders/?status=ORDERED&restaurant_id={steak_restaurant_id}",
        headers={"Authorization": f"Bearer {first_customer_jwt}"},
    )

    assert customer_get_orders_response.status_code == 200
    assert len(customer_get_orders_response.json()) == 1

    merchant_get_orders_response = test_client.get(
        "/orders/",
        headers={"Authorization": f"Bearer {first_merchant_jwt}"},
    )

    assert merchant_get_orders_response.status_code == 200
    assert len(merchant_get_orders_response.json()) == 1
    assert (
        merchant_get_orders_response.json()[0]["id"]
        == first_order_response.json()
    )

    merchant_get_orders_response = test_client.get(
        "/orders/",
        headers={"Authorization": f"Bearer {second_merchant_jwt}"},
    )

    assert merchant_get_orders_response.status_code == 200
    assert len(merchant_get_orders_response.json()) == 1
    assert (
        merchant_get_orders_response.json()[0]["id"]
        == second_order_response.json()
    )

    second_order_cancel_response = test_client.put(
        f"/orders/{second_order_response.json()}/status",
        json={"type": "CANCELLED", "reason": "i'm full"},
        headers={"Authorization": f"Bearer {second_customer_jwt}"},
    )

    assert second_order_cancel_response.status_code == 200

    get_second_order_status_response = test_client.get(
        f"/orders/{second_order_response.json()}/status",
        headers={"Authorization": f"Bearer {second_customer_jwt}"},
    )

    assert get_second_order_status_response.status_code == 200
    assert get_second_order_status_response.json()["type"] == "CANCELLED"
    assert (
        get_second_order_status_response.json()["cancelled_by"] == "CUSTOMER"
    )
    assert get_second_order_status_response.json()["reason"] == "i'm full"

    twice_cancel_response = test_client.put(
        f"/orders/{second_order_response.json()}/status",
        json={"type": "CANCELLED", "reason": "i'm full"},
        headers={"Authorization": f"Bearer {second_customer_jwt}"},
    )

    assert twice_cancel_response.status_code == 400
    assert twice_cancel_response.json() == {
        "detail": {"error": "order can't be cancelled anymore"}
    }

    preparing_order_response = test_client.put(
        f"/orders/{first_order_response.json()}/status",
        json={"type": "PREPARING"},
        headers={"Authorization": f"Bearer {first_merchant_jwt}"},
    )

    assert preparing_order_response.status_code == 200

    get_preparing_order_status_response = test_client.get(
        f"/orders/{first_order_response.json()}/status",
        headers={"Authorization": f"Bearer {first_merchant_jwt}"},
    )

    assert get_preparing_order_status_response.status_code == 200
    assert get_preparing_order_status_response.json()["type"] == "PREPARING"

    ready_order_response = test_client.put(
        f"/orders/{first_order_response.json()}/status",
        json={"type": "READY"},
        headers={"Authorization": f"Bearer {first_merchant_jwt}"},
    )

    assert ready_order_response.status_code == 200

    get_ready_order_status_response = test_client.get(
        f"/orders/{first_order_response.json()}/status",
        headers={"Authorization": f"Bearer {first_merchant_jwt}"},
    )

    assert get_ready_order_status_response.status_code == 200

    assert get_ready_order_status_response.json()["type"] == "READY"

    merchant_settle_order_response = test_client.put(
        f"/orders/{first_order_response.json()}/status",
        json={"type": "SETTLED"},
        headers={"Authorization": f"Bearer {first_merchant_jwt}"},
    )

    assert merchant_settle_order_response.status_code == 400
    assert merchant_settle_order_response.json() == {
        "detail": {"error": "order can't be settled by merchant"}
    }

    customer_settle_order_response = test_client.put(
        f"/orders/{first_order_response.json()}/status",
        json={"type": "SETTLED"},
        headers={"Authorization": f"Bearer {first_customer_jwt}"},
    )

    assert customer_settle_order_response.status_code == 200

    get_settled_order_status_response = test_client.get(
        f"/orders/{first_order_response.json()}/status",
        headers={"Authorization": f"Bearer {first_customer_jwt}"},
    )

    assert get_settled_order_status_response.status_code == 200
    assert get_settled_order_status_response.json()["type"] == "SETTLED"

    first_order_response = test_client.post(
        "/orders/",
        json=steak_order,
        headers={"Authorization": f"Bearer {first_customer_jwt}"},
    )

    assert first_order_response.status_code == 200

    merchant_cancel_order_response = test_client.put(
        f"/orders/{first_order_response.json()}/status",
        json={"type": "CANCELLED", "reason": "out of stock"},
        headers={"Authorization": f"Bearer {first_merchant_jwt}"},
    )

    assert merchant_cancel_order_response.status_code == 200

    get_cancelled_order_status_response = test_client.get(
        f"/orders/{first_order_response.json()}/status",
        headers={"Authorization": f"Bearer {first_merchant_jwt}"},
    )

    assert get_cancelled_order_status_response.status_code == 200
    assert get_cancelled_order_status_response.json()["type"] == "CANCELLED"
    assert (
        get_cancelled_order_status_response.json()["cancelled_by"]
        == "MERCHANT"
    )
    assert (
        get_cancelled_order_status_response.json()["reason"] == "out of stock"
    )

    _: int = test_client.post(
        "/orders/",
        json=steak_order,
        headers={"Authorization": f"Bearer {first_customer_jwt}"},
    ).json()
    _: int = test_client.post(
        "/orders/",
        json=steak_order,
        headers={"Authorization": f"Bearer {first_customer_jwt}"},
    ).json()
    third_order_id: int = test_client.post(
        "/orders/",
        json=steak_order,
        headers={"Authorization": f"Bearer {first_customer_jwt}"},
    ).json()

    third_order_queue = test_client.get(
        f"/orders/{third_order_id}/queues",
        headers={"Authorization": f"Bearer {first_customer_jwt}"},
    )

    assert third_order_queue.status_code == 200

    assert third_order_queue.json()["queue_count"] == 2
    assert third_order_queue.json()["estimated_time"] == 20

    restaurant_queue = test_client.get(
        f"/orders/queues/?restaurant_id={steak_restaurant_id}",
    )

    assert restaurant_queue.status_code == 200

    assert restaurant_queue.json()["queue_count"] == 3
    assert restaurant_queue.json()["estimated_time"] == 30
