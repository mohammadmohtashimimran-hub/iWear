import { useState, useEffect, useCallback } from 'react'
import {
  getOrderStatuses, createOrderStatus, updateOrderStatus, deleteOrderStatus,
} from '../../api'

export default function AdminOrderStatuses() {
  const [statuses, setStatuses] = useState([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)

  const [newName, setNewName] = useState('')
  const [newCode, setNewCode] = useState('')

  const [editId, setEditId] = useState(null)
  const [editName, setEditName] = useState('')
  const [editCode, setEditCode] = useState('')

  const reload = useCallback(async () => {
    const data = await getOrderStatuses()
    setStatuses(data || [])
  }, [])

  useEffect(() => {
    reload().finally(() => setLoading(false))
  }, [reload])

  const handleCreate = async (e) => {
    e.preventDefault()
    if (!newName.trim() || !newCode.trim()) return
    setBusy(true)
    try {
      await createOrderStatus({ name: newName.trim(), code: newCode.trim().toLowerCase() })
      setNewName('')
      setNewCode('')
      await reload()
    } catch (err) { alert(err.message) }
    finally { setBusy(false) }
  }

  const handleUpdate = async (id) => {
    if (!editName.trim() || !editCode.trim()) return
    setBusy(true)
    try {
      await updateOrderStatus(id, { name: editName.trim(), code: editCode.trim().toLowerCase() })
      setEditId(null)
      await reload()
    } catch (err) { alert(err.message) }
    finally { setBusy(false) }
  }

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Delete status "${name}"? This only works if no orders use this status.`)) return
    try {
      await deleteOrderStatus(id)
      await reload()
    } catch (err) { alert(err.message) }
  }

  if (loading) return <div className="loading">Loading…</div>

  return (
    <div>
      <div className="admin-header">
        <h1>Order Statuses</h1>
      </div>
      <p style={{ color: 'var(--color-text-muted)', margin: '-0.75rem 0 1.25rem', fontSize: '0.9rem' }}>
        Manage the statuses that can be assigned to orders. Statuses in use cannot be deleted.
      </p>

      <div className="card" style={{ padding: '1.25rem', maxWidth: 600 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', marginBottom: '1rem' }}>
          {statuses.length === 0 && (
            <span style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>No statuses yet</span>
          )}
          {statuses.map(s => (
            <div key={s.id} style={{
              display: 'flex', alignItems: 'center', gap: '0.5rem',
              padding: '0.5rem 0', borderBottom: '1px solid var(--color-border)',
            }}>
              {editId === s.id ? (
                <>
                  <input
                    value={editName}
                    onChange={e => setEditName(e.target.value)}
                    placeholder="Name"
                    style={{ flex: 1, padding: '0.35rem 0.5rem', fontSize: '0.9rem', border: '1px solid var(--color-accent)', borderRadius: 4 }}
                    autoFocus
                  />
                  <input
                    value={editCode}
                    onChange={e => setEditCode(e.target.value)}
                    placeholder="code"
                    style={{ width: 120, padding: '0.35rem 0.5rem', fontSize: '0.9rem', border: '1px solid var(--color-accent)', borderRadius: 4 }}
                    onKeyDown={e => e.key === 'Enter' && handleUpdate(s.id)}
                  />
                  <button type="button" className="btn btn-primary" style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }} onClick={() => handleUpdate(s.id)} disabled={busy}>Save</button>
                  <button type="button" className="btn btn-secondary" style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }} onClick={() => setEditId(null)}>Cancel</button>
                </>
              ) : (
                <>
                  <span style={{ flex: 1, fontSize: '0.9rem' }}>
                    <strong>{s.name}</strong>
                    <span style={{ color: 'var(--color-text-muted)', marginLeft: '0.5rem', fontSize: '0.82rem' }}>({s.code})</span>
                  </span>
                  <button type="button" className="btn btn-secondary" style={{ padding: '0.25rem 0.5rem', fontSize: '0.78rem' }} onClick={() => { setEditId(s.id); setEditName(s.name); setEditCode(s.code) }}>Edit</button>
                  <button type="button" className="btn btn-secondary" style={{ padding: '0.25rem 0.5rem', fontSize: '0.78rem', color: 'var(--color-error)' }} onClick={() => handleDelete(s.id, s.name)}>Delete</button>
                </>
              )}
            </div>
          ))}
        </div>

        <form onSubmit={handleCreate} style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-end' }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 500, marginBottom: 2 }}>Name</label>
            <input
              value={newName}
              onChange={e => setNewName(e.target.value)}
              placeholder="e.g. Ready to Ship"
              style={{ width: '100%', padding: '0.4rem 0.6rem', fontSize: '0.9rem', border: '1px solid var(--color-border)', borderRadius: 4 }}
            />
          </div>
          <div style={{ width: 140 }}>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 500, marginBottom: 2 }}>Code</label>
            <input
              value={newCode}
              onChange={e => setNewCode(e.target.value)}
              placeholder="e.g. ready"
              style={{ width: '100%', padding: '0.4rem 0.6rem', fontSize: '0.9rem', border: '1px solid var(--color-border)', borderRadius: 4 }}
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ padding: '0.4rem 0.85rem', fontSize: '0.85rem', height: 36 }} disabled={busy || !newName.trim() || !newCode.trim()}>
            Add
          </button>
        </form>
      </div>
    </div>
  )
}
