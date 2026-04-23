import { useState, useEffect, useCallback } from 'react'
import { listCustomersAdmin } from '../../api'

export default function AdminCustomers() {
  const [customers, setCustomers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await listCustomersAdmin(search)
      setCustomers(Array.isArray(data) ? data : [])
    } catch {
      setError('Failed to load customers')
    } finally {
      setLoading(false)
    }
  }, [search])

  useEffect(() => { load() }, [load])

  const handleSearch = (e) => {
    e.preventDefault()
    setSearch(searchInput.trim())
  }

  return (
    <div>
      <div className="admin-header">
        <h1>Customers</h1>
        <span style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>
          {!loading && `${customers.length} customer${customers.length !== 1 ? 's' : ''}`}
        </span>
      </div>

      <form onSubmit={handleSearch} style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem', maxWidth: 420 }}>
        <input
          value={searchInput}
          onChange={e => setSearchInput(e.target.value)}
          placeholder="Search by name, email or phone…"
          style={{
            flex: 1, padding: '0.5rem 0.75rem', fontSize: '0.9rem',
            border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)',
            fontFamily: 'inherit',
          }}
        />
        <button type="submit" className="btn btn-primary" style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}>
          Search
        </button>
        {search && (
          <button
            type="button" className="btn btn-secondary"
            style={{ padding: '0.5rem 0.75rem', fontSize: '0.9rem' }}
            onClick={() => { setSearchInput(''); setSearch('') }}
          >
            Clear
          </button>
        )}
      </form>

      {error && <p className="form-error">{error}</p>}

      {loading ? (
        <div className="loading">Loading customers…</div>
      ) : (
        <div className="card" style={{ overflow: 'hidden' }}>
          <table className="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Phone</th>
                <th>Email</th>
                <th>Orders</th>
                <th>Total Spent</th>
                <th>Joined</th>
              </tr>
            </thead>
            <tbody>
              {customers.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ color: 'var(--color-text-muted)', textAlign: 'center' }}>
                    {search ? 'No customers match your search.' : 'No customers yet.'}
                  </td>
                </tr>
              ) : (
                customers.map(c => (
                  <tr key={c.id}>
                    <td style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>#{c.id}</td>
                    <td>
                      <strong>{c.first_name}</strong>
                      {c.last_name ? ` ${c.last_name}` : ''}
                    </td>
                    <td>{c.phone || '—'}</td>
                    <td style={{ fontSize: '0.9rem' }}>{c.email || '—'}</td>
                    <td>
                      <span style={{
                        fontWeight: 600,
                        color: c.order_count > 0 ? 'var(--color-accent)' : 'var(--color-text-muted)',
                      }}>
                        {c.order_count}
                      </span>
                    </td>
                    <td style={{ fontWeight: 600 }}>
                      ${Number(c.total_spent).toFixed(2)}
                    </td>
                    <td style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>
                      {c.created_at ? new Date(c.created_at).toLocaleDateString() : '—'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
