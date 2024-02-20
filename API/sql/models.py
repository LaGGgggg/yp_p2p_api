from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, BigInteger

from .database import Base


class Scope(Base):

    __tablename__ = 'scopes'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    def __str__(self):
        return self.name


class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    discord_id = Column(BigInteger, unique=True, index=True, nullable=False)


class UserToScope(Base):

    __tablename__ = 'users_to_scopes'
    __table_args__ = (UniqueConstraint('user_id', 'scope_id'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    scope_id = Column(Integer, ForeignKey('scopes.id'))
