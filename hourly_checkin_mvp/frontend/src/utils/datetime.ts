export const TZ_AR = 'America/Argentina/Cordoba'

const dateTimeFormatter = new Intl.DateTimeFormat('es-AR', {
  dateStyle: 'medium',
  timeStyle: 'short',
  timeZone: TZ_AR,
})

const hourFormatter = new Intl.DateTimeFormat('es-AR', {
  hour: '2-digit',
  minute: '2-digit',
  hour12: false,
  timeZone: TZ_AR,
})

export const formatDateTimeAR = (iso: string) => {
  const parsed = new Date(iso)
  if (Number.isNaN(parsed.getTime())) {
    return 'Hora invalida'
  }
  return dateTimeFormatter.format(parsed)
}

export const formatHourAR = (iso: string) => {
  const parsed = new Date(iso)
  if (Number.isNaN(parsed.getTime())) {
    return 'Hora invalida'
  }
  return hourFormatter.format(parsed)
}
