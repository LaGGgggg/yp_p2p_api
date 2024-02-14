from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from . import crud, models, schemas, utils
from .database import get_db

router = APIRouter()


@router.post("/create_user", response_model=schemas.User)
def create_user(
        user: schemas.UserCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(utils.get_current_user)
):
    # Проверка аутентификации
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Валидация данных силами FastAPI
    # Проверка дубликата пользователя
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")

    if crud.get_user_by_discord_id(db, user.discord_id):
        raise HTTPException(status_code=400, detail="Discord ID already registered")

    # Проверка сложности пароля
    if not utils.is_strong_password(user.password):
        raise HTTPException(status_code=400, detail="Weak password")

    # Создание нового пользователя в базе данных
    new_user = models.User(discord_id=user.discord_id, username=user.username, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
