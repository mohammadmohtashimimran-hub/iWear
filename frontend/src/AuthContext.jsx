import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { getUserToken, getUserMe, logoutUser, getMyCart, getCart } from './api'

const CART_KEY = 'iwear_cart_id'
const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [cartCount, setCartCount] = useState(0)
  const [loading, setLoading] = useState(true)

  const [drawerOpen, setDrawerOpen] = useState(false)
  const [drawerCart, setDrawerCart] = useState(null)

  const refreshCart = useCallback(async () => {
    // Authenticated user — pull from /my-cart.
    if (getUserToken()) {
      try {
        const cart = await getMyCart()
        setCartCount(cart.items?.reduce((sum, i) => sum + i.quantity, 0) ?? 0)
      } catch {
        setCartCount(0)
      }
      return
    }
    // Guest — pull the cart id from localStorage and fetch /carts/:id.
    const guestId = parseInt(localStorage.getItem(CART_KEY), 10)
    if (!guestId) {
      setCartCount(0)
      return
    }
    try {
      const cart = await getCart(guestId)
      if (cart?.status && cart.status !== 'active') {
        // Cart has been converted (order placed) or invalidated — clear it.
        localStorage.removeItem(CART_KEY)
        setCartCount(0)
        return
      }
      setCartCount(cart.items?.reduce((sum, i) => sum + i.quantity, 0) ?? 0)
    } catch {
      setCartCount(0)
    }
  }, [])

  const openDrawer = useCallback(async () => {
    setDrawerOpen(true)
    try {
      if (getUserToken()) {
        const cart = await getMyCart()
        setDrawerCart(cart)
      } else {
        const guestId = parseInt(localStorage.getItem(CART_KEY), 10)
        if (guestId) {
          const cart = await getCart(guestId)
          setDrawerCart(cart)
        } else {
          setDrawerCart({ items: [] })
        }
      }
    } catch {
      setDrawerCart({ items: [] })
    }
  }, [])

  const closeDrawer = useCallback(() => {
    setDrawerOpen(false)
  }, [])

  useEffect(() => {
    const token = getUserToken()
    if (!token) {
      setLoading(false)
      return
    }
    getUserMe()
      .then(u => {
        setUser(u)
        if (u) return refreshCart()
      })
      .catch(() => setUser(null))
      .finally(() => setLoading(false))
  }, [refreshCart])

  const logout = useCallback(async () => {
    await logoutUser()
    setUser(null)
    setCartCount(0)
  }, [])

  const setLoggedIn = useCallback((userData) => {
    setUser(userData)
    refreshCart()
  }, [refreshCart])

  return (
    <AuthContext.Provider value={{
      user, loading, cartCount, logout, setLoggedIn, refreshCart,
      drawerOpen, drawerCart, setDrawerCart, openDrawer, closeDrawer,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be inside AuthProvider')
  return ctx
}
