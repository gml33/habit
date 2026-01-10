from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

UTC_TZ = ZoneInfo("UTC")


def validate_timezone(value: str) -> ZoneInfo:
    try:
        return ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ValueError("Timezone invalida") from exc


def ensure_aware(value: datetime, default_tz: ZoneInfo) -> datetime:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        return value.replace(tzinfo=default_tz)
    return value


def floor_to_hour_local(value: datetime, tz: ZoneInfo) -> datetime:
    aware = ensure_aware(value, tz)
    local = aware.astimezone(tz)
    return local.replace(minute=0, second=0, microsecond=0)


def to_utc(value: datetime, default_tz: ZoneInfo) -> datetime:
    aware = ensure_aware(value, default_tz)
    return aware.astimezone(UTC_TZ)


def to_local_iso(value: datetime, tz: ZoneInfo) -> str:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(tz).isoformat()


def datetime_to_utc_iso(value: datetime) -> str:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(UTC_TZ).isoformat().replace("+00:00", "Z")
