import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getOrder, updateOrderStatusAdmin, getOrderStatuses } from '../../api'

export default function AdminOrderDetail() {
  const { id } = useParams()
  const [order, setOrder] = useState(null)
  const [statuses, setStatuses] = useState([])
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)

  useEffect(() => {
    Promise.all([getOrder(id), getOrderStatuses()])
      .then(([o, st]) => {
        setOrder(o)
        setStatuses(st || [])
      })
      .catch(() => setOrder(null))
      .finally(() => setLoading(false))
  }, [id])

  const handleStatusChange = async (newStatus) => {
    if (!order) return
    setUpdating(true)
    try {
      await updateOrderStatusAdmin(order.id, newStatus)
      setOrder(prev => ({ ...prev, status: newStatus }))
    } catch (e) {
      alert(e.message)
    } finally {
      setUpdating(false)
    }
  }

  if (loading) return <div className="loading">Loading order…</div>
  if (!order) return <p className="form-error">Order not found. <Link to="/admin/orders">Back to orders</Link></p>

  return (
    <div>
      <div className="admin-header">
        <h1>Order {order.order_number}</h1>
        <Link to="/admin/orders" className="btn btn-secondary">← Back to orders</Link>
      </div>
      <div className="card" style={{ padding: '1.5rem', marginBottom: '1rem' }}>
        <p><strong>Customer ID:</strong> {order.customer_id}</p>
        <p><strong>Subtotal:</strong> ${Number(order.subtotal).toFixed(2)}</p>
        <p><strong>Grand total:</strong> ${Number(order.grand_total).toFixed(2)}</p>
        <p><strong>Status:</strong> <span className={`admin-badge ${order.status || ''}`}>{order.status || '—'}</span></p>
        <p><strong>Notes:</strong> {order.notes || '—'}</p>
        <p><strong>Created:</strong> {order.created_at ? new Date(order.created_at).toLocaleString() : '—'}</p>
        <div className="form-group" style={{ marginTop: '1rem' }}>
          <label>Change status</label>
          <select
            value={order.status || ''}
            onChange={e => handleStatusChange(e.target.value)}
            disabled={updating}
            style={{ maxWidth: 200 }}
          >
            {statuses.map(s => <option key={s.id} value={s.code}>{s.name}</option>)}
          </select>
        </div>
      </div>
      <div className="card" style={{ padding: '1.5rem' }}>
        <h2 style={{ margin: '0 0 1rem', fontSize: '1.1rem' }}>Items</h2>
        <table className="admin-table">
          <thead>
            <tr>
              <th>Product</th>
              <th>SKU</th>
              <th>Qty</th>
              <th>Unit price</th>
              <th>Line total</th>
              <th>Stock remaining</th>
            </tr>
          </thead>
          <tbody>
            {(order.items || []).map((item, i) => (
              <tr key={i}>
                <td>{item.product_name || `Variant #${item.product_variant_id}`}</td>
                <td style={{ color: 'var(--color-text-muted)' }}>{item.sku || '—'}</td>
                <td>{item.quantity}</td>
                <td>${Number(item.unit_price).toFixed(2)}</td>
                <td>${Number(item.line_total).toFixed(2)}</td>
                <td>
                  <span style={{
                    fontWeight: 600,
                    color: item.stock_remaining === 0 ? '#dc2626' : item.stock_remaining != null && item.stock_remaining <= 5 ? '#d97706' : 'inherit',
                  }}>
                    {item.stock_remaining != null ? item.stock_remaining : '—'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
