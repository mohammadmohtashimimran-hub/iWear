import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { listProductsAdmin, deleteProductAdmin } from '../../api'

export default function AdminProductList() {
  const [data, setData] = useState({ items: [], total: 0, pages: 0 })
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    listProductsAdmin({ page, per_page: 15 })
      .then(setData)
      .catch(() => setError('Failed to load products'))
      .finally(() => setLoading(false))
  }, [page])

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Delete "${name}"?`)) return
    try {
      await deleteProductAdmin(id)
      setData(prev => ({ ...prev, items: prev.items.filter(p => p.id !== id), total: prev.total - 1 }))
    } catch (e) {
      alert(e.message)
    }
  }

  if (loading && !data.items.length) return <div className="loading">Loading products…</div>
  if (error) return <p className="form-error">{error}</p>

  return (
    <div>
      <div className="admin-header">
        <h1>Products</h1>
        <Link to="/admin/products/new" className="btn btn-primary">Add product</Link>
      </div>
      <div className="card" style={{ overflow: 'hidden' }}>
        <table className="admin-table">
          <thead>
            <tr>
              <th style={{ width: 56 }}></th>
              <th>Name</th>
              <th>Price</th>
              <th>Stock</th>
              <th>Active</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {data.items.length === 0 ? (
              <tr><td colSpan={6} style={{ color: 'var(--color-text-muted)' }}>No products. Add one to get started.</td></tr>
            ) : (
              data.items.map(p => (
                <tr key={p.id}>
                  <td style={{ padding: '0.4rem 0.5rem' }}>
                    {p.primary_image ? (
                      <img src={p.primary_image} alt="" style={{ width: 40, height: 40, borderRadius: 6, objectFit: 'cover', display: 'block', background: 'var(--color-bg)' }} />
                    ) : (
                      <div style={{ width: 40, height: 40, borderRadius: 6, background: 'var(--color-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-text-muted)', fontSize: '0.75rem' }}>—</div>
                    )}
                  </td>
                  <td><Link to={`/admin/products/${p.id}`}>{p.name}</Link></td>
                  <td>{p.price != null ? `$${Number(p.price).toFixed(2)}` : '—'}</td>
                  <td>
                    <span style={{
                      fontWeight: 600,
                      color: (p.quantity || 0) === 0 ? '#dc2626' : (p.quantity || 0) <= 5 ? '#d97706' : 'inherit',
                    }}>
                      {p.quantity ?? 0}
                    </span>
                  </td>
                  <td>{p.active ? 'Yes' : 'No'}</td>
                  <td>
                    <Link to={`/admin/products/${p.id}`} className="btn btn-secondary" style={{ marginRight: '0.5rem', padding: '0.4rem 0.75rem' }}>Edit</Link>
                    <button type="button" className="btn btn-secondary" style={{ padding: '0.4rem 0.75rem' }} onClick={() => handleDelete(p.id, p.name)}>Delete</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      {data.pages > 1 && (
        <div className="pagination" style={{ marginTop: '1rem' }}>
          <button type="button" className="btn btn-secondary" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>Previous</button>
          <span>Page {page} of {data.pages}</span>
          <button type="button" className="btn btn-secondary" disabled={page >= data.pages} onClick={() => setPage(p => p + 1)}>Next</button>
        </div>
      )}
    </div>
  )
}
