from fastapi import APIRouter
from fastapi.responses import RedirectResponse, HTMLResponse

from core.config import get_settings


SETTINGS = get_settings()

router = APIRouter(include_in_schema=False)


@router.get('/rapidoc', response_class=HTMLResponse)
async def rapidoc():
    return f"""
        <!doctype html>
        <html>
            <head>
                <meta charset="utf-8">
                <script 
                    type="module" 
                    src="https://unpkg.com/rapidoc/dist/rapidoc-min.js"
                ></script>
            </head>
            <body>
                <rapi-doc spec-url="{SETTINGS.OPENAPI_URL}"></rapi-doc>
            </body> 
        </html>
    """


@router.get('/{_:path}')
async def unknown_page_handler(_: str) -> RedirectResponse:
    """
    Redirects all unknown urls to the "docs" page
    """
    return RedirectResponse('/rapidoc')
