from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
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
            detail="Token invalido",
        )
    return provided


def normalize_to_hour(value: datetime, field_name: str = "ts_hour") -> datetime:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} debe incluir zona horaria",
        )
    return value.replace(minute=0, second=0, microsecond=0)


def apply_checkin_update(record: models.Checkin, payload: schemas.CheckinCreate) -> None:
    record.activity = payload.activity
    record.emotion = payload.emotion
    record.energy = payload.energy
    record.stress = payload.stress
    record.note = payload.note
    record.source = payload.source


@router.post("", response_model=schemas.CheckinOut, dependencies=[Depends(verify_token)])
def upsert_checkin(payload: schemas.CheckinCreate, db: Session = Depends(get_db)):
    normalized_ts = normalize_to_hour(payload.ts_hour)

    record = (
        db.query(models.Checkin)
        .filter(
            models.Checkin.user_id == payload.user_id,
            models.Checkin.ts_hour == normalized_ts,
        )
        .first()
    )

    if record:
        apply_checkin_update(record, payload)
    else:
        record = models.Checkin(
            user_id=payload.user_id,
            ts_hour=normalized_ts,
            activity=payload.activity,
            emotion=payload.emotion,
            energy=payload.energy,
            stress=payload.stress,
            note=payload.note,
            source=payload.source,
        )
        db.add(record)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        record = (
            db.query(models.Checkin)
            .filter(
                models.Checkin.user_id == payload.user_id,
                models.Checkin.ts_hour == normalized_ts,
            )
            .first()
        )
        if record:
            apply_checkin_update(record, payload)
        else:
            record = models.Checkin(
                user_id=payload.user_id,
                ts_hour=normalized_ts,
                activity=payload.activity,
                emotion=payload.emotion,
                energy=payload.energy,
                stress=payload.stress,
                note=payload.note,
                source=payload.source,
            )
            db.add(record)
        db.commit()

    db.refresh(record)
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
        normalized_from = normalize_to_hour(from_, field_name="from")
        query = query.filter(models.Checkin.ts_hour >= normalized_from)
    if to_:
        normalized_to = normalize_to_hour(to_, field_name="to")
        query = query.filter(models.Checkin.ts_hour <= normalized_to)

    return query.order_by(models.Checkin.ts_hour.asc()).all()
