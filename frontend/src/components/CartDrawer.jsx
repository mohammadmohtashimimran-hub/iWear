import { useEffect, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'
import { useCurrency } from '../CurrencyContext'
import {
  getCart,
  updateCartItem,
  removeCartItem,
  updateMyCartItem,
  removeMyCartItem,
} from '../api'

const CART_KEY = 'iwear_cart_id'

export default function CartDrawer() {
  const navigate = useNavigate()
  const {
    user,
    drawerOpen,
    closeDrawer,
    drawerCart,
    setDrawerCart,
    refreshCart,
  } = useAuth()
  const { formatPrice } = useCurrency()
  const overlayRef = useRef(null)

  useEffect(() => {
    if (drawerOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => { document.body.style.overflow = '' }
  }, [drawerOpen])

  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === 'Escape' && drawerOpen) closeDrawer()
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [drawerOpen, closeDrawer])

  const updateQty = async (itemId, quantity) => {
    try {
      if (user) {
        if (quantity < 1) {
          const updated = await removeMyCartItem(itemId)
          setDrawerCart(updated)
        } else {
          const updated = await updateMyCartItem(itemId, quantity)
          setDrawerCart(updated)
        }
        refreshCart()
      } else {
        const guestCartId = parseInt(localStorage.getItem(CART_KEY), 10)
        if (!guestCartId) return
        if (quantity < 1) {
          await removeCartItem(guestCartId, itemId)
          setDrawerCart(prev => ({
            ...prev,
            items: prev.items.filter(i => i.id !== itemId),
          }))
        } else {
          await updateCartItem(guestCartId, itemId, quantity)
          setDrawerCart(prev => ({
            ...prev,
            items: prev.items.map(i =>
              i.id === itemId ? { ...i, quantity } : i,
            ),
          }))
        }
      }
    } catch {
      /* silently ignore */
    }
  }

  const items = drawerCart?.items || []
  const total = items.reduce((s, i) => s + i.quantity * i.unit_price, 0)
  const itemCount = items.reduce((s, i) => s + i.quantity, 0)

  return (
    <>
      {/* Overlay */}
      <div
        ref={overlayRef}
        className={`drawer-overlay${drawerOpen ? ' open' : ''}`}
        onClick={closeDrawer}
      />

      {/* Drawer panel */}
      <aside className={`cart-drawer${drawerOpen ? ' open' : ''}`}>
        {/* Header */}
        <div className="cart-drawer-header">
          <h2>
            Your Cart
            {itemCount > 0 && (
              <span className="cart-drawer-badge">{itemCount}</span>
            )}
          </h2>
          <button
            type="button"
            className="cart-drawer-close"
            onClick={closeDrawer}
            aria-label="Close cart"
          >
            &times;
          </button>
        </div>

        {/* Body */}
        <div className="cart-drawer-body">
          {items.length === 0 ? (
            <div className="cart-drawer-empty">
              <span className="cart-drawer-empty-icon">&#128722;</span>
              <p>Your cart is empty</p>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => { closeDrawer(); navigate('/') }}
              >
                Browse products
              </button>
            </div>
          ) : (
            <ul className="cart-drawer-items">
              {items.map(item => (
                <li key={item.id} className="cart-drawer-item">
                  <div className="cart-drawer-item-info">
                    <span className="cart-drawer-item-name">
                      {item.product_name || 'Product'}
                    </span>
                    {item.sku && (
                      <span className="cart-drawer-item-sku">{item.sku}</span>
                    )}
                    {item.addons?.length > 0 && (
                      <div className="cart-drawer-item-addons">
                        {item.addons.map(a => (
                          <span key={a.id} className="cart-drawer-addon-tag">
                            {a.group_name}: {a.option_name}
                            {a.price > 0 && ` (+${formatPrice(a.price, a.price)})`}
                          </span>
                        ))}
                      </div>
                    )}
                    <span className="cart-drawer-item-price">
                      {formatPrice(item.unit_price, item.unit_price)}
                    </span>
                  </div>
                  <div className="cart-drawer-item-actions">
                    <div className="cart-drawer-qty">
                      <button
                        type="button"
                        onClick={() => updateQty(item.id, item.quantity - 1)}
                        aria-label="Decrease quantity"
                      >
                        &#8722;
                      </button>
                      <span>{item.quantity}</span>
                      <button
                        type="button"
                        onClick={() => updateQty(item.id, item.quantity + 1)}
                        aria-label="Increase quantity"
                      >
                        +
                      </button>
                    </div>
                    <span className="cart-drawer-item-subtotal">
                      {formatPrice(item.quantity * item.unit_price, item.quantity * item.unit_price)}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Footer */}
        {items.length > 0 && (
          <div className="cart-drawer-footer">
            <div className="cart-drawer-total">
              <span>Subtotal</span>
              <span>{formatPrice(total, total)}</span>
            </div>
            <button
              type="button"
              className="btn btn-primary cart-drawer-checkout-btn"
              onClick={() => { closeDrawer(); navigate('/checkout') }}
            >
              Checkout
            </button>
            <button
              type="button"
              className="btn btn-secondary cart-drawer-view-btn"
              onClick={() => { closeDrawer(); navigate('/cart') }}
            >
              View full cart
            </button>
          </div>
        )}
      </aside>
    </>
  )
}
