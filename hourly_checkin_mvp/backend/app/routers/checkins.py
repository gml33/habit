from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db
from ..settings import settings

router = APIRouter(prefix="/checkins", tags=["checkins"])


def verify_token(
    authorization: str | None = Header(default=None),
    token: str | None = Query(default=None),
) -> str:
    provided = None
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            provided = parts[1]
    if not provided and token:
        provided = token
    if not provided or provided != settings.api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return provided


@router.post("", response_model=schemas.CheckinOut, dependencies=[Depends(verify_token)])
def upsert_checkin(payload: schemas.CheckinCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    data["created_at"] = datetime.now(timezone.utc)

    insert_stmt = (
        sqlite_insert(models.Checkin)
        if db.bind.dialect.name == "sqlite"
        else pg_insert(models.Checkin)
    )

    stmt = insert_stmt.values(**data)
    update_fields = {
        key: value
        for key, value in data.items()
        if key not in {"user_id", "ts_hour", "created_at"}
    }
    stmt = stmt.on_conflict_do_update(
        index_elements=["user_id", "ts_hour"],
        set_=update_fields,
    )

    db.execute(stmt)
    db.commit()

    record = (
        db.query(models.Checkin)
        .filter(
            models.Checkin.user_id == payload.user_id,
            models.Checkin.ts_hour == payload.ts_hour,
        )
        .first()
    )
    return record


@router.get("", response_model=list[schemas.CheckinOut], dependencies=[Depends(verify_token)])
def list_checkins(
    user_id: str = Query(...),
    from_: datetime | None = Query(default=None, alias="from"),
    to_: datetime | None = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
):
    query = db.query(models.Checkin).filter(models.Checkin.user_id == user_id)

    if from_:
        query = query.filter(models.Checkin.ts_hour >= from_)
    if to_:
        query = query.filter(models.Checkin.ts_hour <= to_)

    return query.order_by(models.Checkin.ts_hour.asc()).all()
