from datetime import datetime

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from sql import crud, models
from sql.database import get_db
from core import schemas
from core.login_manager import login_manager
from sql.models_enums import ReviewStateEnum

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


@router.get('/p2p_request/list')
def get_p2p_requests_list(
        current_user: models.User = Security(login_manager, scopes=['p2p_request'])
) -> list[schemas.P2PRequest]:
    return [schemas.P2PRequest.model_validate(p2p_request) for p2p_request in current_user.p2p_requests]


@router.get('/p2p_request/review/start')
def p2p_request_start_review(
        current_user: models.User = Security(login_manager, scopes=['p2p_request']),
        db: Session = Depends(get_db)
) -> schemas.P2PRequest | schemas.ErrorResponse:

    reviewer_id = current_user.id
    p2p_review_crud = crud.P2PReviewCrud(db)

    if p2p_review_crud.get(review_state=ReviewStateEnum.PROGRESS.value, reviewer_id=reviewer_id):
        return schemas.ErrorResponse(context='You already have a review, complete it first')

    p2p_request = crud.P2PRequestCrud(db).get_oldest_not_user_without_reviews(reviewer_id)

    if not p2p_request:
        return schemas.ErrorResponse(context='There are not any pending projects')

    p2p_review_crud.create(schemas.P2PReviewCreate(reviewer_id=reviewer_id, p2p_request_id=p2p_request.id))

    return schemas.P2PRequest.model_validate(p2p_request)


@router.post('/p2p_request/review/complete')
def p2p_request_complete_review(
        link: str,
        p2p_request_id: int,
        current_user: models.User = Security(login_manager, scopes=['p2p_request']),
        db: Session = Depends(get_db)
) -> schemas.P2PReview | schemas.ErrorResponse:

    reviewer_id = current_user.id

    review_crud = crud.P2PReviewCrud(db)

    review = review_crud.get(
        p2p_request_id=p2p_request_id, review_state=ReviewStateEnum.PROGRESS.value, reviewer_id=reviewer_id
    )

    if not review:
        return schemas.ErrorResponse(context='Review not found')

    review_crud.update(review, link=link, end_date=datetime.now(), review_state=ReviewStateEnum.COMPLETED.value)

    return schemas.P2PReview.model_validate(review)
