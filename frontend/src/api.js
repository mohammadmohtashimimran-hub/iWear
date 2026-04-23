const API = '/api'
const ADMIN_TOKEN_KEY = 'iwear_admin_token'
const USER_TOKEN_KEY = 'iwear_user_token'

function getAuthHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem(ADMIN_TOKEN_KEY) : null
  const h = { 'Content-Type': 'application/json' }
  if (token) h['Authorization'] = `Bearer ${token}`
  return h
}

function getUserAuthHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem(USER_TOKEN_KEY) : null
  const h = { 'Content-Type': 'application/json' }
  if (token) h['Authorization'] = `Bearer ${token}`
  return h
}

export function getAdminToken() {
  return typeof window !== 'undefined' ? localStorage.getItem(ADMIN_TOKEN_KEY) : null
}
export function setAdminToken(token) {
  if (token && typeof window !== 'undefined') localStorage.setItem(ADMIN_TOKEN_KEY, token)
  else if (typeof window !== 'undefined') localStorage.removeItem(ADMIN_TOKEN_KEY)
}
export function getUserToken() {
  return typeof window !== 'undefined' ? localStorage.getItem(USER_TOKEN_KEY) : null
}
export function setUserToken(token) {
  if (token && typeof window !== 'undefined') localStorage.setItem(USER_TOKEN_KEY, token)
  else if (typeof window !== 'undefined') localStorage.removeItem(USER_TOKEN_KEY)
}

// ---- Auth (admin) ----
export async function loginAdmin(email, password) {
  const r = await fetch(`${API}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  if (!r.ok) {
    const text = await r.text()
    let msg = 'Login failed'
    try {
      const e = JSON.parse(text)
      if (e.error) msg = e.error
    } catch (_) {
      if (r.status >= 500) msg = 'Server error — check that the API is running (port 5000).'
    }
    throw new Error(msg)
  }
  const data = await r.json()
  if (data.access_token) setAdminToken(data.access_token)
  return data
}
export async function logoutAdmin() {
  try {
    await fetch(`${API}/auth/logout`, { method: 'POST', headers: getAuthHeaders() })
  } catch (_) {}
  setAdminToken(null)
}
export async function getMe() {
  const r = await fetch(`${API}/auth/me`, { headers: getAuthHeaders() })
  if (!r.ok) return null
  return r.json()
}

// ---- Admin: inventory (products, categories, brands) ----
export async function listProductsAdmin(params = {}) {
  const q = new URLSearchParams(params).toString()
  const r = await fetch(`${API}/inventory/products?${q}`, { headers: getAuthHeaders() })
  if (!r.ok) throw new Error('Failed to load products')
  return r.json()
}
export async function getProductAdmin(id) {
  const r = await fetch(`${API}/inventory/products/${id}`, { headers: getAuthHeaders() })
  if (!r.ok) throw new Error('Product not found')
  return r.json()
}
async function _apiError(r, fallback) {
  const text = await r.text()
  let e = {}
  try {
    e = JSON.parse(text)
  } catch (_) {}
  const msg = e.error || e.message || e.msg || (r.status === 401 ? 'Session expired. Please log in again.' : r.status === 403 ? 'You do not have permission.' : text || fallback)
  throw new Error(msg)
}

export async function createProductAdmin(data) {
  const r = await fetch(`${API}/inventory/products`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  })
  if (!r.ok) await _apiError(r, 'Failed to create product')
  return r.json()
}
export async function updateProductAdmin(id, data) {
  const r = await fetch(`${API}/inventory/products/${id}`, {
    method: 'PATCH',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  })
  if (!r.ok) await _apiError(r, 'Failed to update product')
  return r.json()
}
export async function deleteProductAdmin(id) {
  const r = await fetch(`${API}/inventory/products/${id}`, { method: 'DELETE', headers: getAuthHeaders() })
  if (!r.ok) throw new Error('Failed to delete product')
}

export async function uploadProductImages(productId, files) {
  const formData = new FormData()
  files.forEach(f => formData.append('images', f))
  const token = getAdminToken()
  const headers = {}
  if (token) headers['Authorization'] = `Bearer ${token}`
  const r = await fetch(`${API}/inventory/products/${productId}/images`, {
    method: 'POST',
    headers,
    body: formData,
  })
  if (!r.ok) await _apiError(r, 'Failed to upload images')
  return r.json()
}

export async function deleteProductImage(productId, imageId) {
  const r = await fetch(`${API}/inventory/products/${productId}/images/${imageId}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  })
  if (!r.ok) throw new Error('Failed to delete image')
}

export async function setPrimaryImage(productId, imageId) {
  const r = await fetch(`${API}/inventory/products/${productId}/images/${imageId}`, {
    method: 'PATCH',
    headers: getAuthHeaders(),
    body: JSON.stringify({ is_primary: true }),
  })
  if (!r.ok) throw new Error('Failed to set primary image')
  return r.json()
}
export async function getCategories() {
  const r = await fetch(`${API}/inventory/categories`, { headers: getAuthHeaders() })
  return r.ok ? r.json() : []
}
export async function getBrands() {
  const r = await fetch(`${API}/inventory/brands`, { headers: getAuthHeaders() })
  return r.ok ? r.json() : []
}
export async function getTypes() {
  const r = await fetch(`${API}/inventory/types`, { headers: getAuthHeaders() })
  return r.ok ? r.json() : []
}

// ---- Admin: catalog item CRUD (categories, brands, types) ----
async function _catalogCreate(endpoint, name) {
  const r = await fetch(`${API}/inventory/${endpoint}`, { method: 'POST', headers: getAuthHeaders(), body: JSON.stringify({ name }) })
  if (!r.ok) await _apiError(r, 'Failed to create')
  return r.json()
}
async function _catalogUpdate(endpoint, id, name) {
  const r = await fetch(`${API}/inventory/${endpoint}/${id}`, { method: 'PATCH', headers: getAuthHeaders(), body: JSON.stringify({ name }) })
  if (!r.ok) await _apiError(r, 'Failed to update')
  return r.json()
}
async function _catalogDelete(endpoint, id) {
  const r = await fetch(`${API}/inventory/${endpoint}/${id}`, { method: 'DELETE', headers: getAuthHeaders() })
  if (!r.ok) throw new Error('Failed to delete')
}
export const createCategory = (name) => _catalogCreate('categories', name)
export const updateCategory = (id, name) => _catalogUpdate('categories', id, name)
export const deleteCategory = (id) => _catalogDelete('categories', id)
export const createBrand = (name) => _catalogCreate('brands', name)
export const updateBrand = (id, name) => _catalogUpdate('brands', id, name)
export const deleteBrand = (id) => _catalogDelete('brands', id)
export const createType = (name) => _catalogCreate('types', name)
export const updateType = (id, name) => _catalogUpdate('types', id, name)
export const deleteType = (id) => _catalogDelete('types', id)

// ---- Admin: Addon groups + options ----
export async function listAddons(categoryId) {
  const q = categoryId ? `?category_id=${categoryId}` : ''
  const r = await fetch(`${API}/inventory/addons${q}`, { headers: getAuthHeaders() })
  return r.ok ? r.json() : []
}
export async function getAddon(id) {
  const r = await fetch(`${API}/inventory/addons/${id}`, { headers: getAuthHeaders() })
  if (!r.ok) throw new Error('Addon not found')
  return r.json()
}
export async function createAddon(data) {
  const r = await fetch(`${API}/inventory/addons`, { method: 'POST', headers: getAuthHeaders(), body: JSON.stringify(data) })
  if (!r.ok) await _apiError(r, 'Failed to create addon')
  return r.json()
}
export async function updateAddon(id, data) {
  const r = await fetch(`${API}/inventory/addons/${id}`, { method: 'PATCH', headers: getAuthHeaders(), body: JSON.stringify(data) })
  if (!r.ok) await _apiError(r, 'Failed to update addon')
  return r.json()
}
export async function deleteAddon(id) {
  const r = await fetch(`${API}/inventory/addons/${id}`, { method: 'DELETE', headers: getAuthHeaders() })
  if (!r.ok) throw new Error('Failed to delete addon')
}
export async function createAddonOption(addonId, data) {
  const r = await fetch(`${API}/inventory/addons/${addonId}/options`, { method: 'POST', headers: getAuthHeaders(), body: JSON.stringify(data) })
  if (!r.ok) await _apiError(r, 'Failed to create option')
  return r.json()
}
export async function updateAddonOption(addonId, optionId, data) {
  const r = await fetch(`${API}/inventory/addons/${addonId}/options/${optionId}`, { method: 'PATCH', headers: getAuthHeaders(), body: JSON.stringify(data) })
  if (!r.ok) await _apiError(r, 'Failed to update option')
  return r.json()
}
export async function deleteAddonOption(addonId, optionId) {
  const r = await fetch(`${API}/inventory/addons/${addonId}/options/${optionId}`, { method: 'DELETE', headers: getAuthHeaders() })
  if (!r.ok) throw new Error('Failed to delete option')
}

// ---- Public: addon image upload ----
export async function uploadAddonImage(file) {
  const formData = new FormData()
  formData.append('image', file)
  const r = await fetch(`${API}/sales/addon-image`, { method: 'POST', body: formData })
  if (!r.ok) {
    const e = await r.json().catch(() => ({}))
    throw new Error(e.error || 'Failed to upload image')
  }
  return r.json()
}

// ---- Admin: customers ----
export async function listCustomersAdmin(search = '') {
  const q = search ? `?search=${encodeURIComponent(search)}` : ''
  const r = await fetch(`${API}/sales/customers${q}`, { headers: getAuthHeaders() })
  if (!r.ok) throw new Error('Failed to load customers')
  return r.json()
}

// ---- Admin: orders ----
export async function listOrdersAdmin() {
  const r = await fetch(`${API}/sales/orders`, { headers: getAuthHeaders() })
  if (!r.ok) throw new Error('Failed to load orders')
  return r.json()
}
export async function getOrderStatuses() {
  const r = await fetch(`${API}/sales/order-statuses`)
  return r.ok ? r.json() : []
}
export async function createOrderStatus(data) {
  const r = await fetch(`${API}/sales/order-statuses`, { method: 'POST', headers: getAuthHeaders(), body: JSON.stringify(data) })
  if (!r.ok) await _apiError(r, 'Failed to create status')
  return r.json()
}
export async function updateOrderStatus(id, data) {
  const r = await fetch(`${API}/sales/order-statuses/${id}`, { method: 'PATCH', headers: getAuthHeaders(), body: JSON.stringify(data) })
  if (!r.ok) await _apiError(r, 'Failed to update status')
  return r.json()
}
export async function deleteOrderStatus(id) {
  const r = await fetch(`${API}/sales/order-statuses/${id}`, { method: 'DELETE', headers: getAuthHeaders() })
  if (!r.ok) await _apiError(r, 'Failed to delete status')
}
export async function updateOrderStatusAdmin(orderId, status) {
  const r = await fetch(`${API}/sales/orders/${orderId}`, {
    method: 'PATCH',
    headers: getAuthHeaders(),
    body: JSON.stringify({ status }),
  })
  if (!r.ok) {
    const e = await r.json().catch(() => ({}))
    throw new Error(e.error || 'Failed to update order')
  }
  return r.json()
}

// ---- Countries & Cities ----
export async function getCountries() {
  const r = await fetch(`${API}/settings/countries`)
  return r.ok ? r.json() : []
}
export async function createCountry(name) {
  const r = await fetch(`${API}/settings/countries`, { method: 'POST', headers: getAuthHeaders(), body: JSON.stringify({ name }) })
  if (!r.ok) await _apiError(r, 'Failed to create country')
  return r.json()
}
export async function updateCountry(id, name) {
  const r = await fetch(`${API}/settings/countries/${id}`, { method: 'PATCH', headers: getAuthHeaders(), body: JSON.stringify({ name }) })
  if (!r.ok) await _apiError(r, 'Failed to update country')
  return r.json()
}
export async function deleteCountry(id) {
  const r = await fetch(`${API}/settings/countries/${id}`, { method: 'DELETE', headers: getAuthHeaders() })
  if (!r.ok) throw new Error('Failed to delete country')
}
export async function getCities(countryId) {
  const q = countryId ? `?country_id=${countryId}` : ''
  const r = await fetch(`${API}/settings/cities${q}`)
  return r.ok ? r.json() : []
}
export async function createCity(name, countryId) {
  const r = await fetch(`${API}/settings/cities`, { method: 'POST', headers: getAuthHeaders(), body: JSON.stringify({ name, country_id: countryId }) })
  if (!r.ok) await _apiError(r, 'Failed to create city')
  return r.json()
}
export async function updateCity(id, name) {
  const r = await fetch(`${API}/settings/cities/${id}`, { method: 'PATCH', headers: getAuthHeaders(), body: JSON.stringify({ name }) })
  if (!r.ok) await _apiError(r, 'Failed to update city')
  return r.json()
}
export async function deleteCity(id) {
  const r = await fetch(`${API}/settings/cities/${id}`, { method: 'DELETE', headers: getAuthHeaders() })
  if (!r.ok) throw new Error('Failed to delete city')
}

// ---- AI Business Insights Assistant (admin) ----
export async function aiQuery(query) {
  const r = await fetch(`${API}/ai-assistant/query`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ query }),
  })
  if (!r.ok) await _apiError(r, 'AI query failed')
  return r.json()
}
export async function aiIntents() {
  const r = await fetch(`${API}/ai-assistant/intents`, { headers: getAuthHeaders() })
  if (!r.ok) return []
  return r.json()
}
export async function aiHistory() {
  const r = await fetch(`${API}/ai-assistant/history`, { headers: getAuthHeaders() })
  if (!r.ok) return []
  return r.json()
}

// ---- Public / store ----
export async function getSettings() {
  const r = await fetch(`${API}/settings/`)
  if (!r.ok) return {}
  return r.json()
}

export async function getProducts(params = {}) {
  const q = new URLSearchParams(params).toString()
  const r = await fetch(`${API}/sales/products?${q}`)
  if (!r.ok) throw new Error('Failed to load products')
  return r.json()
}

export async function getProduct(id) {
  const r = await fetch(`${API}/sales/products/${id}`)
  if (!r.ok) throw new Error('Product not found')
  return r.json()
}

export async function getFrameTypes() {
  const r = await fetch(`${API}/sales/frame-types`)
  return r.ok ? r.json() : []
}

export async function getLensTypes() {
  const r = await fetch(`${API}/sales/lens-types`)
  return r.ok ? r.json() : []
}

export async function getLensIndexes() {
  const r = await fetch(`${API}/sales/lens-indexes`)
  return r.ok ? r.json() : []
}

export async function getLensCoatings() {
  const r = await fetch(`${API}/sales/lens-coatings`)
  return r.ok ? r.json() : []
}

export async function createCart(customerId = null) {
  const r = await fetch(`${API}/sales/carts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(customerId != null ? { customer_id: customerId } : {}),
  })
  if (!r.ok) throw new Error('Failed to create cart')
  return r.json()
}

export async function getCart(cartId) {
  const r = await fetch(`${API}/sales/carts/${cartId}`)
  if (!r.ok) throw new Error('Cart not found')
  return r.json()
}

export async function addToCart(cartId, { productVariantId, productId, quantity = 1, unitPrice, addons } = {}) {
  const body = { quantity, unit_price: unitPrice }
  if (productVariantId) body.product_variant_id = productVariantId
  else if (productId) body.product_id = productId
  if (addons?.length) body.addons = addons
  const r = await fetch(`${API}/sales/carts/${cartId}/items`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!r.ok) {
    const e = await r.json().catch(() => ({}))
    const err = new Error(e.error || `Failed to add to cart (HTTP ${r.status})`)
    err.status = r.status
    throw err
  }
  return r.json()
}

export async function updateCartItem(cartId, itemId, quantity) {
  const r = await fetch(`${API}/sales/carts/${cartId}/items/${itemId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ quantity }),
  })
  if (!r.ok) throw new Error('Failed to update')
  return r.ok ? r.json() : null
}

export async function removeCartItem(cartId, itemId) {
  await fetch(`${API}/sales/carts/${cartId}/items/${itemId}`, { method: 'DELETE' })
}

export async function createCustomer(data) {
  const r = await fetch(`${API}/sales/customers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!r.ok) throw new Error('Failed to create customer')
  return r.json()
}

export async function createOrder(cartId, customerId, options = {}) {
  const token = getUserToken()
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const r = await fetch(`${API}/sales/orders`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ cart_id: cartId, customer_id: customerId, ...options }),
  })
  if (!r.ok) {
    const e = await r.json().catch(() => ({}))
    throw new Error(e.error || 'Failed to place order')
  }
  return r.json()
}

export async function getOrders(customerId) {
  const r = await fetch(`${API}/sales/orders?customer_id=${customerId}`)
  if (!r.ok) throw new Error('Failed to load orders')
  return r.json()
}

export async function getOrder(orderId) {
  const r = await fetch(`${API}/sales/orders/${orderId}`)
  if (!r.ok) throw new Error('Order not found')
  return r.json()
}

// ---- User auth (storefront) ----
export async function loginUser(email, password) {
  const r = await fetch(`${API}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  if (!r.ok) {
    const e = await r.json().catch(() => ({}))
    throw new Error(e.error || 'Login failed')
  }
  const data = await r.json()
  if (data.access_token) setUserToken(data.access_token)
  return data
}

export async function registerUser(email, password, phone) {
  const r = await fetch(`${API}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, phone }),
  })
  if (!r.ok) {
    const e = await r.json().catch(() => ({}))
    throw new Error(e.error || 'Registration failed')
  }
  return r.json()
}

export async function logoutUser() {
  try {
    await fetch(`${API}/auth/logout`, { method: 'POST', headers: getUserAuthHeaders() })
  } catch (_) {}
  setUserToken(null)
}

export async function getUserMe() {
  const r = await fetch(`${API}/auth/me`, { headers: getUserAuthHeaders() })
  if (!r.ok) return null
  return r.json()
}

// ---- User orders (authenticated) ----
export async function getMyOrders() {
  const r = await fetch(`${API}/sales/my-orders`, { headers: getUserAuthHeaders() })
  if (!r.ok) throw new Error('Failed to load orders')
  return r.json()
}

// ---- User cart (authenticated) ----
export async function getMyCart() {
  const r = await fetch(`${API}/sales/my-cart`, { headers: getUserAuthHeaders() })
  if (!r.ok) throw new Error('Failed to load cart')
  return r.json()
}

export async function addToMyCart({ productVariantId, productId, quantity = 1, unitPrice, addons } = {}) {
  const body = { quantity, unit_price: unitPrice }
  if (productVariantId) body.product_variant_id = productVariantId
  else if (productId) body.product_id = productId
  if (addons?.length) body.addons = addons
  const r = await fetch(`${API}/sales/my-cart/items`, {
    method: 'POST',
    headers: getUserAuthHeaders(),
    body: JSON.stringify(body),
  })
  if (!r.ok) throw new Error('Failed to add to cart')
  return r.json()
}

export async function updateMyCartItem(itemId, quantity) {
  const r = await fetch(`${API}/sales/my-cart/items/${itemId}`, {
    method: 'PATCH',
    headers: getUserAuthHeaders(),
    body: JSON.stringify({ quantity }),
  })
  if (!r.ok) throw new Error('Failed to update')
  return r.json()
}

export async function removeMyCartItem(itemId) {
  const r = await fetch(`${API}/sales/my-cart/items/${itemId}`, {
    method: 'DELETE',
    headers: getUserAuthHeaders(),
  })
  if (!r.ok) throw new Error('Failed to remove item')
  return r.json()
}

export async function mergeGuestCart(guestCartId) {
  const r = await fetch(`${API}/sales/my-cart/merge`, {
    method: 'POST',
    headers: getUserAuthHeaders(),
    body: JSON.stringify({ guest_cart_id: guestCartId }),
  })
  if (!r.ok) throw new Error('Failed to merge cart')
  return r.json()
}
