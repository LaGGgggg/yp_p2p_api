from .database import Base
from typing import Type, Any
from abc import ABC

from sqlalchemy.orm import Session, Query
from passlib.context import CryptContext

from core import schemas
from . import models


class BaseCrud(ABC):
    def __init__(self, model: Type[Base], db: Session) -> None:
        self.model = model
        self.db = db

    def _get_query(self) -> Query:
        return self.db.query(self.model)

    def _get_query_filtered(self, **kwargs) -> Query:
        return self._get_query().filter_by(**kwargs)
    
    # TODO Статикметоды обычно висят с самого верху класса
    @staticmethod
    def _get_as_list(object_to_get: Any) -> list[Any]:
        return object_to_get if isinstance(object_to_get, list) else [object_to_get]

    def refresh(self, objects_to_refresh: list[Type[Base]] | Type[Base]) -> None:
        for object_to_refresh in self._get_as_list(objects_to_refresh):
            self.db.refresh(object_to_refresh)

    def add_to_db_and_refresh(self, object_to_add: Type[Base]) -> None:
        self.db.add(object_to_add)
        self.db.commit()
        self.refresh(object_to_add)

    def create(self, schema: Type[schemas.BaseModel]) -> Type[Base]:
        db_object = self.model(**schema.model_dump())
        self.add_to_db_and_refresh(db_object)
        return db_object

    def get(self, **kwargs) -> Type[Base]:
        return self._get_query_filtered(**kwargs).first()

    def get_many(self, **kwargs) -> list[Type[Base]]:
        return self._get_query_filtered(**kwargs).all()

    def update(self, objects_to_update: Type[Base] | list[Type[Base]], **kwargs) -> None:

        objects_to_update = self._get_as_list(objects_to_update)

        for object_to_update in objects_to_update:
            for key, value in kwargs.items():
                setattr(object_to_update, key, value)

        self.db.commit()
        self.refresh(objects_to_update)


class UserCrud(BaseCrud):
    def __init__(self, db: Session) -> None:
        self.pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        super().__init__(models.User, db)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def create(self, user_create: schemas.UserCreate) -> Type[Base]:
        hashed_password = self.get_password_hash(user_create.password)
        user_create_db = schemas.UserCreateDB(
            hashed_password=hashed_password, username=user_create.username, discord_id=user_create.discord_id
        )
        return super().create(user_create_db)


class ScopeCrud(BaseCrud):
    def __init__(self, db: Session) -> None:
        super().__init__(models.Scope, db)


class UserToScopeCrud(BaseCrud):
    def __init__(self, db: Session) -> None:
        super().__init__(models.UserToScope, db)

    def get_user_scopes(self, user: schemas.User) -> list[models.Scope]:
        return self.db.query(models.Scope).join(self.model).filter(self.model.user_id == user.id).all()


class P2PReviewCrud(BaseCrud):
    def __init__(self, db: Session) -> None:
        super().__init__(models.P2PReview, db)


class P2PRequestCrud(BaseCrud):
    def __init__(self, db: Session) -> None:
        super().__init__(models.P2PRequest, db)

    def get_oldest_not_user_without_reviews(self, reviewer_id: int) -> models.P2PRequest | None:
        return self._get_query().filter(
            ~self.model.p2p_reviews.any(), self.model.creator_id != reviewer_id
        ).order_by(self.model.publication_date).first()
