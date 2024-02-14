from sqlalchemy.orm import Session
from passlib.context import CryptContext

from core import schemas
from . import models


class BaseCrud:
    
    def add_to_db_and_refresh(self, db: Session, object_to_add) -> None:
        db.add(object_to_add)
        db.commit()
        db.refresh(object_to_add)


    def create(self, db: Session, object: self.scheme) -> self.model:

        db_object = self.model(**object.dict())

        self.add_to_db_and_refresh(db, db_object)

        return db_object


    def get_all(self, db: Session) -> list[self.model]:
        return db.query(self.model).all()


class UserCrud(BaseCrud):
    def __init__(self):
        self.model = models.User
        self.scheme = schemas.UserCreate


    def create_with_pwd_context(self, db: Session, user: schemas.UserCreate, pwd_context: CryptContext) -> self.model:

        hashed_password = self.get_password_hash(user.password, pwd_context)

        db_user = self.model(username=user.username, hashed_password=hashed_password)

        self.add_to_db_and_refresh(db, db_user)

        return db_user


    def get_by_username(self, db: Session, username: str) -> self.model | None:
        return db.query(self.model).filter(self.model.username == username).first()


    def get_password_hash(self, password: str, pwd_context: CryptContext) -> str:
        return pwd_context.hash(password)


class ScopeCrud(BaseCrud):
    def __init__(self):
        self.model = models.Scope
        self.scheme = schemas.ScopeCreate


class UserToScopeCrud(BaseCrud):
    def __init__(self):
        self.model = models.UserToScope
        self.scheme = schemas.UserToScopeCreate


    def get_user_scopes(self, db: Session, user: schemas.User) -> list[models.Scope]:
        return db.query(models.Scope).join(self.model).filter(self.model.user_id == user.id).all()
