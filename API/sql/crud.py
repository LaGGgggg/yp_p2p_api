from sqlalchemy.orm import Session
from passlib.context import CryptContext

from core import schemas
from . import models


def _add_to_db_and_refresh(db: Session, object_to_add) -> None:

    db.add(object_to_add)
    db.commit()
    db.refresh(object_to_add)


def get_all_scopes(db: Session) -> list[models.Scope]:
    return db.query(models.Scope).all()


def create_scope(db: Session, scope: schemas.ScopeCreate) -> models.Scope:

    db_scope = models.Scope(**scope.dict())

    _add_to_db_and_refresh(db, db_scope)

    return db_scope


def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(models.User.username == username).first()


def _get_password_hash(password: str, pwd_context: CryptContext) -> str:
    return pwd_context.hash(password)


def create_user(db: Session, user: schemas.UserCreate, pwd_context: CryptContext) -> models.User:

    hashed_password = _get_password_hash(user.password, pwd_context)

    db_user = models.User(username=user.username, hashed_password=hashed_password)

    _add_to_db_and_refresh(db, db_user)

    return db_user


def get_user_scopes(db: Session, user: schemas.User) -> list[models.Scope]:
    return db.query(models.Scope).join(models.UserToScope).filter(models.UserToScope.user_id == user.id).all()


def create_user_to_scope(db: Session, user_to_scope: schemas.UserToScopeCreate) -> models.UserToScope:

    db_user_to_scope = models.UserToScope(**user_to_scope.dict())

    _add_to_db_and_refresh(db, db_user_to_scope)

    return db_user_to_scope
