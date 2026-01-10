# n8n - Check-in horario

## Importar workflow
1. Abri n8n.
2. Importa `workflows/hourly-checkin.json`.
3. Ajusta credenciales o reemplaza el nodo de envio segun tu canal (Telegram, Email, etc.).

## Variables de entorno usadas en el Function node
- `HOURLY_CHECKIN_USER_ID`: por defecto `marce`
- `HOURLY_CHECKIN_TOKEN`: token para el link
- `HOURLY_CHECKIN_FRONTEND`: URL base del frontend (ej. `https://tu-dominio.com`)

## Cron
El workflow corre cada hora en el minuto 0. Ajusta el nodo Cron si queres una ventana horaria distinta.

## Envio
El nodo `Send Message` viene configurado como HTTP Request a Telegram. Podes:
- Reemplazar por el nodo oficial de Telegram.
- Cambiar el endpoint por Email u otro servicio de mensajeria.
