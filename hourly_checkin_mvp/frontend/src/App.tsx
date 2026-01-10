import { useEffect, useMemo, useState } from 'react'

type CheckinPayload = {
  user_id: string
  ts_hour: string
  activity: string
  emotion: string
  energy: string
  stress: string
  note?: string | null
  source: string
}

type AuthPayload = {
  user_id: string
  password: string
}

const activityOptions = [
  'sleep',
  'work',
  'hobbies',
  'exercise',
  'leisure',
  'partner',
  'family',
  'chores',
  'travel',
  'misc',
]

const emotionOptions = [
  'fine',
  'happy',
  'excited',
  'sad',
  'sensitive',
  'anxious',
  'insecure',
  'angry',
  'irritated',
  'neutral',
  'emotional',
]

const energyOptions = ['tired', 'okay', 'energized']
const stressOptions = ['low', 'medium', 'high']

const normalizeToHour = (date: Date) => {
  const normalized = new Date(date)
  normalized.setMinutes(0, 0, 0)
  return normalized
}

const formatIsoWithOffset = (date: Date) => {
  const pad = (value: number) => String(value).padStart(2, '0')
  const tzOffset = -date.getTimezoneOffset()
  const sign = tzOffset >= 0 ? '+' : '-'
  const absOffset = Math.abs(tzOffset)
  const offsetHours = pad(Math.floor(absOffset / 60))
  const offsetMinutes = pad(absOffset % 60)

  return (
    `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}` +
    `T${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}` +
    `${sign}${offsetHours}:${offsetMinutes}`
  )
}

const formatHourLabel = (date: Date) => {
  if (Number.isNaN(date.getTime())) return '--:--'
  return date.toLocaleTimeString('es-AR', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
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

const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const userIdStorageKey = 'hourly_checkin_user_id'
const tokenStorageKey = 'hourly_checkin_token'

function App() {
  const params = useMemo(() => new URLSearchParams(window.location.search), [])
  const userIdParam = params.get('user_id') || ''
  const tsHourParam = params.get('ts_hour')
  const tokenParam = params.get('token') || ''

  const parsedTsHour = useMemo(() => {
    if (!tsHourParam) return normalizeToHour(new Date())
    const parsed = new Date(tsHourParam)
    return Number.isNaN(parsed.getTime()) ? normalizeToHour(new Date()) : parsed
  }, [tsHourParam])

  const tsHourValue = tsHourParam || formatIsoWithOffset(normalizeToHour(new Date()))

  const [userId, setUserId] = useState(() => {
    return localStorage.getItem(userIdStorageKey) || ''
  })
  const [token, setToken] = useState(() => {
    return tokenParam || localStorage.getItem(tokenStorageKey) || ''
  })
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login')
  const [loginUserId, setLoginUserId] = useState(userIdParam)
  const [loginPassword, setLoginPassword] = useState('')
  const [registerUserId, setRegisterUserId] = useState(userIdParam)
  const [registerPassword, setRegisterPassword] = useState('')
  const [registerConfirm, setRegisterConfirm] = useState('')
  const [authLoading, setAuthLoading] = useState(false)
  const [authError, setAuthError] = useState('')
  const [activity, setActivity] = useState(activityOptions[0])
  const [emotion, setEmotion] = useState(emotionOptions[0])
  const [energy, setEnergy] = useState(energyOptions[0])
  const [stress, setStress] = useState(stressOptions[0])
  const [note, setNote] = useState('')
  const [loading, setLoading] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!tokenParam) return
    setToken(tokenParam)
    localStorage.setItem(tokenStorageKey, tokenParam)
  }, [tokenParam])

  const canSubmit = Boolean(userId)
  const canLogin = Boolean(loginUserId.trim() && loginPassword)
  const canRegister = Boolean(
    registerUserId.trim() && registerPassword && registerPassword === registerConfirm,
  )

  const persistUserId = (value: string) => {
    setUserId(value)
    localStorage.setItem(userIdStorageKey, value)
  }

  const resetAuthErrors = () => {
    setAuthError('')
    setError('')
  }

  const handleLogout = () => {
    localStorage.removeItem(userIdStorageKey)
    setUserId('')
    setSaved(false)
    resetAuthErrors()
    setAuthMode('login')
    setLoginPassword('')
    setRegisterPassword('')
    setRegisterConfirm('')
  }

  const handleLogin = async (event: React.FormEvent) => {
    event.preventDefault()
    const candidate = loginUserId.trim()
    if (!candidate || !loginPassword) {
      setAuthError('Completa usuario y clave.')
      return
    }

    setAuthError('')
    setAuthLoading(true)

    const payload: AuthPayload = { user_id: candidate, password: loginPassword }

    try {
      const response = await fetch(`${apiBase}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const detail = await readErrorDetail(response)
        throw new Error(detail || 'Error al iniciar sesion')
      }

      const data = (await response.json()) as { user_id?: string }
      persistUserId(data.user_id || candidate)
      setLoginPassword('')
      setSaved(false)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error inesperado'
      setAuthError(message)
    } finally {
      setAuthLoading(false)
    }
  }

  const handleRegister = async (event: React.FormEvent) => {
    event.preventDefault()
    const candidate = registerUserId.trim()
    if (!candidate || !registerPassword) {
      setAuthError('Completa usuario y clave.')
      return
    }
    if (registerPassword !== registerConfirm) {
      setAuthError('Las claves no coinciden.')
      return
    }

    setAuthError('')
    setAuthLoading(true)

    const payload: AuthPayload = { user_id: candidate, password: registerPassword }

    try {
      const response = await fetch(`${apiBase}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const detail = await readErrorDetail(response)
        throw new Error(detail || 'Error al registrar')
      }

      const data = (await response.json()) as { user_id?: string }
      persistUserId(data.user_id || candidate)
      setRegisterPassword('')
      setRegisterConfirm('')
      setSaved(false)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error inesperado'
      setAuthError(message)
    } finally {
      setAuthLoading(false)
    }
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!canSubmit) {
      setError('Falta user_id. Inicia sesion o registrate para continuar.')
      return
    }

    setError('')
    setLoading(true)

    const payload: CheckinPayload = {
      user_id: userId,
      ts_hour: tsHourValue,
      activity,
      emotion,
      energy,
      stress,
      note: note.trim() ? note.trim() : null,
      source: 'notification',
    }

    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      }
      if (token) {
        headers.Authorization = `Bearer ${token}`
      }

      const url = token
        ? `${apiBase}/checkins?token=${encodeURIComponent(token)}`
        : `${apiBase}/checkins`

      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const detail = await readErrorDetail(response)
        throw new Error(detail || 'Error al guardar')
      }

      setSaved(true)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error inesperado'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <main className="card">
        <header className="header">
          <p className="eyebrow">Hourly Check-in</p>
          <h1>
            {userId
              ? `Check-in ${formatHourLabel(parsedTsHour)}`
              : authMode === 'login'
                ? 'Iniciar sesion'
                : 'Crear cuenta'}
          </h1>
          <p className="subtle">
            {userId
              ? 'Completa en menos de 15 segundos.'
              : 'Accede con tu usuario para cargar tu check-in.'}
          </p>
        </header>

        {userId ? (
          <>
            <div className="user-bar">
              <span>Usuario: {userId}</span>
              <button className="secondary small" type="button" onClick={handleLogout}>
                Cambiar
              </button>
            </div>

            {saved ? (
              <section className="success">
                <p className="success-text">Listo ✅</p>
                <button className="secondary" type="button" onClick={() => setSaved(false)}>
                  Editar
                </button>
              </section>
            ) : (
              <form className="form" onSubmit={handleSubmit}>
                <label>
                  Activity
                  <select value={activity} onChange={(event) => setActivity(event.target.value)}>
                    {activityOptions.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Emotion
                  <select value={emotion} onChange={(event) => setEmotion(event.target.value)}>
                    {emotionOptions.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Energy
                  <select value={energy} onChange={(event) => setEnergy(event.target.value)}>
                    {energyOptions.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Stress
                  <select value={stress} onChange={(event) => setStress(event.target.value)}>
                    {stressOptions.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Note (opcional)
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

                <button type="submit" disabled={!canSubmit || loading}>
                  {loading ? 'Guardando...' : 'Guardar'}
                </button>
              </form>
            )}
          </>
        ) : authMode === 'login' ? (
          <>
            <form className="form" onSubmit={handleLogin}>
              <label>
                Usuario
                <input
                  type="text"
                  value={loginUserId}
                  onChange={(event) => setLoginUserId(event.target.value)}
                  placeholder="tu_usuario"
                  autoComplete="username"
                />
              </label>

              <label>
                Clave
                <input
                  type="password"
                  value={loginPassword}
                  onChange={(event) => setLoginPassword(event.target.value)}
                  placeholder="Tu clave"
                  autoComplete="current-password"
                />
              </label>

              {authError ? <p className="error">{authError}</p> : null}

              <button type="submit" disabled={!canLogin || authLoading}>
                {authLoading ? 'Ingresando...' : 'Ingresar'}
              </button>
            </form>

            <p className="warning">
              No tenes cuenta?{' '}
              <button
                className="link"
                type="button"
                onClick={() => {
                  setAuthMode('register')
                  resetAuthErrors()
                }}
              >
                Registrate
              </button>
            </p>
          </>
        ) : (
          <>
            <form className="form" onSubmit={handleRegister}>
              <label>
                Usuario
                <input
                  type="text"
                  value={registerUserId}
                  onChange={(event) => setRegisterUserId(event.target.value)}
                  placeholder="tu_usuario"
                  autoComplete="username"
                />
              </label>

              <label>
                Clave
                <input
                  type="password"
                  value={registerPassword}
                  onChange={(event) => setRegisterPassword(event.target.value)}
                  placeholder="Minimo 6 caracteres"
                  autoComplete="new-password"
                />
              </label>

              <label>
                Repetir clave
                <input
                  type="password"
                  value={registerConfirm}
                  onChange={(event) => setRegisterConfirm(event.target.value)}
                  placeholder="Repeti la clave"
                  autoComplete="new-password"
                />
              </label>

              {authError ? <p className="error">{authError}</p> : null}

              <button type="submit" disabled={!canRegister || authLoading}>
                {authLoading ? 'Creando...' : 'Crear cuenta'}
              </button>
            </form>

            <p className="warning">
              Ya tenes cuenta?{' '}
              <button
                className="link"
                type="button"
                onClick={() => {
                  setAuthMode('login')
                  resetAuthErrors()
                }}
              >
                Inicia sesion
              </button>
            </p>
          </>
        )}
      </main>
    </div>
  )
}

export default App
