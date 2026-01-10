from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class ActivityEnum(str, Enum):
    sleep = "sleep"
    work = "work"
    hobbies = "hobbies"
    exercise = "exercise"
    leisure = "leisure"
    partner = "partner"
    family = "family"
    chores = "chores"
    travel = "travel"
    misc = "misc"


class EmotionEnum(str, Enum):
    fine = "fine"
    happy = "happy"
    excited = "excited"
    sad = "sad"
    sensitive = "sensitive"
    anxious = "anxious"
    insecure = "insecure"
    angry = "angry"
    irritated = "irritated"
    neutral = "neutral"
    emotional = "emotional"


class EnergyEnum(str, Enum):
    tired = "tired"
    okay = "okay"
    energized = "energized"


class StressEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class SourceEnum(str, Enum):
    notification = "notification"
    manual = "manual"
    backfill = "backfill"


class CheckinBase(BaseModel):
    user_id: str
    ts_hour: datetime
    activity: ActivityEnum
    emotion: EmotionEnum
    energy: EnergyEnum
    stress: StressEnum
    note: str | None = Field(default=None, max_length=140)
    source: SourceEnum

    @field_validator("ts_hour")
    @classmethod
    def normalize_ts_hour(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.replace(minute=0, second=0, microsecond=0)

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
