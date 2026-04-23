import { useState, useEffect, useRef } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import {
  getCart, getMyCart, createCustomer, createOrder,
  registerUser, loginUser, getUserMe, mergeGuestCart,
  getCountries, getCities,
} from '../api'
import { useAuth } from '../AuthContext'
import CountryCodeSelect, { COUNTRY_CODES } from '../components/CountryCodeSelect'

const CART_KEY = 'iwear_cart_id'

/**
 * Optional sign-in prompt shown at the top of the checkout page.
 *
 * Guests can check out without an account; this card is purely optional
 * for returning customers who want their profile auto-filled and their
 * order tied to a saved account.
 */
function CheckoutSignInPrompt({ onAuthenticated }) {
  const [open, setOpen] = useState(false)
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('')
  const [countryCode, setCountryCode] = useState(COUNTRY_CODES[0].dial)
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleRegister = async (e) => {
    e.preventDefault()
    setError('')
    if (!phone.trim()) { setError('Phone number is required'); return }
    if (password.length < 6) { setError('Password must be at least 6 characters'); return }
    if (password !== confirm) { setError('Passwords do not match'); return }
    setLoading(true)
    try {
      const fullPhone = countryCode + phone.trim()
      await registerUser(email.trim(), password, fullPhone)
      await loginUser(email.trim(), password)
      const me = await getUserMe()
      onAuthenticated(me)
    } catch (err) {
      setError(err.message || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await loginUser(email.trim(), password)
      const me = await getUserMe()
      onAuthenticated(me)
    } catch (err) {
      setError(err.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  if (!open) {
    return (
      <div className="card" style={{ padding: '1rem 1.25rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.75rem', flexWrap: 'wrap' }}>
        <div>
          <strong style={{ display: 'block', fontSize: '0.96rem' }}>Checking out as a guest</strong>
          <span style={{ color: 'var(--color-text-muted)', fontSize: '0.86rem' }}>
            No account needed. Have one? Sign in to auto-fill your details.
          </span>
        </div>
        <button
          type="button"
          className="btn btn-secondary"
          style={{ fontSize: '0.86rem', padding: '0.5rem 0.9rem' }}
          onClick={() => setOpen(true)}
        >
          Sign in (optional)
        </button>
      </div>
    )
  }

  return (
    <div className="card" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
        <h2 style={{ fontSize: '1.1rem', margin: 0 }}>
          {mode === 'register' ? 'Create an account' : 'Sign in'}
        </h2>
        <button
          type="button"
          onClick={() => setOpen(false)}
          style={{ background: 'none', border: 'none', color: 'var(--color-text-muted)', cursor: 'pointer', fontSize: '0.84rem' }}
        >
          ✕ Continue as guest
        </button>
      </div>
      <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.25rem', fontSize: '0.88rem' }}>
        Optional — you can also check out as a guest without an account.
      </p>

      {error && <p className="form-error" style={{ marginBottom: '1rem' }}>{error}</p>}

      {mode === 'register' ? (
        <form onSubmit={handleRegister}>
          <div className="form-group">
            <label>Email *</label>
            <input
              type="email" value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="you@example.com" required autoComplete="email"
            />
          </div>
          <div className="form-group">
            <label>Phone number *</label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <CountryCodeSelect value={countryCode} onChange={setCountryCode} />
              <input
                type="tel" value={phone}
                onChange={e => setPhone(e.target.value)}
                placeholder="3001234567" required
                autoComplete="tel-national" style={{ flex: 1 }}
              />
            </div>
          </div>
          <div className="form-group">
            <label>Password *</label>
            <input
              type="password" value={password}
              onChange={e => setPassword(e.target.value)}
              required autoComplete="new-password" minLength={6}
            />
          </div>
          <div className="form-group">
            <label>Confirm password *</label>
            <input
              type="password" value={confirm}
              onChange={e => setConfirm(e.target.value)}
              required autoComplete="new-password"
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
            {loading ? 'Creating account...' : 'Create account & continue'}
          </button>
        </form>
      ) : (
        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email" value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="you@example.com" required autoComplete="email"
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input
              type="password" value={password}
              onChange={e => setPassword(e.target.value)}
              required autoComplete="current-password"
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
            {loading ? 'Signing in...' : 'Sign in & continue'}
          </button>
        </form>
      )}

      <p style={{ marginTop: '1rem', fontSize: '0.9rem', textAlign: 'center' }}>
        {mode === 'register' ? (
          <>Already have an account? <button type="button" onClick={() => { setMode('login'); setError('') }} style={{ background: 'none', border: 'none', color: 'var(--color-accent)', cursor: 'pointer', padding: 0, textDecoration: 'underline', fontSize: 'inherit' }}>Sign in</button></>
        ) : (
          <>Don&apos;t have an account? <button type="button" onClick={() => { setMode('register'); setError('') }} style={{ background: 'none', border: 'none', color: 'var(--color-accent)', cursor: 'pointer', padding: 0, textDecoration: 'underline', fontSize: 'inherit' }}>Create one</button></>
        )}
      </p>
    </div>
  )
}


export default function Checkout() {
  const navigate = useNavigate()
  const { user, setLoggedIn, refreshCart } = useAuth()
  const [cart, setCart] = useState(null)
  const [cartId, setCartId] = useState(null)
  const [customerId, setCustomerId] = useState(null)
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    email: '',
    address_line_1: '',
    country_id: '',
    city_id: '',
  })
  const [countries, setCountries] = useState([])
  const [cities, setCities] = useState([])
  const [placing, setPlacing] = useState(false)
  const [error, setError] = useState('')
  const [merging, setMerging] = useState(false)
  const mergingRef = useRef(false)

  const loadCart = async () => {
    if (user) {
      try {
        const c = await getMyCart()
        setCart(c)
        setCartId(c.id)
      } catch {
        setCart({ items: [] })
      }
    } else {
      const id = parseInt(localStorage.getItem(CART_KEY), 10)
      setCartId(id)
      if (id) {
        try { setCart(await getCart(id)) } catch { setCart({ items: [] }) }
      } else {
        setCart({ items: [] })
      }
    }
  }

  useEffect(() => {
    if (!mergingRef.current) loadCart()
    if (user) {
      setForm(f => ({
        ...f,
        first_name: f.first_name || user.first_name || '',
        last_name: f.last_name || user.last_name || '',
        email: f.email || user.email || '',
        phone: f.phone || user.phone || '',
        address_line_1: f.address_line_1 || user.shipping_address || '',
        country_id: f.country_id || (user.shipping_country_id ? String(user.shipping_country_id) : ''),
        city_id: f.city_id || (user.shipping_city_id ? String(user.shipping_city_id) : ''),
      }))
    }
  }, [user])

  useEffect(() => {
    getCountries().then(data => setCountries(data || []))
  }, [])

  useEffect(() => {
    if (form.country_id) {
      getCities(form.country_id).then(data => setCities(data || []))
    } else {
      setCities([])
    }
  }, [form.country_id])

  const handleAuthenticated = async (userData) => {
    mergingRef.current = true
    setMerging(true)
    setLoggedIn(userData)
    try {
      const guestId = parseInt(localStorage.getItem(CART_KEY), 10)
      if (guestId) {
        const merged = await mergeGuestCart(guestId)
        localStorage.removeItem(CART_KEY)
        setCart(merged)
        setCartId(merged.id)
      } else {
        const c = await getMyCart()
        setCart(c)
        setCartId(c.id)
      }
      refreshCart()
      setForm(f => ({
        ...f,
        first_name: f.first_name || userData.first_name || '',
        last_name: f.last_name || userData.last_name || '',
        email: f.email || userData.email || '',
        phone: f.phone || userData.phone || '',
        address_line_1: f.address_line_1 || userData.shipping_address || '',
        country_id: f.country_id || (userData.shipping_country_id ? String(userData.shipping_country_id) : ''),
        city_id: f.city_id || (userData.shipping_city_id ? String(userData.shipping_city_id) : ''),
      }))
    } catch {
      await loadCart()
    } finally {
      mergingRef.current = false
      setMerging(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (!cart?.items?.length) {
      setError('Your cart is empty.')
      return
    }
    if (!form.first_name?.trim() || !form.phone?.trim() || !form.address_line_1?.trim() || !form.country_id || !form.city_id) {
      setError('Please fill in all required fields.')
      return
    }
    setPlacing(true)
    const countryName = countries.find(c => c.id === Number(form.country_id))?.name || ''
    const cityName = cities.find(c => c.id === Number(form.city_id))?.name || ''
    try {
      let cid = customerId
      if (!cid) {
        const c = await createCustomer({
          first_name: form.first_name,
          last_name: form.last_name,
          phone: form.phone,
          email: form.email || undefined,
        })
        cid = c.id
        setCustomerId(cid)
      }
      const order = await createOrder(cartId, cid, {
        shipping_address: form.address_line_1,
        shipping_country_id: Number(form.country_id) || null,
        shipping_city_id: Number(form.city_id) || null,
        notes: form.address_line_1 + ', ' + cityName + ', ' + countryName,
      })
      localStorage.removeItem(CART_KEY)
      refreshCart()
      navigate(`/order-confirmation/${order.id}`)
    } catch (err) {
      setError(err.message || 'Failed to place order. Please try again.')
    } finally {
      setPlacing(false)
    }
  }

  if (!cart || merging) return <div className="loading">Loading...</div>

  if (!cart.items?.length) {
    return (
      <div className="empty-state">
        <p>Your cart is empty.</p>
        <Link to="/" className="btn btn-primary">Go to shop</Link>
      </div>
    )
  }

  return (
    <div style={{ maxWidth: 520 }}>
      <h1 className="page-title">Checkout</h1>
      <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>
        Cash on delivery &mdash; pay when your order arrives.
      </p>

      {/* Optional sign-in prompt for returning customers */}
      {!user && <CheckoutSignInPrompt onAuthenticated={handleAuthenticated} />}

      {/* Shipping details — shown for both guest and authenticated users */}
      {error && <p className="form-error" style={{ marginBottom: '1rem' }}>{error}</p>}

      <form onSubmit={handleSubmit} className="card" style={{ padding: '1.5rem' }}>
        <div className="form-group">
          <label>First name *</label>
          <input
            value={form.first_name}
            onChange={e => setForm(f => ({ ...f, first_name: e.target.value }))}
            required placeholder="Your first name"
          />
        </div>
        <div className="form-group">
          <label>Last name</label>
          <input
            value={form.last_name}
            onChange={e => setForm(f => ({ ...f, last_name: e.target.value }))}
            placeholder="Your last name"
          />
        </div>
        <div className="form-group">
          <label>Phone *</label>
          <input
            type="tel"
            value={form.phone}
            onChange={e => setForm(f => ({ ...f, phone: e.target.value }))}
            required placeholder="e.g. +92 300 1234567"
          />
        </div>
        <div className="form-group">
          <label>Email {user ? '' : '(optional)'}</label>
          <input
            type="email"
            value={form.email}
            onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
            placeholder="optional@example.com"
            readOnly={!!user}
            style={user ? { backgroundColor: 'var(--color-bg-muted, #f3f4f6)', cursor: 'not-allowed' } : undefined}
          />
        </div>
        <div className="form-group">
          <label>Address *</label>
          <input
            value={form.address_line_1}
            onChange={e => setForm(f => ({ ...f, address_line_1: e.target.value }))}
            required placeholder="Street, house number"
          />
        </div>
        <div className="form-group">
          <label>Country *</label>
          <select
            value={form.country_id}
            onChange={e => setForm(f => ({ ...f, country_id: e.target.value, city_id: '' }))}
            required
          >
            <option value="">Select country</option>
            {countries.map(c => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label>City *</label>
          <select
            value={form.city_id}
            onChange={e => setForm(f => ({ ...f, city_id: e.target.value }))}
            required
            disabled={!form.country_id}
          >
            <option value="">{form.country_id ? 'Select city' : 'Select a country first'}</option>
            {cities.map(c => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>
        <button type="submit" className="btn btn-primary" disabled={placing}>
          {placing ? 'Placing order...' : 'Place order (COD)'}
        </button>
      </form>
    </div>
  )
}
