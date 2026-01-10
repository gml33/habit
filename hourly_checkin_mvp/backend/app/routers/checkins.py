from datetime import date, datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db
from ..deps import get_current_user
from ..time_utils import floor_to_hour_local, to_local_iso, to_utc, validate_timezone

router = APIRouter(prefix="/checkins", tags=["checkins"])

def apply_checkin_update(record: models.Checkin, payload: schemas.CheckinCreate) -> None:
    record.activity = payload.activity
    record.emotion = payload.emotion
    record.energy = payload.energy
    record.stress = payload.stress
    record.note = payload.note
    record.source = payload.source


def build_checkin_out(record: models.Checkin, user_tz) -> schemas.CheckinOut:
    return schemas.CheckinOut(
        id=record.id,
        user_id=record.user_id,
        ts_hour_utc=record.ts_hour_utc,
        ts_hour_local=to_local_iso(record.ts_hour_utc, user_tz),
        activity=record.activity,
        emotion=record.emotion,
        energy=record.energy,
        stress=record.stress,
        note=record.note,
        source=record.source,
        created_at_utc=record.created_at,
        created_at_local=to_local_iso(record.created_at, user_tz),
    )


@router.post("", response_model=schemas.CheckinOut)
def upsert_checkin(
    payload: schemas.CheckinCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        user_tz = validate_timezone(current_user.timezone)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    local_hour = floor_to_hour_local(payload.ts_hour, user_tz)
    normalized_ts = to_utc(local_hour, user_tz)

    record = (
        db.query(models.Checkin)
        .filter(
            models.Checkin.user_id == current_user.user_id,
            models.Checkin.ts_hour_utc == normalized_ts,
        )
        .first()
    )

    if record:
        apply_checkin_update(record, payload)
    else:
        record = models.Checkin(
            user_id=current_user.user_id,
            ts_hour_utc=normalized_ts,
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
                models.Checkin.user_id == current_user.user_id,
                models.Checkin.ts_hour_utc == normalized_ts,
            )
            .first()
        )
        if record:
            apply_checkin_update(record, payload)
        else:
            record = models.Checkin(
                user_id=current_user.user_id,
                ts_hour_utc=normalized_ts,
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
    return build_checkin_out(record, user_tz)


@router.get("", response_model=list[schemas.CheckinOut])
def list_checkins(
    from_: datetime | None = Query(default=None, alias="from"),
    to_: datetime | None = Query(default=None, alias="to"),
    day: date | None = Query(default=None),
    user_id: str | None = Query(default=None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user_id and user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado para ese usuario",
        )

    try:
        user_tz = validate_timezone(current_user.timezone)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    query = db.query(models.Checkin).filter(models.Checkin.user_id == current_user.user_id)

    if day:
        start_local = datetime.combine(day, time.min).replace(tzinfo=user_tz)
        end_local = datetime.combine(day, time.max).replace(tzinfo=user_tz)
        query = query.filter(
            models.Checkin.ts_hour_utc >= to_utc(start_local, user_tz),
            models.Checkin.ts_hour_utc <= to_utc(end_local, user_tz),
        )
    else:
        if from_:
            local_from = floor_to_hour_local(from_, user_tz)
            query = query.filter(models.Checkin.ts_hour_utc >= to_utc(local_from, user_tz))
        if to_:
            local_to = floor_to_hour_local(to_, user_tz)
            query = query.filter(models.Checkin.ts_hour_utc <= to_utc(local_to, user_tz))

    records = query.order_by(models.Checkin.ts_hour_utc.asc()).all()
    return [build_checkin_out(record, user_tz) for record in records]
