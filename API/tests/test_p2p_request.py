from fastapi.testclient import TestClient
from httpx import Response

from core.main import app
from core.config import get_settings
from core import schemas
from sql.crud import UserCrud, ScopeCrud, UserToScopeCrud, P2PRequestCrud
from sql.database import get_db_not_dependency
from _testing_utils import UserAccessCookie, get_new_discord_id


SETTINGS = get_settings()

client = TestClient(app)


db = get_db_not_dependency()

for scope_name in SETTINGS.OAUTH2_SCHEME_SCOPES:
    ScopeCrud(db).create(schemas.ScopeCreate(name=scope_name))

test_p2p_user_create_schema = schemas.UserCreate(
    username='p2p_user', password='p2p_password', discord_id=next(get_new_discord_id)
)

test_p2p_user = UserCrud(db).create(test_p2p_user_create_schema)

all_scopes = ScopeCrud(db).get_many()

test_user_scope = all_scopes[2]

UserToScopeCrud(db).create(schemas.UserToScopeCreate(user_id=test_p2p_user.id, scope_id=test_user_scope.id))

test_p2p_request_create_schema = schemas.P2PRequestCreate(
    repository_link='https://test-link', comment='test comment', creator_id=test_p2p_user.id
)

test_p2p_request = P2PRequestCrud(db).create(test_p2p_request_create_schema)


class TestCreateP2PRequestRoute:

    @staticmethod
    def do_request(*args, **kwargs) -> Response:
        return client.post('/p2p_request/create', *args, **kwargs)

    def test_not_authorized(self):

        response = self.do_request()

        assert response.status_code == 401

    def test_incorrect_scope(self):

        response = self.do_request(data={
            'username': test_p2p_user.username,
            'password': test_p2p_user_create_schema.password,
            'scope': 'incorrect_scope',
        })

        assert response.status_code == 401

    def test_user_does_not_have_scope(self):

        users_before_request = len(UserCrud(db).get_many())

        with UserAccessCookie(client, test_p2p_user.username, ''):
            response = self.do_request(params={
                'username': 'test_incorrect_scope_user',
                'password': 'test_incorrect_scope_user',
                'discord_id': next(get_new_discord_id),
            })

        assert response.status_code == 401

        assert users_before_request == len(UserCrud(db).get_many())


class TestP2PRequestReview:

    @staticmethod
    def do_request(*args, **kwargs) -> Response:
        return client.get('/p2p_request/review', *args, **kwargs)

    def test_not_authorized(self):

        response = self.do_request()

        assert response.status_code == 401

    def test_user_does_not_have_scope(self):

        users_before_request = len(UserCrud(db).get_many())

        with UserAccessCookie(client, test_p2p_user.username, ''):
            response = self.do_request(params={
                'username': 'test_incorrect_scope_user',
                'password': 'test_incorrect_scope_user',
                'discord_id': next(get_new_discord_id),
            })

        assert response.status_code == 401

        assert users_before_request == len(UserCrud(db).get_many())
