from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from sql import crud, models
from sql.database import get_db
from core import schemas
from core.login_manager import login_manager

router = APIRouter(tags=['p2p_request'])


@router.post('/p2p_request/create')
def create_p2p_request(
        repository_link: str,
        comment: str,
        current_user: models.User = Security(login_manager, scopes=['p2p_request']),
        db: Session = Depends(get_db)
) -> bool:
    p2p_request_create = schemas.P2PRequestCreate(
        repository_link=repository_link, comment=comment, creator_id=current_user.id,
    )

    crud.P2PRequestCrud(db).create(p2p_request_create)

    return True

