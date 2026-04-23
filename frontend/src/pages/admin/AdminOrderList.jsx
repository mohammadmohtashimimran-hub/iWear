import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { listOrdersAdmin, getOrder, updateOrderStatusAdmin, getOrderStatuses } from '../../api'

export default function AdminOrderList() {
  const [orders, setOrders] = useState([])
  const [statuses, setStatuses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [updating, setUpdating] = useState(null)

  useEffect(() => {
    Promise.all([listOrdersAdmin(), getOrderStatuses()])
      .then(([list, st]) => {
        setOrders(Array.isArray(list) ? list : [])
        setStatuses(st || [])
      })
      .catch(() => setError('Failed to load orders'))
      .finally(() => setLoading(false))
  }, [])

  const handleStatusChange = async (orderId, newStatus) => {
    setUpdating(orderId)
    try {
      await updateOrderStatusAdmin(orderId, newStatus)
      setOrders(prev => prev.map(o => o.id === orderId ? { ...o, status: newStatus } : o))
    } catch (e) {
      alert(e.message)
    } finally {
      setUpdating(null)
    }
  }

  if (loading) return <div className="loading">Loading orders…</div>
  if (error) return <p className="form-error">{error}</p>

  return (
    <div>
      <div className="admin-header">
        <h1>Orders</h1>
      </div>
      <div className="card" style={{ overflow: 'hidden' }}>
        <table className="admin-table">
          <thead>
            <tr>
              <th>Order #</th>
              <th>Customer ID</th>
              <th>Total</th>
              <th>Status</th>
              <th>Date</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {orders.length === 0 ? (
              <tr><td colSpan={6} style={{ color: 'var(--color-text-muted)' }}>No orders yet.</td></tr>
            ) : (
              orders.map(o => (
                <tr key={o.id}>
                  <td><Link to={`/admin/orders/${o.id}`}>{o.order_number}</Link></td>
                  <td>{o.customer_id}</td>
                  <td>${Number(o.grand_total).toFixed(2)}</td>
                  <td>
                    <span className={`admin-badge ${o.status || ''}`}>{o.status || '—'}</span>
                  </td>
                  <td>{o.created_at ? new Date(o.created_at).toLocaleDateString() : '—'}</td>
                  <td>
                    <select
                      value={o.status || ''}
                      onChange={e => handleStatusChange(o.id, e.target.value)}
                      disabled={updating === o.id}
                      style={{ padding: '0.35rem', fontSize: '0.9rem' }}
                    >
                      {statuses.map(s => <option key={s.id} value={s.code}>{s.name}</option>)}
                    </select>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
