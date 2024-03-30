from httpx import Response

from core.main import app
from core.config import get_settings
from core import schemas
from sql.crud import UserCrud, ScopeCrud, UserToScopeCrud
from _testing_utils import TestClientWithDb, UserAccessCookie, get_new_discord_id, get_field_detail_type


SETTINGS = get_settings()

client = TestClientWithDb(app)

for scope_name in SETTINGS.OAUTH2_SCHEME_SCOPES:
    ScopeCrud(client.db).create(schemas.ScopeCreate(name=scope_name))

test_user_1_create_schema = schemas.UserCreate(
    username='username_1', password='password_1', discord_id=next(get_new_discord_id)
)

test_user_1 = UserCrud(client.db).create(test_user_1_create_schema)

all_scopes = ScopeCrud(client.db).get_many()

test_user_scope = all_scopes[0]
not_test_user_scope = all_scopes[1]

UserToScopeCrud(client.db).create(schemas.UserToScopeCreate(user_id=test_user_1.id, scope_id=test_user_scope.id))


class TestLoginRoute:

    @staticmethod
    def do_request(*args, **kwargs) -> Response:
        return client.post(f'/{SETTINGS.TOKEN_URL}', *args, **kwargs)

    def test_empty(self):

        response = self.do_request(data={'username': '', 'password': ''})

        assert response.status_code == 422

        response_details = response.json()['detail']

        assert get_field_detail_type(response_details, 'username') == 'missing'
        assert get_field_detail_type(response_details, 'password') == 'missing'

    def test_incorrect(self):

        response = self.do_request(data={'username': 'test_incorrect_user', 'password': 'test_incorrect_user'})

        assert response.status_code == 401

    def test_incorrect_scope(self):

        response = self.do_request(data={
            'username': test_user_1.username,
            'password': test_user_1_create_schema.password,
            'scope': 'incorrect_scope',
        })

        assert response.status_code == 401

    def test_user_does_not_have_scope(self):

        response = self.do_request(data={
            'username': test_user_1.username,
            'password': test_user_1_create_schema.password,
            'scope': not_test_user_scope.name,
        })

        assert response.status_code == 401

    def test_correct(self):

        response = self.do_request(
            data={'username': test_user_1.username, 'password': test_user_1_create_schema.password},
        )

        client.cookies.clear()

        assert response.status_code == 200
        assert response.json().get('access_token', False)

    def test_correct_with_scope(self):

        response = self.do_request(data={
            'username': test_user_1.username,
            'password': test_user_1_create_schema.password,
            'scope': test_user_scope.name,
        })

        client.cookies.clear()

        assert response.status_code == 200
        assert response.json().get('access_token', False)


class TestGetUserMeDataRoute:

    @staticmethod
    def do_request(*args, **kwargs) -> Response:
        return client.get('/users/me', *args, **kwargs)

    def test_not_authorized(self):

        response = self.do_request()

        assert response.status_code == 401

    def test_user_does_not_have_scope(self):

        with UserAccessCookie(client, test_user_1.username, ''):
            response = self.do_request()

        assert response.status_code == 401

    def test_correct(self):

        with UserAccessCookie(client, test_user_1.username, 'me'):
            response = self.do_request()

        assert response.status_code == 200

        user_schema = schemas.User.model_validate(test_user_1)
        user_schema.available_scopes = UserToScopeCrud(client.db).get_user_scopes(test_user_1)

        assert user_schema.model_dump() == response.json()


class TestCreateUserRoute:

    @staticmethod
    def do_request(*args, **kwargs) -> Response:
        return client.post('/create_user', *args, **kwargs)

    def test_empty(self):

        users_before_request = len(UserCrud(client.db).get_many())

        with UserAccessCookie(client, test_user_1.username, 'register'):
            response = self.do_request()

        assert response.status_code == 422

        response_details = response.json()['detail']

        assert get_field_detail_type(response_details, 'username') == 'missing'
        assert get_field_detail_type(response_details, 'password') == 'missing'
        assert get_field_detail_type(response_details, 'discord_id') == 'missing'

        assert users_before_request == len(UserCrud(client.db).get_many())

    def test_incorrect(self):

        users_before_request = len(UserCrud(client.db).get_many())

        with UserAccessCookie(client, test_user_1.username, 'register'):
            response = self.do_request(
                params={'username': 'test_incorrect_user', 'password': 'test_incorrect_user', 'discord_id': 'not_int'}
            )

        assert response.status_code == 422

        response_details = response.json()['detail']

        assert get_field_detail_type(response_details, 'discord_id') == 'int_parsing'

        assert users_before_request == len(UserCrud(client.db).get_many())

    def test_duplicate_discord_id(self):

        users_before_request = len(UserCrud(client.db).get_many())

        with UserAccessCookie(client, test_user_1.username, 'register'):
            response = self.do_request(params={
                'username': 'test_duplicate_user',
                'password': test_user_1_create_schema.password,
                'discord_id': test_user_1.discord_id,
            })

        assert response.status_code == 400

        assert users_before_request == len(UserCrud(client.db).get_many())

    def test_duplicate_username(self):

        users_before_request = len(UserCrud(client.db).get_many())

        with UserAccessCookie(client, test_user_1.username, 'register'):
            response = self.do_request(params={
                'username': test_user_1.username,
                'password': test_user_1_create_schema.password,
                'discord_id': next(get_new_discord_id),
            })

        assert response.status_code == 400

        assert users_before_request == len(UserCrud(client.db).get_many())

    def test_not_authorized(self):

        response = self.do_request()

        assert response.status_code == 401

    def test_user_does_not_have_scope(self):

        users_before_request = len(UserCrud(client.db).get_many())

        with UserAccessCookie(client, test_user_1.username, ''):
            response = self.do_request(params={
                'username': 'test_incorrect_scope_user',
                'password': 'test_incorrect_scope_user',
                'discord_id': next(get_new_discord_id),
            })

        assert response.status_code == 401

        assert users_before_request == len(UserCrud(client.db).get_many())

    def test_correct(self):

        users_before_request = len(UserCrud(client.db).get_many())

        test_correct_user_create_schema = schemas.UserCreate(
            username='test_correct_user', password='test_correct_user', discord_id=next(get_new_discord_id)
        )

        with UserAccessCookie(client, test_user_1.username, 'register'):
            response = self.do_request(params={
                'username': test_correct_user_create_schema.username,
                'password': test_correct_user_create_schema.password,
                'discord_id': test_correct_user_create_schema.discord_id,
            })

        assert response.status_code == 200

        assert users_before_request + 1 == len(UserCrud(client.db).get_many())

        test_correct_user_db = UserCrud(client.db).get(username=test_correct_user_create_schema.username)

        assert test_correct_user_db
        assert test_correct_user_db.discord_id == test_correct_user_create_schema.discord_id

        user_schema = schemas.User.model_validate(test_correct_user_db)
        user_schema.available_scopes = UserToScopeCrud(client.db).get_user_scopes(test_correct_user_db)

        assert user_schema.model_dump() == response.json()