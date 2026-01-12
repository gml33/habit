import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { useLocation } from 'react-router-dom'
import { formatDateShort, formatHourRange, parseIsoToDate } from './utils/datetime'

type CheckinPayload = {
  ts_hour: string
  activity: string
  emotion: string
  energy: string
  stress: string
  note?: string
  source: string
}

type CheckinResponse = {
  id: number
  user_id: string
  ts_hour_local?: string
  ts_hour_utc?: string
  created_at_local?: string
}

const activityOptions = [
  'dormir',
  'trabajo',
  'pasatiempos',
  'ejercicio',
  'tiempo_libre',
  'pareja',
  'familia',
  'tareas',
  'viaje',
  'otros',
]

const emotionOptions = [
  'bien',
  'feliz',
  'entusiasmado',
  'triste',
  'sensible',
  'ansioso',
  'inseguro',
  'enojado',
  'irritable',
  'neutral',
  'emocional',
]

const energyOptions = ['cansado', 'ok', 'con_energia']
const stressOptions = ['bajo', 'medio', 'alto']

const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const activityLabels: Record<string, string> = {
  dormir: 'Dormir',
  trabajo: 'Trabajo',
  pasatiempos: 'Pasatiempos',
  ejercicio: 'Ejercicio',
  tiempo_libre: 'Tiempo libre',
  pareja: 'Pareja',
  familia: 'Familia',
  tareas: 'Tareas',
  viaje: 'Viaje',
  otros: 'Otros',
}

const emotionLabels: Record<string, string> = {
  bien: 'Bien',
  feliz: 'Feliz',
  entusiasmado: 'Entusiasmado',
  triste: 'Triste',
  sensible: 'Sensible',
  ansioso: 'Ansioso',
  inseguro: 'Inseguro',
  enojado: 'Enojado',
  irritable: 'Irritable',
  neutral: 'Neutral',
  emocional: 'Emocional',
}

const energyLabels: Record<string, string> = {
  cansado: 'Cansado',
  ok: 'OK',
  con_energia: 'Con energia',
}

const stressLabels: Record<string, string> = {
  bajo: 'Bajo',
  medio: 'Medio',
  alto: 'Alto',
}

const readErrorDetail = async (response: Response) => {
  const text = await response.text()
  if (!text) return 'Error inesperado'
  try {
    const data = JSON.parse(text) as { detail?: unknown }
    if (typeof data.detail === 'string') return data.detail
  } catch (err) {
    return text
  }
  return text
}

const submitCheckin = async (apiBaseUrl: string, token: string, payload: CheckinPayload) => {
  const response = await fetch(`${apiBaseUrl}/checkins`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const detail = await readErrorDetail(response)
    throw new Error(detail || 'Error al guardar')
  }

  return (await response.json()) as CheckinResponse
}

const buildMissingParamsMessage = (params: string[]) => {
  if (!params.length) return ''
  return `Faltan parametros en la URL: ${params.join(', ')}`
}

function CheckinPage() {
  const location = useLocation()
  const params = useMemo(() => new URLSearchParams(location.search), [location.search])
  const userId = (params.get('user_id') || '').trim()
  const token = (params.get('token') || '').trim()
  const tsHourParam = params.get('ts_hour')

  const [activity, setActivity] = useState(activityOptions[0])
  const [emotion, setEmotion] = useState(emotionOptions[0])
  const [energy, setEnergy] = useState(energyOptions[0])
  const [stress, setStress] = useState(stressOptions[0])
  const [note, setNote] = useState('')
  const [status, setStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle')
  const [error, setError] = useState<string | null>(null)
  const [savedCheckin, setSavedCheckin] = useState<CheckinResponse | null>(null)
  const [saveMessage, setSaveMessage] = useState<string | null>(null)

  useEffect(() => {
    setSavedCheckin(null)
    setSaveMessage(null)
    setStatus('idle')
  }, [tsHourParam])

  const missingParams = [
    ...(userId ? [] : ['user_id']),
    ...(token ? [] : ['token']),
    ...(tsHourParam ? [] : ['ts_hour']),
  ]

  const warningMessage = buildMissingParamsMessage(missingParams)
  const displayIso =
    savedCheckin?.ts_hour_local || tsHourParam || savedCheckin?.ts_hour_utc || null
  const displayDate = useMemo(() => parseIsoToDate(displayIso), [displayIso])
  const hasIso = Boolean(displayIso)
  const isHourValid = Boolean(displayDate)
  const dateLabel = displayDate ? formatDateShort(displayDate) : hasIso ? 'Hora invalida' : '—'
  const rangeLabel = displayDate ? formatHourRange(displayDate) : hasIso ? 'Hora invalida' : '—'

  const canSubmit = Boolean(userId && token && tsHourParam && isHourValid && status !== 'saving')

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (!canSubmit) {
      if (!userId || !token || !tsHourParam) {
        setError('Completa user_id, token y ts_hour en la URL.')
      } else if (!isHourValid) {
        setError('ts_hour invalido.')
      } else {
        setError('Completa los datos requeridos.')
      }
      setStatus('error')
      return
    }

    setError(null)
    setStatus('saving')
    setSaveMessage(null)

    const trimmedNote = note.trim()
    const payload: CheckinPayload = {
      ts_hour: tsHourParam!,
      activity,
      emotion,
      energy,
      stress,
      source: 'notificacion',
      ...(trimmedNote ? { note: trimmedNote } : {}),
    }

    try {
      const response = await submitCheckin(apiBase, token, payload)
      const message =
        savedCheckin && response.id === savedCheckin.id ? 'Actualizado ✅' : 'Guardado ✅'
      setSavedCheckin(response)
      setSaveMessage(message)
      setStatus('success')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error inesperado'
      setError(message)
      setStatus('error')
    }
  }

  return (
    <div className="app">
      <main className="card">
        <header className="header">
          <p className="eyebrow">Check-in horario</p>
          <h1>Check-in horario</h1>
          <p className="subtle">Completa en menos de 15 segundos.</p>
        </header>

        <section className="meta">
          <div>
            <span className="meta-label">Usuario</span>
            <strong>{userId || '—'}</strong>
          </div>
          <div>
            <span className="meta-label">Fecha</span>
            <strong>{dateLabel}</strong>
          </div>
          <div>
            <span className="meta-label">Hora</span>
            <strong>{rangeLabel}</strong>
          </div>
        </section>

        <p className="subtle">Hora local (UTC-3)</p>
        <p className="subtle">
          Un registro por hora. Si lo editas dentro de la misma hora, se actualiza.
        </p>

        {warningMessage ? <p className="warning">{warningMessage}</p> : null}

        {status === 'success' ? (
          <section className="success">
            <p className="success-text">{saveMessage || 'Guardado ✅'}</p>
            <button className="secondary" type="button" onClick={() => setStatus('idle')}>
              Editar
            </button>
          </section>
        ) : (
          <form className="form" onSubmit={handleSubmit}>
            <label>
              Actividad
              <select value={activity} onChange={(event) => setActivity(event.target.value)}>
                {activityOptions.map((option) => (
                  <option key={option} value={option}>
                    {activityLabels[option] ?? option}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Emocion
              <select value={emotion} onChange={(event) => setEmotion(event.target.value)}>
                {emotionOptions.map((option) => (
                  <option key={option} value={option}>
                    {emotionLabels[option] ?? option}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Energia
              <select value={energy} onChange={(event) => setEnergy(event.target.value)}>
                {energyOptions.map((option) => (
                  <option key={option} value={option}>
                    {energyLabels[option] ?? option}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Estres
              <select value={stress} onChange={(event) => setStress(event.target.value)}>
                {stressOptions.map((option) => (
                  <option key={option} value={option}>
                    {stressLabels[option] ?? option}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Nota (opcional)
              <textarea
                maxLength={140}
                rows={3}
                value={note}
                onChange={(event) => setNote(event.target.value)}
                placeholder="Algun detalle rapido..."
              />
              <span className="counter">{note.length}/140</span>
            </label>

            {error ? <p className="error">{error}</p> : null}

            <button type="submit" disabled={!canSubmit || status === 'saving'}>
              {status === 'saving' ? 'Guardando...' : 'Guardar'}
            </button>
          </form>
        )}
      </main>
    </div>
  )
}

export default CheckinPage
