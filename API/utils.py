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


def create_superuser(username: str, password: str, discord_id: str, db: Session) -> None:

    try:
        user = crud.UserCrud(db).create(schemas.UserCreate(username=username, password=password, discord_id=int(discord_id)))

    except IntegrityError:

        warning("The user already exists, just updates the user's scopes")

        db.rollback()

        user = crud.UserCrud(db).get(username=username)

    all_user_scopes = crud.UserToScopeCrud(db).get_user_scopes(user)

    for scope in crud.ScopeCrud(db).get_many():
        if scope not in all_user_scopes:
            crud.UserToScopeCrud(db).create(schemas.UserToScopeCreate(user_id=user.id, scope_id=scope.id))


if __name__ == '__main__':

    if 'create_superuser' in argv and len(argv) == 5:

        try:

            create_superuser(*argv[2:], db=get_db_not_dependency())

            info('Superuser successfully created/updated')

        except Exception as e:
            error(f'Something went wrong\n{e}')

    else:
        error('Unknown command or incorrect command arguments')
