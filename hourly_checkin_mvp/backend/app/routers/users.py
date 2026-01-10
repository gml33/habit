import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=schemas.UserCreatedOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.user_id == payload.user_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El usuario ya existe")

    api_token = secrets.token_urlsafe(32)
    user = models.User(
        user_id=payload.user_id,
        display_name=payload.display_name,
        timezone=payload.timezone,
        api_token=api_token,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return schemas.UserCreatedOut(
        user_id=user.user_id,
        display_name=user.display_name,
        timezone=user.timezone,
        api_token=user.api_token,
        created_at=user.created_at,
    )


@router.get("/me", response_model=schemas.UserMeOut)
def get_me(current_user: models.User = Depends(get_current_user)):
    return schemas.UserMeOut(
        user_id=current_user.user_id,
        display_name=current_user.display_name,
        timezone=current_user.timezone,
        created_at=current_user.created_at,
    )


@router.patch("/me", response_model=schemas.UserMeOut)
def update_me(
    payload: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.display_name is not None:
        current_user.display_name = payload.display_name
    if payload.timezone is not None:
        current_user.timezone = payload.timezone

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return schemas.UserMeOut(
        user_id=current_user.user_id,
        display_name=current_user.display_name,
        timezone=current_user.timezone,
        created_at=current_user.created_at,
    )
