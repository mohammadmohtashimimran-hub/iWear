import { Navigate, useLocation } from 'react-router-dom'
import { getAdminToken } from '../api'

export default function ProtectedAdminRoute({ children }) {
  const location = useLocation()
  const token = getAdminToken()
  if (!token) {
    return <Navigate to="/admin/login" state={{ from: location }} replace />
  }
  return children
}
