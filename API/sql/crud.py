from .database import Base
from typing import Type
from abc import ABC
from datetime import datetime

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from core import schemas
from . import models
from sql.models_enums import ReviewStateEnum


class BaseCrud(ABC):
    def __init__(self, model: Type[Base], db: Session) -> None:
        self.model = model
        self.db = db

    def add_to_db_and_refresh(self, object_to_add: Type[Base]) -> None:
        self.db.add(object_to_add)
        self.db.commit()
        self.db.refresh(object_to_add)

    def create(self, schema: Type[schemas.BaseModel]) -> Type[Base]:
        db_object = self.model(**schema.model_dump())
        self.add_to_db_and_refresh(db_object)
        return db_object

    def get(self, **kwargs) -> Type[Base]:
        return self.db.query(self.model).filter_by(**kwargs).first()

    def get_many(self, **kwargs) -> list[Type[Base]]:
        return self.db.query(self.model).filter_by(**kwargs).all()


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
