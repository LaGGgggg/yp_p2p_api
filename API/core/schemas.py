from datetime import datetime

from pydantic import BaseModel, ConfigDict

from sql.models_choices_enums import ReviewStateChoicesEnum


class Token(BaseModel):
    access_token: str
    token_type: str


class ScopeBase(BaseModel):
    name: str


class ScopeCreate(ScopeBase):
    pass


class Scope(ScopeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class UserBase(BaseModel):
    username: str
    discord_id: int


class UserCreate(UserBase):
    password: str


class UserCreateDB(UserBase):
    hashed_password: str


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool = True
    available_scopes: list[Scope] = []


class UserToScopeBase(BaseModel):
    user_id: int
    scope_id: int


class UserToScopeCreate(UserToScopeBase):
    pass


class UserToScope(UserToScopeBase):
    model_config = ConfigDict(from_attributes=True)
  
    id: int


class P2PRequestBase(BaseModel):
    repository_link: str
    comment: str
    review_state: ReviewStateChoicesEnum


class P2PRequestCreate(P2PRequestBase):
    creator_id: int
    reviewer_id: int | None = None
    review_start_date: datetime | None = None
    review_state: ReviewStateChoicesEnum = ReviewStateChoicesEnum.PENDING.value


class P2PRequest(P2PRequestBase):
    model_config = ConfigDict(from_attributes=True)
  
    id: int
    publication_date: datetime
    creator: User
    reviewer: User | None
    review_start_date: datetime | None
