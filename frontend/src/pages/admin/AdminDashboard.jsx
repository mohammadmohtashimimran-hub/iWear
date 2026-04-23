import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { listProductsAdmin, listOrdersAdmin, listCustomersAdmin } from '../../api'

function StatCard({ label, value, hint, icon, tone = '', to }) {
  return (
    <div className="stat-card">
      <div className={`stat-card-icon ${tone}`}>{icon}</div>
      <div className="stat-card-label">{label}</div>
      <div className="stat-card-value">{value}</div>
      {hint && <div className="stat-card-trend">{hint}</div>}
      {to && <Link to={to} style={{ fontSize: '0.85rem', marginTop: '0.6rem', display: 'inline-block' }}>View →</Link>}
    </div>
  )
}

export default function AdminDashboard() {
  const [stats, setStats] = useState({ products: 0, orders: 0, customers: 0, revenue: 0 })
  const [recent, setRecent] = useState([])

  useEffect(() => {
    listProductsAdmin({ per_page: 1 }).then(d => setStats(s => ({ ...s, products: d.total || 0 }))).catch(() => {})
    listOrdersAdmin().then(list => {
      const arr = Array.isArray(list) ? list : []
      const revenue = arr.reduce((sum, o) => sum + (Number(o.grand_total) || 0), 0)
      setStats(s => ({ ...s, orders: arr.length, revenue }))
      setRecent(arr.slice(0, 5))
    }).catch(() => {})
    listCustomersAdmin().then(list => setStats(s => ({ ...s, customers: (list && list.length) || 0 }))).catch(() => {})
  }, [])

  return (
    <div>
      <div className="stat-grid">
        <StatCard label="Products" value={stats.products} icon="◉" hint="Active catalog" to="/admin/products" />
        <StatCard label="Orders" value={stats.orders} icon="▤" tone="green" hint="All time" to="/admin/orders" />
        <StatCard label="Customers" value={stats.customers} icon="◍" tone="indigo" hint="Registered" to="/admin/customers" />
        <StatCard label="Revenue" value={`$${stats.revenue.toFixed(2)}`} icon="$" tone="amber" hint="Sum of orders" to="/admin/orders" />
      </div>

      <h2 className="section-title">Recent orders</h2>
      {recent.length === 0 ? (
        <div className="empty-state">
          <span className="empty-icon">▤</span>
          <p>No orders yet. Place a test order from the storefront to see it here.</p>
        </div>
      ) : (
        <table className="admin-table">
          <thead>
            <tr><th>Order #</th><th>Customer</th><th>Total</th><th>Status</th><th></th></tr>
          </thead>
          <tbody>
            {recent.map(o => (
              <tr key={o.id}>
                <td><Link to={`/admin/orders/${o.id}`}>{o.order_number || `#${o.id}`}</Link></td>
                <td>{o.customer_name || o.customer_email || '—'}</td>
                <td>${Number(o.grand_total || 0).toFixed(2)}</td>
                <td><span className={`admin-badge ${(o.status || 'pending').toLowerCase()}`}>{o.status || 'pending'}</span></td>
                <td><Link to={`/admin/orders/${o.id}`}>View</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <p style={{ color: 'var(--color-text-muted)', marginTop: '2rem' }}>
        Use the sidebar to manage products, run AI insights, and configure your store.
      </p>
    </div>
  )
}
