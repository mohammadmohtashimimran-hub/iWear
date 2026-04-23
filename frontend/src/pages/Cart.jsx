import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { getCart, updateCartItem, removeCartItem, getMyCart, updateMyCartItem, removeMyCartItem } from '../api'
import { useAuth } from '../AuthContext'

const CART_KEY = 'iwear_cart_id'

export default function Cart() {
  const navigate = useNavigate()
  const { user, refreshCart } = useAuth()
  const [cart, setCart] = useState(null)
  const [loading, setLoading] = useState(true)
  const guestCartId = typeof window !== 'undefined' ? parseInt(localStorage.getItem(CART_KEY), 10) : null

  useEffect(() => {
    if (user) {
      getMyCart()
        .then(setCart)
        .catch(() => setCart({ items: [] }))
        .finally(() => setLoading(false))
    } else if (guestCartId) {
      getCart(guestCartId)
        .then(setCart)
        .catch(() => setCart({ items: [] }))
        .finally(() => setLoading(false))
    } else {
      setCart({ items: [] })
      setLoading(false)
    }
  }, [user, guestCartId])

  const updateQty = async (itemId, quantity) => {
    if (user) {
      if (quantity < 1) {
        const updated = await removeMyCartItem(itemId)
        setCart(updated)
      } else {
        const updated = await updateMyCartItem(itemId, quantity)
        setCart(updated)
      }
      refreshCart()
    } else {
      if (quantity < 1) {
        await removeCartItem(guestCartId, itemId)
        setCart(prev => ({ ...prev, items: prev.items.filter(i => i.id !== itemId) }))
      } else {
        await updateCartItem(guestCartId, itemId, quantity)
        setCart(prev => ({
          ...prev,
          items: prev.items.map(i => (i.id === itemId ? { ...i, quantity } : i)),
        }))
      }
    }
  }

  if (loading) return <div className="loading">Loading cart…</div>

  const total = cart?.items?.reduce((s, i) => s + (i.quantity * i.unit_price), 0) ?? 0

  return (
    <div>
      <h1 className="page-title">Cart</h1>

      {!cart?.items?.length ? (
        <div className="empty-state">
          <p>Your cart is empty.</p>
          <Link to="/" className="btn btn-primary">Browse products</Link>
        </div>
      ) : (
        <>
          <div className="card" style={{ overflow: 'hidden', marginBottom: '1.5rem' }}>
            <table className="cart-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>SKU</th>
                  <th>Qty</th>
                  <th>Price</th>
                  <th>Subtotal</th>
                </tr>
              </thead>
              <tbody>
                {cart.items.map(i => (
                  <tr key={i.id}>
                    <td>
                      {i.product_name}
                      {i.addons?.length > 0 && (
                        <div className="cart-item-addons">
                          {i.addons.map(a => (
                            <span key={a.id} className="cart-addon-tag">
                              {a.group_name}: {a.option_name}
                              {a.price > 0 && ` (+$${Number(a.price).toFixed(2)})`}
                            </span>
                          ))}
                        </div>
                      )}
                    </td>
                    <td style={{ color: 'var(--color-text-muted)' }}>{i.sku}</td>
                    <td>
                      <input
                        type="number"
                        min={0}
                        value={i.quantity}
                        onChange={e => updateQty(i.id, parseInt(e.target.value, 10) || 0)}
                      />
                    </td>
                    <td>${Number(i.unit_price).toFixed(2)}</td>
                    <td><strong>${(i.quantity * i.unit_price).toFixed(2)}</strong></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p style={{ fontSize: '1.15rem', marginBottom: '1rem' }}>
            <strong>Total: ${total.toFixed(2)}</strong>
          </p>
          <p style={{ color: 'var(--color-text-muted)', marginBottom: '1rem' }}>
            Pay when your order is delivered (Cash on Delivery).
          </p>
          <button type="button" className="btn btn-primary" onClick={() => navigate('/checkout')}>
            Proceed to checkout
          </button>
          <span style={{ marginLeft: '0.75rem' }}>
            <Link to="/">Continue shopping</Link>
          </span>
        </>
      )}
    </div>
  )
}
