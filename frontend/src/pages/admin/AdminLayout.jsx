import { Link, NavLink, useNavigate, Outlet } from 'react-router-dom'
import { logoutAdmin, getMe } from '../../api'
import { useState, useEffect } from 'react'

const NAV = [
  { to: '/admin', label: 'Dashboard', end: true },
  { to: '/admin/products', label: 'Products' },
  { to: '/admin/addons', label: 'Addons' },
  { to: '/admin/customers', label: 'Customers' },
  { to: '/admin/orders', label: 'Orders' },
  { to: '/admin/order-statuses', label: 'Order Statuses' },
  { to: '/admin/catalog', label: 'Catalog Settings' },
  { to: '/admin/locations', label: 'Countries & Cities' },
  { to: '/admin/ai-insights', label: 'AI Insights' },
]

export default function AdminLayout() {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)

  useEffect(() => {
    getMe().then(setUser).catch(() => setUser(null))
  }, [])

  const handleLogout = () => {
    logoutAdmin()
    navigate('/admin/login', { replace: true })
  }

  return (
    <div className="admin-layout">
      <aside className="admin-sidebar">
        <Link to="/admin" className="brand">iWear Admin</Link>
        {NAV.map(n => (
          <NavLink key={n.to} to={n.to} end={n.end} className={({ isActive }) => isActive ? 'active' : ''}>
            {n.label}
          </NavLink>
        ))}
        <a href="/" target="_blank" rel="noopener noreferrer" style={{ marginTop: 'auto', opacity: 0.7 }}>View store →</a>
      </aside>
      <main className="admin-main">
        <div className="admin-header">
          <h1>Back office</h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            {user && <span style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>{user.email}</span>}
            <button type="button" className="btn btn-secondary" onClick={handleLogout}>Logout</button>
          </div>
        </div>
        <Outlet />
      </main>
    </div>
  )
}
