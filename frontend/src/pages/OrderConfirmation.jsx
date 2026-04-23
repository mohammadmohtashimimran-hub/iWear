import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getOrder } from '../api'

const STATUS_COLORS = {
  pending:    { bg: '#fef3c7', color: '#92400e' },
  confirmed:  { bg: '#d1fae5', color: '#065f46' },
  processing: { bg: '#dbeafe', color: '#1e40af' },
  shipped:    { bg: '#e0e7ff', color: '#3730a3' },
  delivered:  { bg: '#d1fae5', color: '#047857' },
  cancelled:  { bg: '#fee2e2', color: '#991b1b' },
}

function StatusBadge({ code, name }) {
  const c = STATUS_COLORS[code] || { bg: 'var(--color-bg)', color: 'var(--color-text)' }
  return (
    <span style={{
      fontSize: '0.85rem', fontWeight: 600, padding: '0.25rem 0.75rem',
      borderRadius: 'var(--radius-sm, 4px)', background: c.bg, color: c.color,
      textTransform: 'capitalize',
    }}>
      {name || code || '—'}
    </span>
  )
}

export default function OrderConfirmation() {
  const { orderId } = useParams()
  const [order, setOrder] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getOrder(orderId)
      .then(setOrder)
      .catch(() => setError('Order not found.'))
  }, [orderId])

  if (error) {
    return (
      <div className="empty-state">
        <p>{error}</p>
        <Link to="/">Back to shop</Link>
      </div>
    )
  }

  if (!order) return <div className="loading">Loading order…</div>

  const shippingParts = [order.shipping_address, order.shipping_city, order.shipping_country].filter(Boolean)
  const shippingText = shippingParts.length ? shippingParts.join(', ') : order.notes || '—'

  return (
    <div style={{ maxWidth: 680, margin: '0 auto' }}>
      <div className="order-success">
        <h2>Thank you for your order!</h2>
        <p style={{ margin: 0 }}>
          Order <strong>#{order.order_number}</strong> has been placed successfully.
        </p>
      </div>

      {/* Status + summary */}
      <div className="card" style={{ padding: '1.5rem', marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div>
            <span style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>Order placed</span>
            <div style={{ fontWeight: 500 }}>
              {order.created_at ? new Date(order.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) : '—'}
            </div>
          </div>
          <StatusBadge code={order.status} name={order.status_name} />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.92rem' }}>
          {order.customer_name && (
            <div>
              <span style={{ color: 'var(--color-text-muted)', fontSize: '0.82rem' }}>Customer</span>
              <div>{order.customer_name}</div>
            </div>
          )}
          {order.customer_phone && (
            <div>
              <span style={{ color: 'var(--color-text-muted)', fontSize: '0.82rem' }}>Phone</span>
              <div>{order.customer_phone}</div>
            </div>
          )}
          {order.customer_email && (
            <div>
              <span style={{ color: 'var(--color-text-muted)', fontSize: '0.82rem' }}>Email</span>
              <div>{order.customer_email}</div>
            </div>
          )}
          <div>
            <span style={{ color: 'var(--color-text-muted)', fontSize: '0.82rem' }}>Shipping address</span>
            <div>{shippingText}</div>
          </div>
          <div>
            <span style={{ color: 'var(--color-text-muted)', fontSize: '0.82rem' }}>Payment</span>
            <div>Cash on Delivery</div>
          </div>
        </div>
      </div>

      {/* Order items */}
      <div className="card" style={{ padding: '1.5rem', marginBottom: '1.25rem' }}>
        <h3 style={{ fontSize: '1.05rem', marginBottom: '1rem' }}>
          Items ({order.items?.length || 0})
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {order.items?.map((item, idx) => (
            <div key={idx} style={{
              display: 'flex', gap: '1rem', alignItems: 'center',
              paddingBottom: idx < order.items.length - 1 ? '1rem' : 0,
              borderBottom: idx < order.items.length - 1 ? '1px solid var(--color-border, #e5e7eb)' : 'none',
            }}>
              {item.image_url ? (
                <img
                  src={item.image_url}
                  alt={item.product_name}
                  style={{ width: 64, height: 64, objectFit: 'cover', borderRadius: 'var(--radius-sm, 4px)', flexShrink: 0, background: '#f3f4f6' }}
                />
              ) : (
                <div style={{
                  width: 64, height: 64, borderRadius: 'var(--radius-sm, 4px)', flexShrink: 0,
                  background: '#f3f4f6', display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: '#9ca3af', fontSize: '0.75rem',
                }}>No img</div>
              )}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontWeight: 600, marginBottom: '0.15rem' }}>
                  {item.product_slug ? (
                    <Link to={`/product/${item.product_slug}`} style={{ color: 'inherit', textDecoration: 'none' }}>
                      {item.product_name}
                    </Link>
                  ) : item.product_name}
                </div>
                {item.variant_name && (
                  <div style={{ fontSize: '0.82rem', color: 'var(--color-text-muted)' }}>
                    {item.variant_name}
                  </div>
                )}
                <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>
                  Qty: {item.quantity} &times; ${item.unit_price.toFixed(2)}
                </div>
              </div>
              <div style={{ fontWeight: 600, whiteSpace: 'nowrap' }}>
                ${item.line_total.toFixed(2)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Order total */}
      <div className="card" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.92rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--color-text-muted)' }}>Subtotal</span>
            <span>${Number(order.subtotal).toFixed(2)}</span>
          </div>
          {Number(order.discount_total) > 0 && (
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--color-text-muted)' }}>Discount</span>
              <span>-${Number(order.discount_total).toFixed(2)}</span>
            </div>
          )}
          {Number(order.tax_total) > 0 && (
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--color-text-muted)' }}>Tax</span>
              <span>${Number(order.tax_total).toFixed(2)}</span>
            </div>
          )}
          <div style={{
            display: 'flex', justifyContent: 'space-between',
            fontWeight: 700, fontSize: '1.1rem', borderTop: '1px solid var(--color-border, #e5e7eb)',
            paddingTop: '0.5rem', marginTop: '0.25rem',
          }}>
            <span>Total</span>
            <span>${Number(order.grand_total).toFixed(2)}</span>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '0.75rem' }}>
        <Link to="/" className="btn btn-primary">Continue shopping</Link>
        <Link to="/orders" className="btn btn-secondary">My orders</Link>
      </div>
    </div>
  )
}
