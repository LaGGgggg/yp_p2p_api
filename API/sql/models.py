from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, BigInteger, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .database import Base
from .models_enums import ReviewStateEnum


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

    p2p_requests = relationship('P2PRequest', back_populates='creator')
    p2p_reviews = relationship('P2PReview', back_populates='reviewer')


class UserToScope(Base):

    __tablename__ = 'users_to_scopes'
    __table_args__ = (UniqueConstraint('user_id', 'scope_id'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    scope_id = Column(Integer, ForeignKey('scopes.id'), nullable=False)


class P2PRequest(Base):
    __tablename__ = 'p2p_requests'

    id = Column(Integer, primary_key=True, index=True)
    repository_link = Column(String, index=True, nullable=False)
    comment = Column(String, nullable=False, default='')
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    publication_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    creator = relationship('User', back_populates='p2p_requests')
    p2p_reviews = relationship('P2PReview', back_populates='p2p_request')


class P2PReview(Base):
    __tablename__ = 'p2p_reviews'

    id = Column(Integer, primary_key=True, index=True)
    link = Column(String)
    creation_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    end_date = Column(DateTime(timezone=True))
    review_state = Column(
        Enum(ReviewStateEnum, name='review_state_enums', values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=ReviewStateEnum.PROGRESS,
    )
    reviewer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    p2p_request_id = Column(Integer, ForeignKey('p2p_requests.id'), nullable=False)

    reviewer = relationship('User', back_populates='p2p_reviews')
    p2p_request = relationship('P2PRequest', back_populates='p2p_reviews')
