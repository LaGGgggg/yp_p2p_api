from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from core.config import get_settings


SETTINGS = get_settings()

engine = create_engine(str(SETTINGS.DATABASE_URL_TEST) if SETTINGS.IS_TEST else str(SETTINGS.DATABASE_URL))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    with SessionLocal() as db:
        yield db


def get_db_not_dependency() -> Session:
    with SessionLocal() as db:
        return db
