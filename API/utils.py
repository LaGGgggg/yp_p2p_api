from sys import argv
from logging import INFO, basicConfig, info, warning, error

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

from sql.database import get_db_not_dependency
from sql import crud
from core import schemas
from core.config import get_settings


basicConfig(level=INFO)

SETTINGS = get_settings()

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def create_superuser(username: str, password: str, db: Session) -> None:

    try:
        user = crud.UserCrud().create_with_pwd_context(db, schemas.UserCreate(username=username, password=password), pwd_context)

    except IntegrityError:

        warning('The user already exists')

        db.rollback()

        user = crud.UserCrud().get_by_username(db, username)

    all_user_scopes = crud.UserToScopeCrud().get_user_scopes(db, user)

    for scope in crud.ScopeCrud().get_all(db):
        if scope not in all_user_scopes:
            crud.UserToScopeCrud().create(db, schemas.UserToScopeCreate(user_id=user.id, scope_id=scope.id))


if __name__ == '__main__':

    if 'create_superuser' in argv and len(argv) == 4:

        try:

            create_superuser(*argv[2:], db=get_db_not_dependency())

            info('Superuser successfully created')

        except Exception as e:
            error(f'Something went wrong\n{e}')

    else:
        error('Unknown command or incorrect command arguments')
