# Desarrollo con Docker

## Levantar servicios
```bash
docker compose up --build
```

## Verificaciones rapidas
```bash
curl http://localhost:8000/health
```

Crear usuario y obtener token:
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"user_id":"marce","timezone":"America/Argentina/Buenos_Aires"}'
```

Abrir en el navegador:
```
http://localhost:5173/checkin?user_id=marce&token=<TOKEN>&ts_hour=2026-01-10T15:00:00-03:00
```

## Notas
- La base SQLite se persiste en `backend/hourly_checkin.db`.
- Si cambiaste el esquema, borra ese archivo y levanta de nuevo.
- El frontend se compila con `VITE_API_BASE_URL=http://localhost:8000` (MVP). Para mejorar luego, se puede usar proxy en nginx.
