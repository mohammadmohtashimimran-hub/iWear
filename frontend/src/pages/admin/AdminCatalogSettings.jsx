import { useState, useEffect, useCallback } from 'react'
import {
  getCategories, createCategory, updateCategory, deleteCategory,
  getBrands, createBrand, updateBrand, deleteBrand,
  getTypes, createType, updateType, deleteType,
} from '../../api'

function CatalogSection({ title, items, onCreate, onUpdate, onDelete }) {
  const [newName, setNewName] = useState('')
  const [editId, setEditId] = useState(null)
  const [editName, setEditName] = useState('')
  const [busy, setBusy] = useState(false)

  const handleCreate = async (e) => {
    e.preventDefault()
    if (!newName.trim()) return
    setBusy(true)
    try {
      await onCreate(newName.trim())
      setNewName('')
    } catch (err) { alert(err.message) }
    finally { setBusy(false) }
  }

  const handleUpdate = async (id) => {
    if (!editName.trim()) return
    setBusy(true)
    try {
      await onUpdate(id, editName.trim())
      setEditId(null)
    } catch (err) { alert(err.message) }
    finally { setBusy(false) }
  }

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Delete "${name}"? Products using it will lose this assignment.`)) return
    try { await onDelete(id) } catch (err) { alert(err.message) }
  }

  return (
    <div className="card" style={{ padding: '1.25rem' }}>
      <h3 style={{ margin: '0 0 0.75rem', fontSize: '1rem', fontWeight: 600 }}>{title}</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', marginBottom: '0.75rem' }}>
        {items.length === 0 && <span style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>None yet</span>}
        {items.map(item => (
          <div key={item.id} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.4rem 0', borderBottom: '1px solid var(--color-border)' }}>
            {editId === item.id ? (
              <>
                <input
                  value={editName}
                  onChange={e => setEditName(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && handleUpdate(item.id)}
                  style={{ flex: 1, padding: '0.35rem 0.5rem', fontSize: '0.9rem', border: '1px solid var(--color-accent)', borderRadius: 4, outline: 'none' }}
                  autoFocus
                />
                <button type="button" className="btn btn-primary" style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }} onClick={() => handleUpdate(item.id)} disabled={busy}>Save</button>
                <button type="button" className="btn btn-secondary" style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }} onClick={() => setEditId(null)}>Cancel</button>
              </>
            ) : (
              <>
                <span style={{ flex: 1, fontSize: '0.9rem' }}>{item.name}</span>
                <button type="button" className="btn btn-secondary" style={{ padding: '0.25rem 0.5rem', fontSize: '0.78rem' }} onClick={() => { setEditId(item.id); setEditName(item.name) }}>Edit</button>
                <button type="button" className="btn btn-secondary" style={{ padding: '0.25rem 0.5rem', fontSize: '0.78rem', color: 'var(--color-error)' }} onClick={() => handleDelete(item.id, item.name)}>Delete</button>
              </>
            )}
          </div>
        ))}
      </div>
      <form onSubmit={handleCreate} style={{ display: 'flex', gap: '0.5rem' }}>
        <input
          value={newName}
          onChange={e => setNewName(e.target.value)}
          placeholder={`New ${title.toLowerCase().replace(/s$/, '')} name`}
          style={{ flex: 1, padding: '0.4rem 0.6rem', fontSize: '0.9rem', border: '1px solid var(--color-border)', borderRadius: 4 }}
        />
        <button type="submit" className="btn btn-primary" style={{ padding: '0.4rem 0.85rem', fontSize: '0.85rem' }} disabled={busy || !newName.trim()}>
          Add
        </button>
      </form>
    </div>
  )
}

export default function AdminCatalogSettings() {
  const [categories, setCategories] = useState([])
  const [brands, setBrands] = useState([])
  const [types, setTypes] = useState([])
  const [loading, setLoading] = useState(true)

  const reload = useCallback(() => {
    setLoading(true)
    Promise.all([getCategories(), getBrands(), getTypes()])
      .then(([c, b, t]) => { setCategories(c || []); setBrands(b || []); setTypes(t || []) })
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { reload() }, [reload])

  const wrap = (fn) => async (...args) => { await fn(...args); reload() }

  if (loading && !categories.length) return <div className="loading">Loading…</div>

  return (
    <div>
      <div className="admin-header">
        <h1>Catalog Settings</h1>
      </div>
      <p style={{ color: 'var(--color-text-muted)', margin: '-0.75rem 0 1.25rem', fontSize: '0.9rem' }}>
        Manage the dropdown options that appear when creating or editing products.
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.25rem' }}>
        <CatalogSection title="Categories" items={categories} onCreate={wrap(createCategory)} onUpdate={wrap(updateCategory)} onDelete={wrap(deleteCategory)} />
        <CatalogSection title="Brands" items={brands} onCreate={wrap(createBrand)} onUpdate={wrap(updateBrand)} onDelete={wrap(deleteBrand)} />
        <CatalogSection title="Types" items={types} onCreate={wrap(createType)} onUpdate={wrap(updateType)} onDelete={wrap(deleteType)} />
      </div>
    </div>
  )
}
