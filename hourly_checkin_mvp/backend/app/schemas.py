from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_serializer, field_validator

from .time_utils import datetime_to_utc_iso, validate_timezone


class ActivityEnum(str, Enum):
    sleep = "dormir"
    work = "trabajo"
    hobbies = "pasatiempos"
    exercise = "ejercicio"
    leisure = "tiempo_libre"
    partner = "pareja"
    family = "familia"
    chores = "tareas"
    travel = "viaje"
    misc = "otros"


class EmotionEnum(str, Enum):
    fine = "bien"
    happy = "feliz"
    excited = "entusiasmado"
    sad = "triste"
    sensitive = "sensible"
    anxious = "ansioso"
    insecure = "inseguro"
    angry = "enojado"
    irritated = "irritable"
    neutral = "neutral"
    emotional = "emocional"


class EnergyEnum(str, Enum):
    tired = "cansado"
    okay = "ok"
    energized = "con_energia"


class StressEnum(str, Enum):
    low = "bajo"
    medium = "medio"
    high = "alto"


class SourceEnum(str, Enum):
    notification = "notificacion"
    manual = "manual"
    backfill = "carga_historica"


class CheckinCreate(BaseModel):
    ts_hour: datetime
    activity: ActivityEnum
    emotion: EmotionEnum
    energy: EnergyEnum
    stress: StressEnum
    note: str | None = Field(default=None, max_length=140)
    source: SourceEnum

    @field_validator("note")
    @classmethod
    def normalize_note(cls, value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None

    model_config = {"extra": "ignore"}


class CheckinOut(BaseModel):
    id: int
    user_id: str
    ts_hour_utc: datetime
    ts_hour_local: str
    activity: ActivityEnum
    emotion: EmotionEnum
    energy: EnergyEnum
    stress: StressEnum
    note: str | None
    source: SourceEnum
    created_at_utc: datetime
    created_at_local: str

    @field_serializer("ts_hour_utc", when_used="json")
    def serialize_ts_hour_utc(self, value: datetime) -> str:
        return datetime_to_utc_iso(value)

    @field_serializer("created_at_utc", when_used="json")
    def serialize_created_at_utc(self, value: datetime) -> str:
        return datetime_to_utc_iso(value)


class UserCreate(BaseModel):
    user_id: str = Field(min_length=3, max_length=64)
    display_name: str | None = Field(default=None, max_length=120)
    timezone: str = Field(default="America/Argentina/Buenos_Aires")

    @field_validator("timezone")
    @classmethod
    def validate_timezone_value(cls, value: str) -> str:
        validate_timezone(value)
        return value


class UserCreatedOut(BaseModel):
    user_id: str
    display_name: str | None
    timezone: str
    api_token: str
    created_at: datetime


class UserMeOut(BaseModel):
    user_id: str
    display_name: str | None
    timezone: str
    created_at: datetime


class UserUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=120)
    timezone: str | None = Field(default=None)

    @field_validator("timezone")
    @classmethod
    def validate_timezone_value(cls, value: str | None) -> str | None:
        if value is None:
            return None
        validate_timezone(value)
        return value
