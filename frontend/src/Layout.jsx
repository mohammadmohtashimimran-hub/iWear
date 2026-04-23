import { Link, NavLink, Outlet } from 'react-router-dom'
import { useAuth } from './AuthContext'
import { useCurrency } from './CurrencyContext'
import CartDrawer from './components/CartDrawer'

export default function Layout() {
  const { user, cartCount, logout, openDrawer } = useAuth()
  const { currency, setCurrency, currencies } = useCurrency()

  return (
    <>
      <header className="app-header">
        <div className="container">
          <Link to="/" className="brand">iWear</Link>
          <nav className="nav-links">
            <NavLink to="/" end>Shop</NavLink>
            <NavLink to="/size-guide">Size Guide</NavLink>
            <NavLink to="/orders">Orders</NavLink>
            <select
              value={currency}
              onChange={e => setCurrency(e.target.value)}
              aria-label="Currency"
              style={{
                background: 'var(--color-surface-alt, #f6f7fb)',
                border: '1px solid var(--color-border)',
                borderRadius: 6,
                padding: '0.35rem 0.5rem',
                fontSize: '0.82rem',
                fontWeight: 600,
                fontFamily: 'inherit',
                color: 'var(--color-text)',
                cursor: 'pointer',
              }}
            >
              {currencies.map(c => <option key={c.code} value={c.code}>{c.label}</option>)}
            </select>
            <button
              type="button"
              onClick={openDrawer}
              className="btn-ghost"
              style={{
                position: 'relative',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                fontFamily: 'inherit',
                fontSize: '0.93rem',
                fontWeight: 500,
                padding: '0.45rem 0.7rem',
                borderRadius: 8,
                color: 'inherit',
              }}
              aria-label="Open cart"
            >
              Cart
              {cartCount > 0 && (
                <span style={{
                  position: 'absolute',
                  top: 0,
                  right: -4,
                  background: 'var(--color-accent)',
                  color: '#fff',
                  fontSize: '0.66rem',
                  fontWeight: 700,
                  borderRadius: '999px',
                  minWidth: 18,
                  height: 18,
                  padding: '0 5px',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  lineHeight: 1,
                  boxShadow: '0 2px 8px -2px rgba(79,70,229,.45)',
                }}>{cartCount > 99 ? '99+' : cartCount}</span>
              )}
            </button>
            {user ? (
              <>
                <span style={{ fontSize: '0.84rem', color: 'var(--color-text-muted)' }}>{user.email}</span>
                <button
                  type="button"
                  onClick={logout}
                  className="btn btn-secondary"
                  style={{ padding: '0.45rem 0.9rem', fontSize: '0.85rem' }}
                >Sign out</button>
              </>
            ) : (
              <Link to="/login" className="btn btn-primary" style={{ padding: '0.5rem 1.1rem', fontSize: '0.88rem' }}>Sign in</Link>
            )}
          </nav>
        </div>
      </header>
      <main className="container"><Outlet /></main>
      <CartDrawer />
      <footer className="app-footer">
        <div className="footer-grid">
          <div>
            <div className="brand" style={{ color: '#fff', marginBottom: '0.85rem' }}>iWear</div>
            <p style={{ color: '#94a3b8', margin: '0 0 0.5rem', maxWidth: '24rem', fontSize: '0.88rem', lineHeight: 1.6 }}>
              Premium eyewear designed for everyday comfort. Browse frames, customise lenses, and order with cash-on-delivery.
            </p>
          </div>
          <div>
            <h4>Shop</h4>
            <ul>
              <li><Link to="/">All Products</Link></li>
              <li><Link to="/size-guide">Size Guide</Link></li>
              <li><Link to="/orders">My Orders</Link></li>
            </ul>
          </div>
          <div>
            <h4>Account</h4>
            <ul>
              <li><Link to="/login">Sign in</Link></li>
              <li><Link to="/register">Create account</Link></li>
            </ul>
          </div>
          <div>
            <h4>Support</h4>
            <ul>
              <li><a href="mailto:support@iwear.local">support@iwear.local</a></li>
              <li><a href="/admin">Admin Portal</a></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom container" style={{ textAlign: 'center' }}>
          <p style={{ margin: 0 }}>&copy; {new Date().getFullYear()} iWear. Eyewear that fits your style.</p>
        </div>
      </footer>
    </>
  )
}
