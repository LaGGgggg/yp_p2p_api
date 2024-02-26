from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, BigInteger, DateTime
from sqlalchemy.sql import func
from sqlalchemy_utils import ChoiceType

from .database import Base


class Scope(Base):

    __tablename__ = 'scopes'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    def __str__(self):
        return self.name


class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    discord_id = Column(BigInteger, unique=True, index=True)


class UserToScope(Base):

    __tablename__ = 'users_to_scopes'
    __table_args__ = (UniqueConstraint('user_id', 'scope_id'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    scope_id = Column(Integer, ForeignKey('scopes.id'))


class P2PRequest(Base):
    __tablename__ = 'p2p_requests'

    REVIEW_STATE_CHOICES = [
        ('pending', 'Pending'),
        ('progress', 'Progress'),
        ('completed', 'Completed'),
    ]

    id = Column(Integer, primary_key=True, index=True)
    repository_link = Column(String, index=True, nullable=False)
    comment = Column(String)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    publication_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    review_state = Column(ChoiceType(REVIEW_STATE_CHOICES), nullable=False)
    reviewer_id = Column(Integer, ForeignKey('users.id'))
