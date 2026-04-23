import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { registerUser, loginUser, getUserMe } from '../api'
import { useAuth } from '../AuthContext'
import CountryCodeSelect, { COUNTRY_CODES } from '../components/CountryCodeSelect'

export default function Register() {
  const navigate = useNavigate()
  const { setLoggedIn } = useAuth()
  const [email, setEmail] = useState('')
  const [countryCode, setCountryCode] = useState(COUNTRY_CODES[0].dial)
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (!phone.trim()) {
      setError('Phone number is required')
      return
    }
    if (password !== confirm) {
      setError('Passwords do not match')
      return
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }
    setLoading(true)
    try {
      const fullPhone = countryCode + phone.trim()
      await registerUser(email.trim(), password, fullPhone)
      await loginUser(email.trim(), password)
      const me = await getUserMe()
      setLoggedIn(me)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err.message || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 420, margin: '2rem auto' }}>
      <div className="card" style={{ padding: '2rem' }}>
        <h1 className="page-title" style={{ marginBottom: '0.25rem' }}>Create account</h1>
        <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>
          Sign up for an iWear account
        </p>
        {error && <p className="form-error" style={{ marginBottom: '1rem' }}>{error}</p>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email *</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              autoComplete="email"
            />
          </div>
          <div className="form-group">
            <label>Phone number *</label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <CountryCodeSelect value={countryCode} onChange={setCountryCode} />
              <input
                type="tel"
                value={phone}
                onChange={e => setPhone(e.target.value)}
                placeholder="3001234567"
                required
                autoComplete="tel-national"
                style={{ flex: 1 }}
              />
            </div>
          </div>
          <div className="form-group">
            <label>Password *</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              autoComplete="new-password"
              minLength={6}
            />
          </div>
          <div className="form-group">
            <label>Confirm password *</label>
            <input
              type="password"
              value={confirm}
              onChange={e => setConfirm(e.target.value)}
              required
              autoComplete="new-password"
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
            {loading ? 'Creating account...' : 'Create account'}
          </button>
        </form>
        <p style={{ marginTop: '1.25rem', fontSize: '0.9rem', textAlign: 'center' }}>
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
