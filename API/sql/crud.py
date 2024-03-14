from .database import Base
from typing import Type, Any
from abc import ABC
from datetime import datetime

from sqlalchemy.orm import Session, Query
from passlib.context import CryptContext

from core import schemas
from . import models
from sql.models_enums import ReviewStateEnum


class BaseCrud(ABC):
    def __init__(self, model: Type[Base], db: Session) -> None:
        self.model = model
        self.db = db

    def _get_query(self) -> Query:
        return self.db.query(self.model)

    def _get_query_filtered(self, **kwargs) -> Query:
        return self._get_query().filter_by(**kwargs)

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
        return self._get_query().join(self.model).filter(self.model.user_id == user.id).all()


class ReviewCrud(BaseCrud):
    def __init__(self, db: Session) -> None:
        super().__init__(models.P2PReview, db)

    def end_review(self, reviewer_id: int, link: str) -> None:

        review = self.get(reviewer_id=reviewer_id)
        review.link = link
        review.end_date = datetime.now()
        review.review_state = ReviewStateEnum.COMPLETED.value
        self.db.commit()


class P2PRequestCrud(BaseCrud):
    def __init__(self, db: Session) -> None:
        super().__init__(models.P2PRequest, db)

    def start_review(self, reviewer_id: int, create_schema: schemas.ReviewCreate) -> models.P2PRequest | None:

        project = self.db.query(self.model).filter(
            self.model.review_state == ReviewStateEnum.PENDING.value, self.model.creator_id != reviewer_id
        ).order_by(self.model.publication_date).first()

        if not project:
            return None

        ReviewCrud(self.db).create(create_schema)

        return project
