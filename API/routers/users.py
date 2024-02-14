from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.responses import Response
from passlib.context import CryptContext

from fastapi_login.exceptions import InvalidCredentialsException

from sql import crud, models
from sql.database import get_db, get_db_not_dependency
from core import schemas
from core.config import get_settings
from core.login_manager import login_manager


SETTINGS = get_settings()

router = APIRouter(tags=['users'])


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


@login_manager.user_loader()
def get_user(username: str, db: Session = get_db_not_dependency()) -> models.User | None:
    return crud.UserCrud().get_by_username(db, username)


@router.post(f'/{SETTINGS.TOKEN_URL}', response_model=schemas.Token)
def login(
        response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)
):

    user = get_user(form_data.username, db)

    if not user:
        raise InvalidCredentialsException

    if not verify_password(form_data.password, user.hashed_password):
        raise InvalidCredentialsException

    user_scopes = [i.name for i in crud.UserToScopeCrud().get_user_scopes(db, user)]

    if not all([(scope in SETTINGS.OAUTH2_SCHEME_SCOPES) and (scope in user_scopes) for scope in form_data.scopes]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect scope(s)',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    access_token = login_manager.create_access_token(data={'sub': user.username, 'scopes': form_data.scopes})

    login_manager.set_cookie(response, access_token)

    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get('/users/me')
def get_user_me_data(
        current_user: models.User = Security(login_manager, scopes=['me']), db: Session = Depends(get_db)
) -> schemas.User:

    if not current_user.is_active:
        return InvalidCredentialsException

    current_user = schemas.User.from_orm(current_user)

    current_user.available_scopes = crud.UserToScopeCrud().get_user_scopes(db, current_user)

    return current_user
