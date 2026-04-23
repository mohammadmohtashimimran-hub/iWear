import { useState, useEffect, useCallback } from 'react'
import {
  listAddons, createAddon, updateAddon, deleteAddon,
  createAddonOption, updateAddonOption, deleteAddonOption,
  getCategories,
} from '../../api'

const emptyGroup = { name: '', description: '', category_id: '', is_required: false, requires_image: false, active: true }
const emptyOpt = { name: '', description: '', price: '', active: true }

export default function AdminAddons() {
  const [addons, setAddons] = useState([])
  const [categories, setCategories] = useState([])
  const [filterCat, setFilterCat] = useState('')
  const [loading, setLoading] = useState(true)

  const [showGroupForm, setShowGroupForm] = useState(false)
  const [editGroupId, setEditGroupId] = useState(null)
  const [groupForm, setGroupForm] = useState(emptyGroup)

  const [optFormFor, setOptFormFor] = useState(null)
  const [editOptId, setEditOptId] = useState(null)
  const [optForm, setOptForm] = useState(emptyOpt)

  const [expandedGroup, setExpandedGroup] = useState(null)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  const reload = useCallback(() => {
    setLoading(true)
    Promise.all([listAddons(filterCat || undefined), getCategories()])
      .then(([a, c]) => { setAddons(a || []); setCategories(c || []) })
      .finally(() => setLoading(false))
  }, [filterCat])

  useEffect(() => { reload() }, [reload])

  // ---- Group form ----
  const openNewGroup = () => {
    setEditGroupId(null)
    setGroupForm(emptyGroup)
    setShowGroupForm(true)
    setError(null)
  }
  const openEditGroup = (g) => {
    setEditGroupId(g.id)
    setGroupForm({ name: g.name, description: g.description || '', category_id: g.category_id || '', is_required: g.is_required, requires_image: g.requires_image || false, active: g.active })
    setShowGroupForm(true)
    setError(null)
  }
  const submitGroup = async (e) => {
    e.preventDefault()
    setError(null)
    setSaving(true)
    const payload = {
      name: groupForm.name.trim(),
      description: groupForm.description || undefined,
      category_id: groupForm.category_id ? parseInt(groupForm.category_id, 10) : undefined,
      is_required: groupForm.is_required,
      requires_image: groupForm.requires_image,
      active: groupForm.active,
    }
    try {
      if (editGroupId) await updateAddon(editGroupId, payload)
      else await createAddon(payload)
      setShowGroupForm(false)
      reload()
    } catch (err) { setError(err.message) }
    finally { setSaving(false) }
  }
  const handleDeleteGroup = async (id, name) => {
    if (!window.confirm(`Delete addon group "${name}" and all its options?`)) return
    try { await deleteAddon(id); reload() } catch (err) { alert(err.message) }
  }

  // ---- Option form ----
  const openNewOpt = (addonId) => {
    setOptFormFor(addonId)
    setEditOptId(null)
    setOptForm(emptyOpt)
    setError(null)
  }
  const openEditOpt = (addonId, opt) => {
    setOptFormFor(addonId)
    setEditOptId(opt.id)
    setOptForm({ name: opt.name, description: opt.description || '', price: opt.price != null ? opt.price : '', active: opt.active })
    setError(null)
  }
  const submitOpt = async (e) => {
    e.preventDefault()
    setError(null)
    setSaving(true)
    const payload = {
      name: optForm.name.trim(),
      description: optForm.description || undefined,
      price: optForm.price !== '' ? Number(optForm.price) : 0,
      active: optForm.active,
    }
    try {
      if (editOptId) await updateAddonOption(optFormFor, editOptId, payload)
      else await createAddonOption(optFormFor, payload)
      setOptFormFor(null)
      reload()
    } catch (err) { setError(err.message) }
    finally { setSaving(false) }
  }
  const handleDeleteOpt = async (addonId, optId, name) => {
    if (!window.confirm(`Delete option "${name}"?`)) return
    try { await deleteAddonOption(addonId, optId); reload() } catch (err) { alert(err.message) }
  }

  return (
    <div>
      <div className="admin-header">
        <h1>Addons</h1>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <select value={filterCat} onChange={e => setFilterCat(e.target.value)}
            style={{ padding: '0.5rem 0.75rem', border: '1px solid var(--color-border)', borderRadius: 6, fontSize: '0.9rem' }}>
            <option value="">All categories</option>
            {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <button type="button" className="btn btn-primary" onClick={openNewGroup}>Add addon group</button>
        </div>
      </div>

      <p style={{ color: 'var(--color-text-muted)', margin: '-0.5rem 0 1.25rem', fontSize: '0.9rem' }}>
        Create addon groups per category, then add selectable options within each group.
      </p>

      {/* Group form */}
      {showGroupForm && (
        <div className="card" style={{ padding: '1.25rem', marginBottom: '1.25rem', maxWidth: 520 }}>
          <h2 style={{ margin: '0 0 0.75rem', fontSize: '1.05rem', fontWeight: 600 }}>
            {editGroupId ? 'Edit addon group' : 'New addon group'}
          </h2>
          {error && <p className="form-error" style={{ marginBottom: '0.5rem' }}>{error}</p>}
          <form onSubmit={submitGroup}>
            <div className="form-group"><label>Group name *</label>
              <input value={groupForm.name} onChange={e => setGroupForm(f => ({ ...f, name: e.target.value }))} placeholder='e.g. "Glasses", "Lens Coating"' required />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div className="form-group"><label>Category *</label>
                <select value={groupForm.category_id} onChange={e => setGroupForm(f => ({ ...f, category_id: e.target.value }))} required>
                  <option value="">Select</option>
                  {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </div>
              <div className="form-group" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', gap: '0.4rem' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <input type="checkbox" checked={groupForm.is_required} onChange={e => setGroupForm(f => ({ ...f, is_required: e.target.checked }))} />
                  Required selection
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <input type="checkbox" checked={groupForm.requires_image} onChange={e => setGroupForm(f => ({ ...f, requires_image: e.target.checked }))} />
                  Requires image upload
                </label>
              </div>
            </div>
            <div className="form-group"><label>Description</label>
              <input value={groupForm.description} onChange={e => setGroupForm(f => ({ ...f, description: e.target.value }))} placeholder="Shown to customer" />
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Saving…' : (editGroupId ? 'Update' : 'Create')}</button>
              <button type="button" className="btn btn-secondary" onClick={() => setShowGroupForm(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      {/* Addon groups list */}
      {loading && !addons.length ? <div className="loading">Loading…</div> : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {addons.length === 0 && <div className="card" style={{ padding: '2rem', textAlign: 'center', color: 'var(--color-text-muted)' }}>No addon groups yet. Create one to get started.</div>}
          {addons.map(g => {
            const isOpen = expandedGroup === g.id
            const opts = g.options || []
            return (
              <div key={g.id} className="card" style={{ overflow: 'visible' }}>
                {/* Group header */}
                <div
                  style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '1rem 1.25rem', cursor: 'pointer', userSelect: 'none' }}
                  onClick={() => setExpandedGroup(isOpen ? null : g.id)}
                >
                  <span style={{ fontSize: '1.1rem', transition: 'transform .15s', transform: isOpen ? 'rotate(90deg)' : 'rotate(0)' }}>▶</span>
                  <div style={{ flex: 1 }}>
                    <strong style={{ fontSize: '1rem' }}>{g.name}</strong>
                    <span className="admin-badge" style={{ marginLeft: '0.5rem' }}>{g.category_name}</span>
                    {g.is_required && <span className="admin-badge" style={{ marginLeft: '0.35rem', background: '#dbeafe', color: '#1e40af' }}>Required</span>}
                    {g.requires_image && <span className="admin-badge" style={{ marginLeft: '0.35rem', background: '#fef3c7', color: '#92400e' }}>Image Upload</span>}
                    {!g.active && <span className="admin-badge" style={{ marginLeft: '0.35rem', background: '#fee2e2', color: '#991b1b' }}>Inactive</span>}
                    {g.description && <div style={{ fontSize: '0.82rem', color: 'var(--color-text-muted)', marginTop: 2 }}>{g.description}</div>}
                  </div>
                  <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>{opts.length} option{opts.length !== 1 ? 's' : ''}</span>
                  <button type="button" className="btn btn-secondary" style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }} onClick={e => { e.stopPropagation(); openEditGroup(g) }}>Edit</button>
                  <button type="button" className="btn btn-secondary" style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem', color: 'var(--color-error)' }} onClick={e => { e.stopPropagation(); handleDeleteGroup(g.id, g.name) }}>Delete</button>
                </div>

                {/* Expanded: options list */}
                {isOpen && (
                  <div style={{ borderTop: '1px solid var(--color-border)', padding: '0.75rem 1.25rem 1rem', background: 'var(--color-bg)' }}>
                    {opts.length === 0 && <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem', margin: '0 0 0.5rem' }}>No options yet. Add items the customer can select from.</p>}
                    {opts.length > 0 && (
                      <table className="admin-table" style={{ marginBottom: '0.75rem', fontSize: '0.9rem' }}>
                        <thead><tr><th>Option</th><th>Price</th><th>Active</th><th></th></tr></thead>
                        <tbody>
                          {opts.map(o => (
                            <tr key={o.id}>
                              <td>
                                <strong>{o.name}</strong>
                                {o.description && <div style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>{o.description}</div>}
                              </td>
                              <td>${Number(o.price).toFixed(2)}</td>
                              <td>{o.active ? 'Yes' : 'No'}</td>
                              <td>
                                <button type="button" className="btn btn-secondary" style={{ padding: '0.25rem 0.5rem', fontSize: '0.78rem', marginRight: '0.35rem' }} onClick={() => openEditOpt(g.id, o)}>Edit</button>
                                <button type="button" className="btn btn-secondary" style={{ padding: '0.25rem 0.5rem', fontSize: '0.78rem', color: 'var(--color-error)' }} onClick={() => handleDeleteOpt(g.id, o.id, o.name)}>Delete</button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    )}

                    {/* Option form */}
                    {optFormFor === g.id ? (
                      <form onSubmit={submitOpt} style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
                        <div className="form-group" style={{ margin: 0, flex: '1 1 160px' }}><label style={{ fontSize: '0.82rem' }}>Name *</label>
                          <input value={optForm.name} onChange={e => setOptForm(f => ({ ...f, name: e.target.value }))} placeholder="e.g. Single Vision Lens" required style={{ fontSize: '0.88rem', padding: '0.4rem 0.6rem' }} />
                        </div>
                        <div className="form-group" style={{ margin: 0, flex: '1 1 160px' }}><label style={{ fontSize: '0.82rem' }}>Description</label>
                          <input value={optForm.description} onChange={e => setOptForm(f => ({ ...f, description: e.target.value }))} style={{ fontSize: '0.88rem', padding: '0.4rem 0.6rem' }} />
                        </div>
                        <div className="form-group" style={{ margin: 0, flex: '0 0 100px' }}><label style={{ fontSize: '0.82rem' }}>Price</label>
                          <input type="number" step="0.01" min="0" value={optForm.price} onChange={e => setOptForm(f => ({ ...f, price: e.target.value }))} style={{ fontSize: '0.88rem', padding: '0.4rem 0.6rem' }} />
                        </div>
                        <button type="submit" className="btn btn-primary" disabled={saving} style={{ padding: '0.45rem 0.85rem', fontSize: '0.85rem' }}>{editOptId ? 'Update' : 'Add'}</button>
                        <button type="button" className="btn btn-secondary" style={{ padding: '0.45rem 0.85rem', fontSize: '0.85rem' }} onClick={() => setOptFormFor(null)}>Cancel</button>
                      </form>
                    ) : (
                      <button type="button" className="btn btn-primary" style={{ padding: '0.4rem 0.85rem', fontSize: '0.85rem' }} onClick={() => openNewOpt(g.id)}>+ Add option</button>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
