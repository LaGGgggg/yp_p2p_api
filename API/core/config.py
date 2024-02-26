from os import environ
from functools import cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import PostgresDsn, BaseModel, ConfigDict, ValidationError
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict
from fastapi.security import OAuth2PasswordBearer


OAUTH2_SCHEME_SCOPES = {
    'me': 'can see the logged in user profile',
    'register': 'can register new users',
}


class BaseSettings(BaseModel):

    DATABASE_URL: PostgresDsn
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: float
    TOKEN_URL: str
    DEBUG: bool
    DATABASE_URL_TEST: PostgresDsn | None = None
    IS_TEST: bool = False  # needed only for automated testing purposes


class RawSettings(BaseSettings, PydanticBaseSettings):
    model_config = SettingsConfigDict(env_file='../core/.env', env_file_encoding='UTF-8')


class Settings(BaseSettings):

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # here are all the environment variables with custom parsing logic (or if the variable should not be set by .env)
    ORIGINS: list[str]
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    LOGS_DIR: Path = BASE_DIR / 'logs'
    LOGGING: dict = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'main': {
                'format': '[{levelname}] [{asctime}] path - "{pathname}" function - "{funcName}" message - "{message}"',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'main',
            },
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'main',
                'filename': LOGS_DIR / 'info.log',
                'maxBytes': 1024 * 1024 * 100,  # 100 Mb
                'encoding': 'utf-8',
            },
        },
        'loggers': {
            'main': {
                'handlers': [],
                'level': 'INFO',
            },
        },
    }
    OPENAPI_URL: str = '/openapi.json'
    OAUTH2_SCHEME: OAuth2PasswordBearer
    OAUTH2_SCHEME_SCOPES: dict = OAUTH2_SCHEME_SCOPES


@cache
def get_settings() -> Settings:

    load_dotenv('core/.env')

    if origins := environ.get('ORIGINS', None):
        origins = origins.split(', ')

    raw_settings = RawSettings()

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl=raw_settings.TOKEN_URL, scopes=OAUTH2_SCHEME_SCOPES)

    settings = Settings(ORIGINS=origins, OAUTH2_SCHEME=oauth2_scheme, **raw_settings.model_dump())

    settings.LOGGING['loggers']['main']['handlers'] = ['console'] if settings.DEBUG else ['file']

    if settings.IS_TEST and not settings.DATABASE_URL_TEST:
        raise ValidationError('To run tests, you need to set the DATABASE_URL_TEST environment variable')

    return settings
