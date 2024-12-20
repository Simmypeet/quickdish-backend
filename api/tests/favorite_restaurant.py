from fastapi.testclient import TestClient

from api.configuration import Configuration
from api.dependencies.configuration import get_configuration
from api import app


def test_favorites_restaurant(configuration_fixture: Configuration):
    app.dependency_overrides[get_configuration] = lambda: configuration_fixture
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

    merchant_register_response = test_client.post(
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

    delete_non_existing_response = test_client.request(
        "DELETE",
        "/customers/favorite-restaurants",
        json=[999],
        headers={"Authorization": f"Bearer {customer_token}"},
    )

    assert delete_non_existing_response.status_code == 404
    assert delete_non_existing_response.json() == {
        "detail": {"error": "restaurant id 999 not found in the favorite list"}
    }

    duplicating_delete_response = test_client.request(
        "DELETE",
        "/customers/favorite-restaurants",
        json=[restaurant_id, restaurant_id],
        headers={"Authorization": f"Bearer {customer_token}"},
    )

    assert duplicating_delete_response.status_code == 409

    delete_response = test_client.request(
        "DELETE",
        "/customers/favorite-restaurants",
        json=[restaurant_id],
        headers={"Authorization": f"Bearer {customer_token}"},
    )

    assert delete_response.status_code == 200
    assert delete_response.json() == "success"

    get_favorites_response = test_client.get(
        "/customers/favorite-restaurants",
        headers={"Authorization": f"Bearer {customer_token}"},
    )

    assert get_favorites_response.status_code == 200
    assert get_favorites_response.json() == []
