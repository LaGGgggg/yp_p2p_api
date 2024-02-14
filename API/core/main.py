from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sql import crud
from sql.database import get_db, get_db_not_dependency
from . import schemas
from .config import get_settings
from routers import system, users


SETTINGS = get_settings()

tags_metadata = [
    {
        'name': 'users',
        'description': 'users section',
    },
]


app = FastAPI(
    title='YP_P2P_API',
    description='Yandex practicum p2p API',
    version='0.0.1',
    contact={
        'name': 'admin',
        'email': 'poni22poni23@yandex.ru',
    },
    openapi_tags=tags_metadata,
    openapi_url=SETTINGS.OPENAPI_URL,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=SETTINGS.ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
async def startup_db_scopes_init() -> None:

    db = get_db_not_dependency()

    all_scopes = [str(i) for i in crud.ScopeCrud().get_all(db)]

    for scope_name in SETTINGS.OAUTH2_SCHEME_SCOPES:
        if scope_name not in all_scopes:
            crud.ScopeCrud().create(db, schemas.ScopeCreate(name=scope_name))


app.include_router(users.router)
app.include_router(system.router)
