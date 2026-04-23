import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { loginUser, getUserMe } from '../api'
import { useAuth } from '../AuthContext'

export default function Login() {
  const navigate = useNavigate()
  const { setLoggedIn } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await loginUser(email.trim(), password)
      const me = await getUserMe()
      setLoggedIn(me)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 420, margin: '2rem auto' }}>
      <div className="card" style={{ padding: '2rem' }}>
        <h1 className="page-title" style={{ marginBottom: '0.25rem' }}>Sign in</h1>
        <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>
          Log in to your iWear account
        </p>
        {error && <p className="form-error" style={{ marginBottom: '1rem' }}>{error}</p>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
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
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
        <p style={{ marginTop: '1.25rem', fontSize: '0.9rem', textAlign: 'center' }}>
          Don't have an account? <Link to="/register">Create one</Link>
        </p>
      </div>
    </div>
  )
}
