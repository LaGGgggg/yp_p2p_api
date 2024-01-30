from pydantic import BaseModel


class Token(BaseModel):

    access_token: str
    token_type: str


class ScopeBase(BaseModel):
    name: str


class ScopeCreate(ScopeBase):
    pass


class Scope(ScopeBase):

    id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):

    id: int
    is_active: bool = True
    available_scopes: list[Scope] = []

    class Config:
        from_attributes = True


class UserToScopeBase(BaseModel):

    user_id: int
    scope_id: int


class UserToScopeCreate(UserToScopeBase):
    pass


class UserToScope(UserToScopeBase):

    id: int

    class Config:
        from_attributes = True
