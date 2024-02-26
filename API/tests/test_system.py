from fastapi.testclient import TestClient

from core.main import app


BASE_URL = 'http://testserver'

client = TestClient(app, base_url=BASE_URL)


class TestSystem:

    @staticmethod
    def test_rapidoc_route():

        response = client.get('/rapidoc')

        assert response.status_code == 200

    @staticmethod
    def test_unknown_page_handler_route():

        response = client.get('/', follow_redirects=True)

        assert response.status_code == 200
        assert response.url == f'{BASE_URL}/rapidoc'
