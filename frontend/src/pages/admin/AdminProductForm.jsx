import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import {
  getProductAdmin,
  createProductAdmin,
  updateProductAdmin,
  getCategories,
  getBrands,
  getTypes,
  uploadProductImages,
  deleteProductImage,
  setPrimaryImage,
} from '../../api'

const MAX_IMAGES = 10
const ACCEPTED = '.png,.jpg,.jpeg,.gif,.webp'

export default function AdminProductForm() {
  const { id } = useParams()
  const navigate = useNavigate()
  const isEdit = !!id
  const fileRef = useRef()

  const [categories, setCategories] = useState([])
  const [brands, setBrands] = useState([])
  const [types, setTypes] = useState([])
  const [form, setForm] = useState({
    name: '', slug: '', description: '', price: '', price_pkr: '', quantity: '',
    category_id: '', brand_id: '', type_id: '', active: true,
  })
  const [existingImages, setExistingImages] = useState([])
  const [newFiles, setNewFiles] = useState([])
  const [previews, setPreviews] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [dragOver, setDragOver] = useState(false)

  const totalCount = existingImages.length + newFiles.length

  useEffect(() => {
    Promise.all([getCategories(), getBrands(), getTypes()]).then(([c, b, t]) => {
      setCategories(c || [])
      setBrands(b || [])
      setTypes(t || [])
    })
  }, [])

  useEffect(() => {
    if (!isEdit) return
    getProductAdmin(id).then(p => {
      setForm({
        name: p.name || '', slug: p.slug || '', description: p.description || '',
        price: p.price != null ? p.price : '',
        price_pkr: p.price_pkr != null ? p.price_pkr : '',
        quantity: p.quantity != null ? p.quantity : 0,
        category_id: p.category_id || '', brand_id: p.brand_id || '',
        type_id: p.type_id || '', active: p.active !== false,
      })
      setExistingImages(p.images || [])
    }).catch(() => setError('Product not found'))
  }, [id, isEdit])

  useEffect(() => {
    const urls = newFiles.map(f => URL.createObjectURL(f))
    setPreviews(urls)
    return () => urls.forEach(u => URL.revokeObjectURL(u))
  }, [newFiles])

  const addFiles = useCallback((fileList) => {
    const arr = Array.from(fileList).filter(f => f.type.startsWith('image/'))
    const remaining = MAX_IMAGES - totalCount
    if (remaining <= 0) return
    setNewFiles(prev => [...prev, ...arr.slice(0, remaining)])
  }, [totalCount])

  const handleFileChange = (e) => {
    addFiles(e.target.files)
    e.target.value = ''
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    addFiles(e.dataTransfer.files)
  }

  const removeNewFile = (idx) => {
    setNewFiles(prev => prev.filter((_, i) => i !== idx))
  }

  const handleDeleteExisting = async (imageId) => {
    try {
      await deleteProductImage(id, imageId)
      setExistingImages(prev => {
        const remaining = prev.filter(i => i.id !== imageId)
        const deleted = prev.find(i => i.id === imageId)
        if (deleted?.is_primary && remaining.length > 0) {
          remaining[0].is_primary = true
        }
        return remaining
      })
    } catch {
      alert('Failed to delete image')
    }
  }

  const handleSetPrimary = async (imageId) => {
    try {
      await setPrimaryImage(id, imageId)
      setExistingImages(prev => prev.map(i => ({ ...i, is_primary: i.id === imageId })))
    } catch {
      alert('Failed to set primary image')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    const payload = {
      name: form.name.trim(),
      slug: form.slug.trim() || undefined,
      description: form.description || undefined,
      price: form.price !== '' ? Number(form.price) : 0,
      price_pkr: form.price_pkr !== '' ? Number(form.price_pkr) : null,
      quantity: form.quantity !== '' ? parseInt(form.quantity, 10) : 0,
      category_id: form.category_id ? parseInt(form.category_id, 10) : undefined,
      brand_id: form.brand_id ? parseInt(form.brand_id, 10) : undefined,
      type_id: form.type_id ? parseInt(form.type_id, 10) : undefined,
      active: form.active,
    }
    try {
      let productId = id
      if (isEdit) {
        await updateProductAdmin(id, payload)
      } else {
        const created = await createProductAdmin(payload)
        productId = created.id
      }
      if (newFiles.length > 0) {
        await uploadProductImages(productId, newFiles)
      }
      navigate('/admin/products')
    } catch (err) {
      setError(err.message || 'Failed to save')
    } finally {
      setLoading(false)
    }
  }

  if (isEdit && !form.name && !error) return <div className="loading">Loading…</div>

  return (
    <div>
      <div className="admin-header">
        <h1>{isEdit ? 'Edit product' : 'Add product'}</h1>
        <Link to="/admin/products" className="btn btn-secondary">← Back to list</Link>
      </div>
      {error && <p className="form-error" style={{ marginBottom: '1rem' }}>{error}</p>}

      <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', alignItems: 'start' }}>
        {/* Left column — product details */}
        <div className="card" style={{ padding: '1.5rem' }}>
          <h2 style={{ margin: '0 0 1rem', fontSize: '1.1rem', fontWeight: 600 }}>Product details</h2>
          <div className="form-group">
            <label>Name *</label>
            <input value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} required />
          </div>
          <div className="form-group">
            <label>Slug (optional)</label>
            <input value={form.slug} onChange={e => setForm(f => ({ ...f, slug: e.target.value }))} placeholder="auto from name" />
          </div>
          <div className="form-group">
            <label>Description</label>
            <textarea value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} rows={3} style={{ width: '100%', maxWidth: '100%' }} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <div className="form-group">
              <label>Price USD *</label>
              <input type="number" step="0.01" min="0" value={form.price} onChange={e => setForm(f => ({ ...f, price: e.target.value }))} required />
            </div>
            <div className="form-group">
              <label>Price PKR</label>
              <input type="number" step="1" min="0" value={form.price_pkr} onChange={e => setForm(f => ({ ...f, price_pkr: e.target.value }))} placeholder="e.g. 36120" />
            </div>
            <div className="form-group">
              <label>Stock quantity</label>
              <input type="number" min="0" step="1" value={form.quantity} onChange={e => setForm(f => ({ ...f, quantity: e.target.value }))} placeholder="0" />
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.75rem' }}>
            <div className="form-group">
              <label>Category</label>
              <select value={form.category_id} onChange={e => setForm(f => ({ ...f, category_id: e.target.value }))}>
                <option value="">—</option>
                {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Brand</label>
              <select value={form.brand_id} onChange={e => setForm(f => ({ ...f, brand_id: e.target.value }))}>
                <option value="">—</option>
                {brands.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Type</label>
              <select value={form.type_id} onChange={e => setForm(f => ({ ...f, type_id: e.target.value }))}>
                <option value="">—</option>
                {types.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
              </select>
            </div>
          </div>
          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input type="checkbox" checked={form.active} onChange={e => setForm(f => ({ ...f, active: e.target.checked }))} />
              Active (visible in store)
            </label>
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading} style={{ marginTop: '0.5rem' }}>
            {loading ? 'Saving…' : (isEdit ? 'Update product' : 'Create product')}
          </button>
        </div>

        {/* Right column — images */}
        <div className="card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600 }}>Images</h2>
            <span style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>
              {totalCount} / {MAX_IMAGES}
            </span>
          </div>

          {/* Existing images grid */}
          {existingImages.length > 0 && (
            <div className="img-grid">
              {existingImages.map(img => (
                <div key={img.id} className={`img-card${img.is_primary ? ' primary' : ''}`}>
                  <img src={img.image_url} alt={img.alt_text || ''} />
                  <div className="img-overlay">
                    <button type="button" title={img.is_primary ? 'Primary image' : 'Set as primary'}
                      onClick={() => !img.is_primary && handleSetPrimary(img.id)}
                      style={{ color: img.is_primary ? '#facc15' : '#fff' }}>
                      {img.is_primary ? '★' : '☆'}
                    </button>
                    <button type="button" title="Delete" onClick={() => handleDeleteExisting(img.id)}
                      style={{ color: '#f87171' }}>
                      ✕
                    </button>
                  </div>
                  {img.is_primary && <span className="img-badge badge-primary">Primary</span>}
                </div>
              ))}
            </div>
          )}

          {/* New files preview grid */}
          {previews.length > 0 && (
            <>
              {existingImages.length > 0 && (
                <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', margin: '0.75rem 0 0.5rem' }}>
                  New (will upload on save)
                </div>
              )}
              <div className="img-grid">
                {previews.map((url, idx) => (
                  <div key={idx} className="img-card">
                    <img src={url} alt="" />
                    <div className="img-overlay">
                      <span />
                      <button type="button" title="Remove" onClick={() => removeNewFile(idx)}
                        style={{ color: '#f87171' }}>
                        ✕
                      </button>
                    </div>
                    <span className="img-badge badge-new">New</span>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* Drop zone */}
          {totalCount < MAX_IMAGES && (
            <div
              className={`img-drop-zone${dragOver ? ' drag-over' : ''}`}
              onDragOver={e => { e.preventDefault(); setDragOver(true) }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileRef.current?.click()}
              style={{ marginTop: (existingImages.length > 0 || previews.length > 0) ? '0.75rem' : 0 }}
            >
              <input ref={fileRef} type="file" multiple accept={ACCEPTED} onChange={handleFileChange}
                style={{ display: 'none' }} />
              <div style={{ fontSize: '2rem', lineHeight: 1 }}>📷</div>
              <div style={{ fontWeight: 500 }}>
                {dragOver ? 'Drop images here' : 'Click or drag images here'}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                PNG, JPG, GIF, WebP — up to {MAX_IMAGES - totalCount} more
              </div>
            </div>
          )}
        </div>
      </form>
    </div>
  )
}
