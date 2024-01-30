from datetime import timedelta

from fastapi_login import LoginManager

from core.config import get_settings


SETTINGS = get_settings()


login_manager = LoginManager(
    SETTINGS.SECRET_KEY,
    algorithm=SETTINGS.ALGORITHM,
    default_expiry=timedelta(minutes=SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES),
    token_url=SETTINGS.TOKEN_URL,
    use_cookie=True,
    scopes=SETTINGS.OAUTH2_SCHEME_SCOPES
)
