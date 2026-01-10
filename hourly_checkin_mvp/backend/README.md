# Hourly Check-in API (FastAPI)

## Requisitos
- Python 3.11+

## Setup rapido
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
- `API_TOKEN`: token unico para el MVP
- `CORS_ALLOW_ORIGINS`: lista separada por comas o `*`

## Endpoints
- `GET /health`
- `POST /checkins` (upsert por `user_id` + `ts_hour`)
- `GET /checkins?user_id=...&from=...&to=...`

## Ejemplos con curl
```bash
curl -X POST http://localhost:8000/checkins \
  -H "Authorization: Bearer changeme" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "marce",
    "ts_hour": "2026-01-09T14:00:00-03:00",
    "activity": "work",
    "emotion": "fine",
    "energy": "okay",
    "stress": "medium",
    "note": "Enfocado en tareas clave",
    "source": "notification"
  }'
```

```bash
curl "http://localhost:8000/checkins?user_id=marce&from=2026-01-09T06:00:00-03:00&to=2026-01-09T23:00:00-03:00" \
  -H "Authorization: Bearer changeme"
```
