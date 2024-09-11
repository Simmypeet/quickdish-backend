from fastapi.testclient import TestClient
from api.dependency.state import get_state
from api import app
from api.tests import override_get_state


class TestRestaurnt:
    __test_client: TestClient

    def setup_class(self):
        app.dependency_overrides[get_state] = override_get_state

        self.__test_client = TestClient(app)

    def teardown_class(self):
        app.dependency_overrides = {}
        override_get_state().session.flush()
        override_get_state().session.close()

    def test_create_restaurant(self):
        pass
