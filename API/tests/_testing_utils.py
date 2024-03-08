from typing import Generator

from fastapi.testclient import TestClient

from core.login_manager import login_manager
from sql.database import SessionLocal


class TestClientWithDb(TestClient):
    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

        with SessionLocal() as db:
            self.db = db


class UserAccessCookie:
    """
    Set an access cookie for a user, on exit clear cookies
    """

    def __init__(self, client: TestClient, username: str, scopes: str) -> None:

        self.client = client

        self.client.cookies.set(
            'access-token', login_manager.create_access_token(data={'sub': username, 'scopes': scopes})
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.client.cookies.clear()


def _get_new_discord_id() -> Generator[int, None, None]:

    i = 0

    while True:

        yield i

        i += 1


get_new_discord_id: Generator[int, None, None] = _get_new_discord_id()


def get_field_detail_type(details: list[dict], field_name: str) -> str:
    """
    details example:
    [
        {
            "type": "missing",
            "loc": [
                "body",
                "password"
            ],
            "msg": "Field required",
            "input": null,
            "url": "https://errors.pydantic.dev/2.5/v/missing"
        }, ...
    ]
    return example: "missing"
    """

    for detail in details:
        if detail['loc'][1] == field_name:
            return detail['type']

    return ''
