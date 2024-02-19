from sqlalchemy.orm import Session
from passlib.context import CryptContext

from core import schemas
from . import models

from .database import Base
from typing import Type
from abc import ABC


class BaseCrud(ABC):
    def __init__(self, model: Type[Base], scheme: Type[schemas.BaseModel], db: Session) -> None:
        self.model = model
        self.scheme = scheme
        self.db = db

    def add_to_db_and_refresh(self, object_to_add: Type[Base]) -> None:
        self.db.add(object_to_add)
        self.db.commit()
        self.db.refresh(object_to_add)

    def create(self, **kwargs):
        db_object = self.model(**kwargs)
        self.add_to_db_and_refresh(db_object)
        return db_object

    def get(self, **kwargs) -> Type[Base]:
        return self.db.query(self.model).filter_by(**kwargs).first()

    def get_many(self, *args, **kwargs) -> list[Type[Base]]:
        return self.db.query(self.model).filter(*args, **kwargs).all()


class UserCrud(BaseCrud):
    def __init__(self, db: Session) -> None:
        self.pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        super().__init__(models.User, schemas.UserCreate, db)

    def create(self, user: schemas.UserCreate):
        hashed_password = self.get_password_hash(user.password)
        return super().create(usernsme=user, hashed_password=hashed_password)

    def get_by_username(self, username: str):
        return self.db.query(self.model).filter(self.model.username == username).first()

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)


class ScopeCrud(BaseCrud):
    def __init__(self, db: Session) -> None:
        super().__init__(models.Scope, schemas.ScopeCreate, db)


class UserToScopeCrud(BaseCrud):
    def __init__(self, db: Session) -> None:
        super().__init__(models.UserToScope, schemas.UserToScopeCreate, db)

    def get_user_scopes(self, user: schemas.User) -> list[models.Scope]:
        return self.db.query(models.Scope).join(self.model).filter(self.model.user_id == user.id).all()
