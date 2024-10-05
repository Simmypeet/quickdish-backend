from fastapi.testclient import TestClient

from api.dependencies.state import get_state
from api.state import State
from api import app

import jwt


def test_favorites_restaurant(state_fixture: State):
    app.dependency_overrides[get_state] = lambda: state_fixture
    test_client = TestClient(app)

    customer_register_response = test_client.post(
        "/customers/register",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "email": "test@gmail.com",
            "password": "password",
        },
    )

    assert customer_register_response.status_code == 200
    customer_token = customer_register_response.json()["jwt_token"]

    merchant_register_response = test_client.post(
        "/merchants/register",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "email": "test@gmail.com",
            "password": "password",
        },
    )

    assert merchant_register_response.status_code == 200

    merchant_token = merchant_register_response.json()["jwt_token"]

    merchant_register_response = test_client.post(
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

    restaurant_id: int = merchant_register_response.json()
    assert merchant_register_response.status_code == 200

    get_favorites_response = test_client.get(
        "/customers/favorite-restaurants",
        headers={"Authorization": f"Bearer {customer_token}"},
    )

    assert get_favorites_response.status_code == 200
    assert get_favorites_response.json() == []

    duplicating_add_favorites_response = test_client.post(
        "/customers/favorite-restaurants",
        json=[restaurant_id, restaurant_id],
        headers={"Authorization": f"Bearer {customer_token}"},
    )

    assert duplicating_add_favorites_response.status_code == 409
    assert duplicating_add_favorites_response.json() == {
        "detail": {
            "error": f"restaurant id {restaurant_id} is duplicated in the request"
        }
    }

    get_favorites_response = test_client.get(
        "/customers/favorite-restaurants",
        headers={"Authorization": f"Bearer {customer_token}"},
    )

    assert get_favorites_response.status_code == 200
    assert get_favorites_response.json() == []

    add_favorites_response = test_client.post(
        "/customers/favorite-restaurants",
        json=[restaurant_id],
        headers={"Authorization": f"Bearer {customer_token}"},
    )

    assert add_favorites_response.status_code == 200
    assert add_favorites_response.json() == "success"

    not_found_restaurant_response = test_client.post(
        "/customers/favorite-restaurants",
        json=[999],
        headers={"Authorization": f"Bearer {customer_token}"},
    )

    assert not_found_restaurant_response.status_code == 404
    assert not_found_restaurant_response.json() == {
        "detail": {"error": "restaurant id 999 not found"}
    }

    already_added_favorites_response = test_client.post(
        "/customers/favorite-restaurants",
        json=[restaurant_id],
        headers={"Authorization": f"Bearer {customer_token}"},
    )

    assert already_added_favorites_response.status_code == 409
    assert already_added_favorites_response.json() == {
        "detail": {
            "error": "restaurant id 1 already exists in the favorite list"
        }
    }
