# Frontend de Check-in horario

## Requisitos
- Node.js 18+

## Configuracion
```bash
npm install
```

## Variables de entorno
Crear `.env.local` si necesitas cambiar la API:
```
VITE_API_BASE_URL=http://localhost:8000
```

## Desarrollo
```bash
npm run dev
```

## Flujo local rapido
1) Crear usuario en la API:
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"user_id":"marce","timezone":"America/Argentina/Buenos_Aires"}'
```

2) Abrir:
```
http://localhost:5173/checkin?user_id=marce&ts_hour=2026-01-09T14:00:00-03:00&token=<TOKEN>
```

La UI muestra siempre la hora local (rango tipo `15:00 – 16:00`) y distingue "Guardado" vs "Actualizado" cuando hay upsert en la misma hora.
