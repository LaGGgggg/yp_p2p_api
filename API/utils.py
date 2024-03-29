from sys import argv
from logging import INFO, basicConfig, info, warning, error
from typing import Callable

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from sql.database import get_db_not_dependency
from sql import crud
from core import schemas


basicConfig(level=INFO)

BLUE = '\033[0;34m'
YELLOW = '\033[0;33m'
RED = '\033[0;31m'
NO_COLOR = '\033[0m'


def log_with_color(log_function: Callable, message: str, color: str = BLUE) -> None:
    log_function(f'{color}{message}{NO_COLOR}')


def create_superuser(username: str, password: str, discord_id: str, db: Session) -> None:
    # TODO Че за дискорд айдишник
    discord_id = int(discord_id)

    try:
        user = crud.UserCrud(db).create(
            schemas.UserCreate(username=username, password=password, discord_id=discord_id)
        )

    except IntegrityError:

        log_with_color(warning, "The user already exists, just updates the user's scopes", YELLOW)

        db.rollback()

        user = crud.UserCrud(db).get(username=username) or crud.UserCrud(db).get(discord_id=discord_id)

    all_user_scopes = crud.UserToScopeCrud(db).get_user_scopes(user)

    for scope in crud.ScopeCrud(db).get_many():
        if scope not in all_user_scopes:
            crud.UserToScopeCrud(db).create(schemas.UserToScopeCreate(user_id=user.id, scope_id=scope.id))

    log_with_color(info, 'Superuser successfully created/updated')


if __name__ == '__main__':

    if 'create_superuser' in argv and len(argv) == 5:

        try:
            create_superuser(*argv[2:], db=get_db_not_dependency())

        except Exception as e:
            log_with_color(error, f'Something went wrong\n{e}', RED)

    else:
        log_with_color(error, 'Unknown command or incorrect command arguments', RED)
