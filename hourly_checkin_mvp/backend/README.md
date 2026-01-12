# API de Check-in horario (FastAPI)

API multiusuario con token por usuario y zona horaria configurable.

## Requisitos
- Python 3.11+

## Configuracion rapida
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Correr en desarrollo
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Variables de entorno
- `DB_URL`: por defecto `sqlite:///./hourly_checkin.db`
- `CORS_ALLOW_ORIGINS`: lista separada por comas o `*`

## Nota sobre UTC y zona horaria
- `ts_hour_utc` y `created_at` se guardan en UTC.
- La API responde `ts_hour_local` y `created_at_local` en la zona horaria del usuario.
- Si llega un datetime sin zona horaria, se asume la timezone del usuario para calcular la hora local.
- Si venis de una version anterior, borra `hourly_checkin.db` y recrea la base.

## Respuesta de checkins
- `ts_hour_utc` (UTC, Z) y `ts_hour_local` (offset local).
- `created_at_utc` y `created_at_local` para ver la hora local del usuario.

## Rutas
- `GET /health`
- `POST /users` (crear usuario + token)
- `GET /users/me`
- `PATCH /users/me`
- `POST /checkins` (upsert por `user_id` + `ts_hour_utc`)
- `GET /checkins?from=...&to=...&day=YYYY-MM-DD`
- `GET /checkins/current`

## Ejemplos con curl
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "marce",
    "timezone": "America/Argentina/Buenos_Aires"
  }'
```

```bash
curl -X POST http://localhost:8000/checkins \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "ts_hour": "2026-01-09T14:00:00-03:00",
    "activity": "trabajo",
    "emotion": "bien",
    "energy": "ok",
    "stress": "medio",
    "note": "Enfocado en tareas clave",
    "source": "notificacion"
  }'
```

```bash
curl "http://localhost:8000/checkins?from=2026-01-09T06:00:00-03:00&to=2026-01-09T23:00:00-03:00" \
  -H "Authorization: Bearer <TOKEN>"
```

```bash
curl "http://localhost:8000/checkins/current" \
  -H "Authorization: Bearer <TOKEN>"
```
