from datetime import datetime

from pydantic import BaseModel, ConfigDict

from sql.models_enums import ReviewStateEnum

# TODO Как-то очень много схем, я бы думаю по разным файликам побил
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


class P2PRequestCreate(P2PRequestBase):
    creator_id: int


class P2PRequest(P2PRequestBase):
    model_config = ConfigDict(from_attributes=True)
  
    id: int
    publication_date: datetime


class ErrorResponse(BaseModel):
    context: str


class P2PReviewBase(BaseModel):
    pass


class P2PReviewCreate(P2PReviewBase):
    reviewer_id: int
    p2p_request_id: int


class P2PReview(P2PReviewBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reviewer_id: int
    p2p_request_id: int
    creation_date: datetime
    end_date: datetime
    review_state: ReviewStateEnum
    link: str
