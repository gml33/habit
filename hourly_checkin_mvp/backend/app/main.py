from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import init_db
from .routers.auth import router as auth_router
from .routers.checkins import router as checkins_router
from .settings import settings

app = FastAPI(title="Hourly Check-in API", version="0.1.0")

origins = settings.cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(checkins_router)
app.include_router(auth_router)
