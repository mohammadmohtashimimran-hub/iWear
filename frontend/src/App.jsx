import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './AuthContext'
import { CurrencyProvider } from './CurrencyContext'
import Layout from './Layout'
import ProductList from './pages/ProductList'
import ProductDetail from './pages/ProductDetail'
import Cart from './pages/Cart'
import Checkout from './pages/Checkout'
import OrderConfirmation from './pages/OrderConfirmation'
import OrderHistory from './pages/OrderHistory'
import SizeGuide from './pages/SizeGuide'
import Login from './pages/Login'
import Register from './pages/Register'
import ProtectedAdminRoute from './components/ProtectedAdminRoute'
import AdminLayout from './pages/admin/AdminLayout'
import AdminLogin from './pages/admin/AdminLogin'
import AdminDashboard from './pages/admin/AdminDashboard'
import AdminProductList from './pages/admin/AdminProductList'
import AdminProductForm from './pages/admin/AdminProductForm'
import AdminOrderList from './pages/admin/AdminOrderList'
import AdminOrderDetail from './pages/admin/AdminOrderDetail'
import AdminCatalogSettings from './pages/admin/AdminCatalogSettings'
import AdminAddons from './pages/admin/AdminAddons'
import AdminLocations from './pages/admin/AdminLocations'
import AdminOrderStatuses from './pages/admin/AdminOrderStatuses'
import AdminCustomers from './pages/admin/AdminCustomers'
import AdminAIInsights from './pages/admin/AdminAIInsights'

export default function App() {
  return (
    <BrowserRouter>
      <CurrencyProvider>
      <AuthProvider>
        <Routes>
          {/* Store (customer-facing) */}
          <Route path="/" element={<Layout />}>
            <Route index element={<ProductList />} />
            <Route path="product/:id" element={<ProductDetail />} />
            <Route path="cart" element={<Cart />} />
            <Route path="checkout" element={<Checkout />} />
            <Route path="order-confirmation/:orderId" element={<OrderConfirmation />} />
            <Route path="orders" element={<OrderHistory />} />
            <Route path="size-guide" element={<SizeGuide />} />
            <Route path="login" element={<Login />} />
            <Route path="register" element={<Register />} />
          </Route>

          {/* Admin */}
          <Route path="/admin/login" element={<AdminLogin />} />
          <Route path="/admin" element={<ProtectedAdminRoute><AdminLayout /></ProtectedAdminRoute>}>
            <Route index element={<AdminDashboard />} />
            <Route path="products" element={<AdminProductList />} />
            <Route path="products/new" element={<AdminProductForm />} />
            <Route path="products/:id" element={<AdminProductForm />} />
            <Route path="orders" element={<AdminOrderList />} />
            <Route path="orders/:id" element={<AdminOrderDetail />} />
            <Route path="catalog" element={<AdminCatalogSettings />} />
            <Route path="addons" element={<AdminAddons />} />
            <Route path="locations" element={<AdminLocations />} />
            <Route path="order-statuses" element={<AdminOrderStatuses />} />
            <Route path="customers" element={<AdminCustomers />} />
            <Route path="ai-insights" element={<AdminAIInsights />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
      </CurrencyProvider>
    </BrowserRouter>
  )
}
