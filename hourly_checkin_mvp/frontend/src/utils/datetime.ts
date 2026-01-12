export const TZ_AR = 'America/Argentina/Buenos_Aires'

const dateFormatter = new Intl.DateTimeFormat('es-AR', {
  weekday: 'short',
  day: '2-digit',
  month: '2-digit',
  timeZone: TZ_AR,
})

const timeFormatter = new Intl.DateTimeFormat('es-AR', {
  hour: '2-digit',
  minute: '2-digit',
  hour12: false,
  timeZone: TZ_AR,
})

const hourFormatter = new Intl.DateTimeFormat('es-AR', {
  hour: '2-digit',
  hour12: false,
  timeZone: TZ_AR,
})

export const parseIsoToDate = (iso: string | null | undefined) => {
  if (!iso) return null
  const parsed = new Date(iso)
  return Number.isNaN(parsed.getTime()) ? null : parsed
}

export const formatTime = (date: Date | null) => {
  if (!date) return ''
  return timeFormatter.format(date)
}

export const formatDateShort = (date: Date | null) => {
  if (!date) return ''
  const label = dateFormatter.format(date).replace('.', '')
  return label ? `${label.charAt(0).toUpperCase()}${label.slice(1)}` : label
}

export const formatHourRange = (date: Date | null) => {
  if (!date) return ''
  const end = new Date(date.getTime() + 60 * 60 * 1000)
  const startHour = hourFormatter.format(date)
  const endHour = hourFormatter.format(end)
  return `${startHour}:00 – ${endHour}:00`
}
