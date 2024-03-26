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

test_reviewer_create_schema = schemas.UserCreate(
    username='reviewer', password='reviewer_password', discord_id=next(get_new_discord_id)
)

test_reviewer = UserCrud(db).create(test_reviewer_create_schema)

all_scopes = ScopeCrud(db).get_many()

test_user_scope = all_scopes[2]

UserToScopeCrud(db).create(schemas.UserToScopeCreate(user_id=test_p2p_user.id, scope_id=test_user_scope.id))

UserToScopeCrud(db).create(schemas.UserToScopeCreate(user_id=test_reviewer.id, scope_id=test_user_scope.id))

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

        with UserAccessCookie(client, test_p2p_user.username, 'me'):
            response = self.do_request()

        assert response.status_code == 401

    def test_user_does_not_have_scope(self):

        user_crud = UserCrud(db)

        users_before_request = len(user_crud.get_many())

        with UserAccessCookie(client, test_p2p_user.username, ''):
            response = self.do_request(params={
                'username': test_p2p_user.username,
                'password': test_p2p_user_create_schema.password,
                'discord_id': next(get_new_discord_id),
            })

        assert response.status_code == 401

        assert users_before_request == len(user_crud.get_many())

    def test_correct(self):

        with UserAccessCookie(client, test_p2p_user.username, 'p2p_request'):
            response = self.do_request(params={
                'repository_link': test_p2p_request.repository_link,
                'comment': test_p2p_request.comment
            })

        assert response.status_code == 200
        assert response.json() is True


class TestP2PRequestReview:

    @staticmethod
    def do_request(*args, **kwargs) -> Response:
        return client.get('/p2p_request/review', *args, **kwargs)

    def test_not_authorized(self):

        response = self.do_request()

        assert response.status_code == 401

    def test_user_does_not_have_scope(self):

        user_crud = UserCrud(db)

        users_before_request = len(user_crud.get_many())

        with UserAccessCookie(client, test_p2p_user.username, ''):
            response = self.do_request(params={
                'username': test_p2p_user.username,
                'password': test_p2p_user_create_schema.password,
                'discord_id': next(get_new_discord_id),
            })

        assert response.status_code == 401

        assert users_before_request == len(user_crud.get_many())

    def test_user_gets_his_own_project(self):

        with UserAccessCookie(client, test_p2p_user.username, 'p2p_request'):
            response = self.do_request()

        assert response.status_code == 200

        assert response.json() == {'context': 'There are not any pending projects'}

    def test_correct(self):

        with UserAccessCookie(client, test_reviewer.username, 'p2p_request'):
            response = self.do_request()

        assert response.status_code == 200

        oldest_project = P2PRequestCrud(db).start_review(test_reviewer.id)

        p2p_request_schema = schemas.P2PRequest.model_validate(test_p2p_request)

        assert p2p_request_schema.model_dump()['review_state'] != response.json()['review_state']

        assert schemas.P2PRequest.model_validate(oldest_project).id == response.json()['id'] + 1

    def test_user_already_have_review(self):

        with UserAccessCookie(client, test_reviewer.username, 'p2p_request'):
            response = self.do_request()

        assert response.status_code == 200

        assert response.json() == {'context': 'You already have a review, complete it first'}

    def test_no_pending_projects(self):

        with UserAccessCookie(client, test_p2p_user.username, 'p2p_request'):
            response = self.do_request()

        assert response.status_code == 200

        assert response.json() == {'context': 'There are not any pending projects'}
