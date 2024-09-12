"""
from fastapi.testclient import TestClient
from api.dependency.state import get_state
from api import app
from api.models.merchant import Restaurant
from api.schemas.point import Point
from api.tests import override_get_state

import jwt


class TestRestaurnt:
    __test_client: TestClient

    __merchant_id: int
    __merchant_token: str

    def setup_class(self):
        app.dependency_overrides[get_state] = override_get_state

        test_client = TestClient(app)

        response = test_client.post(
            "/merchant/register",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "email": "test@gmail.com",
                "password": "password",
            },
        )

        print(response)
        assert response.status_code == 200

        self.__merchant_id = jwt.decode(  # type:ignore
            response.json()["jwt_token"],
            override_get_state().jwt_secret,
            algorithms=["HS256"],
        )["merchant_id"] self.__merchant_token = response.json()["jwt_token"]

    def teardown_class(self):
        app.dependency_overrides = {}
        override_get_state().session.flush()
        override_get_state().session.close()

    def test_create_restaurant(self):
"""

from fastapi.testclient import TestClient

from api.dependencies.state import get_state
from api.models.restaurant import Restaurant
from api.schemas.point import Point
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

    print(response)
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

    assert response.status_code == 200

    result = (
        state_fixture.session.query(Restaurant)
        .filter_by(id=response.json())
        .first()
    )

    assert result is not None

    assert result.name == "Test Restaurant"  # type:ignore
    assert result.address == "123 Test St"  # type:ignore
    assert result.location == Point(lat=123, lng=123)  # type:ignore
    assert result.merchant_id == merchant_id
