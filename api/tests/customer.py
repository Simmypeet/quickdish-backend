from fastapi.testclient import TestClient

from api import app
from api.dependency.state import get_state
from api.models.customer import Customer
from api.tests import override_get_state

import jwt


class TestCustomer:
    __test_client: TestClient

    def __decode_jwt(self, jwt_token: str) -> int:
        return jwt.decode(  # type:ignore
            jwt_token, override_get_state().jwt_secret, algorithms=["HS256"]
        )["customer_id"]

    def setup_class(self):
        app.dependency_overrides[get_state] = override_get_state

        self.__test_client = TestClient(app)

    def teardown_class(self):
        app.dependency_overrides = {}
        override_get_state().session.flush()
        override_get_state().session.close()

    def test_customer_register(self):
        try:
            response = self.__test_client.post(
                "/customer/register",
                json={
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "johndoe",
                    "email": "test@gmail.com",
                    "password": "password",
                },
            )

            assert response.status_code == 200
            decoded_id = self.__decode_jwt(response.json()["jwt_token"])

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
                "/customer/register",
                json={
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "username": "johndoe",
                    "email": "test@gmail.com",
                    "password": "password",
                },
            )

            assert failed_response.status_code == 409

        finally:
            override_get_state().session.query(Customer).delete()

    def test_customer_login(self):
        try:
            register_response = self.__test_client.post(
                "/customer/register",
                json={
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "johndoe",
                    "email": "test@gmail.com",
                    "password": "mypassword",
                },
            )

            assert register_response.status_code == 200

            registered_id = self.__decode_jwt(
                register_response.json()["jwt_token"]
            )

            login_response = self.__test_client.post(
                "/customer/login",
                json={"username": "johndoe", "password": "mypassword"},
            )

            assert login_response.status_code == 200

            logged_in_id = self.__decode_jwt(
                login_response.json()["jwt_token"]
            )

            assert registered_id == logged_in_id

            failed_response = self.__test_client.post(
                "/customer/login",
                json={"username": "johndoe", "password": "wrongpassword"},
            )

            assert failed_response.status_code == 401

            failed_response = self.__test_client.post(
                "/customer/login",
                json={"username": "wrongusername", "password": "mypassword"},
            )

        finally:
            override_get_state().session.query(Customer).delete()

    def test_customer_get(self):
        try:

            register_response = self.__test_client.post(
                "/customer/register",
                json={
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "johndoe",
                    "email": "test@gmail.com",
                    "password": "mypassword",
                },
            )

            assert register_response.status_code == 200

            registered_id = self.__decode_jwt(
                register_response.json()["jwt_token"]
            )

            get_response =  self.__test_client.get("/customer/", headers={
                "Authorization": f"Bearer {register_response.json()["jwt_token"]}"
            })

            assert get_response.status_code == 200
            assert registered_id == get_response.json()["id"]

            failed_response = self.__test_client.get("/customer/", headers={
                "Authorization": "Bearer Invalid"
            })

            assert failed_response.status_code == 401

        finally:
            override_get_state().session.query(Customer).delete()
