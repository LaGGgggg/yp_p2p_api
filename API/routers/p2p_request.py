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


@router.get('/p2p_request/review')
def p2p_request_review(
        current_user: models.User = Security(login_manager, scopes=['p2p_request']),
        db: Session = Depends(get_db)
) -> schemas.P2PRequest | schemas.ErrorResponse:

    p2p_request_crud = crud.P2PRequestCrud(db)

    if p2p_request_crud.get(review_state=models.P2PRequest.PROGRESS, reviewer_id=current_user.id):
        return schemas.ErrorResponse(context='You already have a review, complete it first')

    project = p2p_request_crud.start_review(current_user.id)

    if not project:
        return schemas.ErrorResponse(context='There are not any pending projects')

    return schemas.P2PRequest.model_validate(project)
