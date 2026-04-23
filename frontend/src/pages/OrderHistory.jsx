import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getMyOrders } from '../api'
import { useAuth } from '../AuthContext'

const STATUS_COLORS = {
  pending:   { bg: '#fef3c7', color: '#92400e' },
  confirmed: { bg: '#d1fae5', color: '#065f46' },
  processing:{ bg: '#dbeafe', color: '#1e40af' },
  shipped:   { bg: '#e0e7ff', color: '#3730a3' },
  delivered: { bg: '#d1fae5', color: '#047857' },
  cancelled: { bg: '#fee2e2', color: '#991b1b' },
}

function StatusBadge({ code, name }) {
  const c = STATUS_COLORS[code] || { bg: 'var(--color-bg)', color: 'var(--color-text)' }
  return (
    <span style={{
      fontSize: '0.82rem', fontWeight: 600, padding: '0.2rem 0.6rem',
      borderRadius: 'var(--radius-sm)', background: c.bg, color: c.color,
      textTransform: 'capitalize',
    }}>
      {name || code || '—'}
    </span>
  )
}

export default function OrderHistory() {
  const { user } = useAuth()
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!user) {
      setLoading(false)
      return
    }
    getMyOrders()
      .then(data => setOrders(Array.isArray(data) ? data : []))
      .catch(() => setError('Could not load orders.'))
      .finally(() => setLoading(false))
  }, [user])

  if (!user) {
    return (
      <div className="empty-state">
        <p>Please sign in to view your orders.</p>
        <Link to="/login" className="btn btn-primary">Sign in</Link>
      </div>
    )
  }

  if (loading) return <div className="loading">Loading orders…</div>
  if (error) return <p className="form-error">{error}</p>

  return (
    <div>
      <h1 className="page-title">My Orders</h1>

      {orders.length === 0 ? (
        <div className="empty-state">
          <p>You haven&apos;t placed any orders yet.</p>
          <Link to="/" className="btn btn-primary">Browse products</Link>
        </div>
      ) : (
        <div className="card" style={{ overflow: 'hidden' }}>
          <table className="cart-table" style={{ width: '100%' }}>
            <thead>
              <tr>
                <th>Order #</th>
                <th>Date</th>
                <th>Items</th>
                <th>Total</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {orders.map(o => (
                <tr key={o.id}>
                  <td>
                    <Link to={`/order-confirmation/${o.id}`} style={{ fontWeight: 600 }}>
                      {o.order_number}
                    </Link>
                  </td>
                  <td style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>
                    {o.created_at ? new Date(o.created_at).toLocaleDateString() : '—'}
                  </td>
                  <td>{o.items_count ?? '—'}</td>
                  <td style={{ fontWeight: 600 }}>${Number(o.grand_total).toFixed(2)}</td>
                  <td><StatusBadge code={o.status} name={o.status_name} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
