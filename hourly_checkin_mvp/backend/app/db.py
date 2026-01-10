from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .settings import settings


def _connect_args() -> dict:
    if settings.db_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


engine = create_engine(settings.db_url, connect_args=_connect_args())
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
