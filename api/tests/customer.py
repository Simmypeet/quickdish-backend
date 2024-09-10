from fastapi.testclient import TestClient
from api import app, get_state

from api.models.customer import Customer
from api.tests import override_get_state

import jwt


class TestCustomer:
    __test_client: TestClient

    def setup_class(self):
        app.dependency_overrides[get_state] = override_get_state

        self.__test_client = TestClient(app)

    def teardown_class(self):
        app.dependency_overrides = {}
        override_get_state().session.flush()
        override_get_state().session.close()

    def test_create_customer(self):
        response = self.__test_client.post(
            "/customers/",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "email": "test@gmail.com",
                "password": "password",
            },
        )

        assert response.status_code == 200
        decoded_id = jwt.decode(  # type:ignore
            response.json()["jwt_token"],
            override_get_state().jwt_secret,
            algorithms=["HS256"],
        )["customer_id"]

        result = (
            override_get_state()
            .session.query(Customer)
            .filter_by(id=decoded_id)
            .first()
        )

        assert result is not None

        assert result.first_name == "John"  # type:ignore
        assert result.last_name == "Doe"  # type:ignore
        assert result.username == "johndoe"  # type:ignore
        assert result.email == "test@gmail.com"  # type:ignore
        assert result.id == decoded_id  # type:ignore

        failed_response = self.__test_client.post(
            "/customers/",
            json={
                "first_name": "Jane",
                "last_name": "Doe",
                "username": "johndoe",
                "email": "test@gmail.com",
                "password": "password",
            },
        )

        assert failed_response.status_code == 409
        assert failed_response.json() == {
            "error": "an account with the same username or email already exists"
        }
