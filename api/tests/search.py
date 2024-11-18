from fastapi.testclient import TestClient
from api.configuration import Configuration

from api import app
from api.dependencies.configuration import get_configuration


def test_search_restaurnat(configuration_fixture: Configuration):
    app.dependency_overrides[get_configuration] = lambda: configuration_fixture
    test_client = TestClient(app)

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

    restaurant_ids: list[int] = []

    for i in range(20):
        restaurant_register_response = test_client.post(
            "/restaurants",
            json={
                "name": f"Test Restaurant {i}",
                "address": f"{i} Test St",
                "canteen_id": canteen_id,
                "location": {
                    "lat": i,
                    "lng": i,
                },
            },
            headers={"Authorization": f"Bearer {merchant_token}"},
        )

        assert restaurant_register_response.status_code == 200
        restaurant_ids.append(restaurant_register_response.json())

    zero_restaurant_response = test_client.get(
        "/restaurants/search",
        params={"query": "Good", "limit": 10},
    )

    assert zero_restaurant_response.status_code == 200
    assert len(zero_restaurant_response.json()) == 0

    negative_limit_response = test_client.get(
        "/restaurants/search",
        params={"query": "Test", "limit": -1},
    )

    assert negative_limit_response.status_code == 400

    ten_restaurant_response = test_client.get(
        "/restaurants/search",
        params={"query": "Test", "limit": 10},
    )

    assert ten_restaurant_response.status_code == 200
    assert len(ten_restaurant_response.json()) == 10
