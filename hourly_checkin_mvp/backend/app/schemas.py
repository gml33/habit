from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


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


class CheckinBase(BaseModel):
    user_id: str
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


class CheckinCreate(CheckinBase):
    pass


class CheckinOut(CheckinBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class UserAuth(BaseModel):
    user_id: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class UserOut(BaseModel):
    user_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
