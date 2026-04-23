import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { getProduct, addToCart, createCart, addToMyCart, uploadAddonImage } from '../api'
import { useAuth } from '../AuthContext'
import { useCurrency } from '../CurrencyContext'

const CART_KEY = 'iwear_cart_id'

function getOrCreateCartId() {
  const id = typeof window !== 'undefined' ? localStorage.getItem(CART_KEY) : null
  return id ? parseInt(id, 10) : null
}

function setCartIdInStorage(id) {
  if (typeof window !== 'undefined' && id) localStorage.setItem(CART_KEY, String(id))
}

function AddonImageUpload({ groupId, addonImages, setAddonImages }) {
  const fileRef = useRef(null)
  const [dragging, setDragging] = useState(false)
  const entry = addonImages[groupId]
  const uploading = entry?.uploading

  const handleFile = useCallback(async (file) => {
    if (!file) return
    const previewUrl = URL.createObjectURL(file)
    setAddonImages(prev => ({ ...prev, [groupId]: { file, previewUrl, uploadedUrl: null, uploading: true, error: null } }))
    try {
      const res = await uploadAddonImage(file)
      setAddonImages(prev => ({ ...prev, [groupId]: { ...prev[groupId], uploadedUrl: res.image_url, uploading: false } }))
    } catch (err) {
      setAddonImages(prev => ({ ...prev, [groupId]: { ...prev[groupId], uploading: false, error: err.message } }))
    }
  }, [groupId, setAddonImages])

  const onDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files?.[0]
    if (file) handleFile(file)
  }, [handleFile])

  const removeImage = () => {
    if (entry?.previewUrl) URL.revokeObjectURL(entry.previewUrl)
    setAddonImages(prev => {
      const next = { ...prev }
      delete next[groupId]
      return next
    })
  }

  return (
    <div className="pdp-ag-upload-area">
      {entry?.previewUrl ? (
        <div className="pdp-ag-upload-preview">
          <img src={entry.previewUrl} alt="Uploaded" />
          <div className="pdp-ag-upload-overlay">
            {uploading ? (
              <span className="pdp-ag-upload-status">Uploading...</span>
            ) : entry.error ? (
              <span className="pdp-ag-upload-status error">{entry.error}</span>
            ) : (
              <span className="pdp-ag-upload-status success">Uploaded</span>
            )}
            <button type="button" className="pdp-ag-upload-remove" onClick={removeImage}>Remove</button>
          </div>
        </div>
      ) : (
        <div
          className={`pdp-ag-upload-drop${dragging ? ' dragging' : ''}`}
          onDragOver={e => { e.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          onClick={() => fileRef.current?.click()}
        >
          <span className="pdp-ag-upload-icon">📷</span>
          <span className="pdp-ag-upload-text">Upload your image</span>
          <span className="pdp-ag-upload-hint">Drag & drop or click to browse</span>
          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            style={{ display: 'none' }}
            onChange={e => { handleFile(e.target.files?.[0]); e.target.value = '' }}
          />
        </div>
      )}
    </div>
  )
}

/**
 * Manual prescription entry form for eyewear customers who prefer typing
 * their optical values instead of uploading a photo. Captures the standard
 * six fields per eye (sphere, cylinder, axis, add) plus pupillary distance.
 *
 * Values are stored into ``addonPrescriptions[groupId]`` in the parent
 * component and are considered to satisfy the same "prescription required"
 * gate as an uploaded image.
 */
function PrescriptionInputForm({ groupId, addonPrescriptions, setAddonPrescriptions }) {
  const entry = addonPrescriptions[groupId] || {}
  const update = (field, value) => {
    setAddonPrescriptions(prev => ({
      ...prev,
      [groupId]: { ...(prev[groupId] || {}), [field]: value },
    }))
  }
  const rowLabel = { fontSize: '0.78rem', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.03em' }
  const cellStyle = { display: 'flex', flexDirection: 'column', gap: '0.15rem' }
  const inputStyle = {
    width: '100%',
    padding: '0.45rem 0.6rem',
    fontFamily: 'inherit',
    fontSize: '0.88rem',
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-sm)',
    background: 'var(--color-surface)',
  }

  return (
    <div style={{ padding: '0.85rem 1rem', background: 'var(--color-surface-alt, #fafbfd)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border)' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr 1fr 1fr 1fr', gap: '0.6rem 0.85rem', alignItems: 'end' }}>
        <div />
        <div style={rowLabel}>Sphere (SPH)</div>
        <div style={rowLabel}>Cylinder (CYL)</div>
        <div style={rowLabel}>Axis</div>
        <div style={rowLabel}>Add</div>

        <div style={{ ...rowLabel, alignSelf: 'center' }}>Right (OD)</div>
        <div style={cellStyle}><input type="number" step="0.25" placeholder="-2.50" value={entry.od_sph ?? ''} onChange={e => update('od_sph', e.target.value)} style={inputStyle} /></div>
        <div style={cellStyle}><input type="number" step="0.25" placeholder="-0.75" value={entry.od_cyl ?? ''} onChange={e => update('od_cyl', e.target.value)} style={inputStyle} /></div>
        <div style={cellStyle}><input type="number" min="0" max="180" placeholder="90" value={entry.od_axis ?? ''} onChange={e => update('od_axis', e.target.value)} style={inputStyle} /></div>
        <div style={cellStyle}><input type="number" step="0.25" placeholder="+1.00" value={entry.od_add ?? ''} onChange={e => update('od_add', e.target.value)} style={inputStyle} /></div>

        <div style={{ ...rowLabel, alignSelf: 'center' }}>Left (OS)</div>
        <div style={cellStyle}><input type="number" step="0.25" placeholder="-2.25" value={entry.os_sph ?? ''} onChange={e => update('os_sph', e.target.value)} style={inputStyle} /></div>
        <div style={cellStyle}><input type="number" step="0.25" placeholder="-0.50" value={entry.os_cyl ?? ''} onChange={e => update('os_cyl', e.target.value)} style={inputStyle} /></div>
        <div style={cellStyle}><input type="number" min="0" max="180" placeholder="85" value={entry.os_axis ?? ''} onChange={e => update('os_axis', e.target.value)} style={inputStyle} /></div>
        <div style={cellStyle}><input type="number" step="0.25" placeholder="+1.00" value={entry.os_add ?? ''} onChange={e => update('os_add', e.target.value)} style={inputStyle} /></div>
      </div>
      <div style={{ display: 'flex', gap: '0.85rem', alignItems: 'end', marginTop: '0.85rem' }}>
        <div style={{ ...cellStyle, maxWidth: 140 }}>
          <div style={rowLabel}>PD (mm)</div>
          <input type="number" step="0.5" placeholder="63" value={entry.pd ?? ''} onChange={e => update('pd', e.target.value)} style={inputStyle} />
        </div>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.78rem', margin: 0, lineHeight: 1.4 }}>
          PD (pupillary distance) is the gap between your pupils in millimetres. You can find it on an existing prescription or measure it with a ruler.
        </p>
      </div>
    </div>
  )
}

/**
 * Combined prescription capture UI — offers a tab toggle between uploading
 * a photo of the prescription and typing the values manually. Either one
 * satisfies the "prescription required" gate for the addon group.
 */
function PrescriptionCapture({ groupId, addonImages, setAddonImages, addonPrescriptions, setAddonPrescriptions }) {
  const hasImage = !!addonImages[groupId]?.uploadedUrl
  const hasValues = !!addonPrescriptions[groupId] && Object.values(addonPrescriptions[groupId]).some(v => v !== '' && v != null)
  const [mode, setMode] = useState(hasValues ? 'values' : 'upload')

  const tabBtn = (key, label) => ({
    flex: 1,
    padding: '0.55rem 0.9rem',
    fontFamily: 'inherit',
    fontSize: '0.84rem',
    fontWeight: 600,
    background: mode === key ? 'var(--color-accent)' : 'var(--color-surface)',
    color: mode === key ? '#fff' : 'var(--color-text)',
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-sm)',
    cursor: 'pointer',
    transition: 'all .15s',
  })

  return (
    <div className="pdp-ag-upload-area">
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.85rem' }}>
        <button type="button" style={tabBtn('upload', 'upload')} onClick={() => setMode('upload')}>
          📷 Upload Image{hasImage ? ' ✓' : ''}
        </button>
        <button type="button" style={tabBtn('values', 'values')} onClick={() => setMode('values')}>
          ✏️ Enter Values{hasValues ? ' ✓' : ''}
        </button>
      </div>
      {mode === 'upload' ? (
        <AddonImageUpload groupId={groupId} addonImages={addonImages} setAddonImages={setAddonImages} />
      ) : (
        <PrescriptionInputForm groupId={groupId} addonPrescriptions={addonPrescriptions} setAddonPrescriptions={setAddonPrescriptions} />
      )}
      <p style={{ color: 'var(--color-text-muted)', fontSize: '0.78rem', marginTop: '0.6rem', marginBottom: 0 }}>
        {mode === 'upload'
          ? 'Upload a clear photo of your prescription, or switch to manual entry.'
          : 'Enter your prescription values, or switch to image upload.'}
      </p>
    </div>
  )
}

export default function ProductDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user, refreshCart, openDrawer } = useAuth()
  const { formatPrice, getPrice, currency } = useCurrency()
  const [product, setProduct] = useState(null)
  const [selectedVariant, setSelectedVariant] = useState(null)
  const [activeImg, setActiveImg] = useState(0)
  const [qty, setQty] = useState(1)
  const [selectedOptions, setSelectedOptions] = useState({})
  const [addonImages, setAddonImages] = useState({})
  const [addonPrescriptions, setAddonPrescriptions] = useState({})
  const [openGroup, setOpenGroup] = useState(null)
  const [adding, setAdding] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    setError(null)
    setSelectedOptions({})
    setAddonImages({})
    setAddonPrescriptions({})
    setOpenGroup(null)
    getProduct(id)
      .then(p => {
        setProduct(p)
        setActiveImg(0)
        if (p?.variants?.length) setSelectedVariant(p.variants[0])
      })
      .catch(() => {
        setProduct(null)
        setError('Product not found.')
      })
  }, [id])

  const selectOption = (groupId, option) => {
    setSelectedOptions(prev => {
      if (prev[groupId]?.id === option.id) {
        const next = { ...prev }
        delete next[groupId]
        return next
      }
      return { ...prev, [groupId]: option }
    })
  }

  const handleAddToCart = async () => {
    if (!product) return
    setAdding(true)
    setError(null)
    try {
      const v = selectedVariant || (product.variants && product.variants[0])
      const basePrice = v?.unit_price ?? product.price
      const addonsArr = Object.entries(selectedOptions).map(([groupId, opt]) => {
        const pres = addonPrescriptions[groupId]
        const hasPres = pres && Object.values(pres).some(x => x !== '' && x != null)
        return {
          addon_option_id: opt.id,
          image_url: addonImages[groupId]?.uploadedUrl || null,
          // Manual prescription values are serialised into the cart line
          // notes so the admin can see them on the order detail page until
          // the full prescription_records flow is wired into checkout.
          prescription: hasPres ? pres : null,
        }
      })
      const addonsPriceTotal = Object.values(selectedOptions).reduce(
        (sum, o) => sum + (o?.price || 0), 0,
      )
      const unitPrice = (Number(basePrice) || 0) + addonsPriceTotal
      const payload = {
        productVariantId: v?.id || null,
        productId: v ? undefined : product.id,
        quantity: qty,
        unitPrice,
        addons: addonsArr,
      }
      if (user) {
        await addToMyCart(payload)
        refreshCart()
      } else {
        // Guest flow — reuse the cart from localStorage if we have one,
        // otherwise create a fresh cart. If the stored cart has already
        // been converted (status != active) or deleted, fall through to
        // create a new cart and retry once.
        const addGuestItem = async () => {
          let cartId = getOrCreateCartId()
          if (!cartId) {
            const created = await createCart()
            cartId = created.id
            setCartIdInStorage(cartId)
          }
          try {
            await addToCart(cartId, payload)
          } catch (err) {
            if (err?.status === 400 || err?.status === 404) {
              // Stale cart (converted or deleted) — clear and retry once.
              if (typeof window !== 'undefined') localStorage.removeItem(CART_KEY)
              const fresh = await createCart()
              setCartIdInStorage(fresh.id)
              await addToCart(fresh.id, payload)
            } else {
              throw err
            }
          }
        }
        await addGuestItem()
      }
      refreshCart()
      openDrawer()
    } catch (e) {
      setError(e.message || 'Failed to add to cart.')
    } finally {
      setAdding(false)
    }
  }

  if (error && !product) {
    return (
      <div className="empty-state">
        <p>{error}</p>
        <Link to="/">Back to shop</Link>
      </div>
    )
  }

  if (!product) return <div className="loading">Loading product...</div>

  const images = product.images || []
  const addonGroups = (product.addons || []).filter(g => g.options && g.options.length > 0)
  const variant = selectedVariant || (product.variants && product.variants[0])
  const basePrice = getPrice(variant?.unit_price ?? product.price, variant?.unit_price_pkr ?? product.price_pkr)
  const addonsTotal = Object.values(selectedOptions).reduce((sum, o) => sum + getPrice(o?.price || 0, o?.price_pkr), 0)
  const totalPrice = (Number(basePrice) || 0) + addonsTotal

  // A "requires prescription" addon is satisfied by EITHER an uploaded image
  // OR a completed manual prescription form — the customer picks whichever
  // is more convenient.
  const hasPrescriptionValues = (groupId) => {
    const v = addonPrescriptions[groupId]
    if (!v) return false
    return Object.values(v).some(x => x !== '' && x != null)
  }
  const imageUploadPending = addonGroups.some(g =>
    g.requires_image
    && selectedOptions[g.id]
    && !addonImages[g.id]?.uploadedUrl
    && !hasPrescriptionValues(g.id)
  )

  return (
    <div style={{ maxWidth: 960, margin: '0 auto' }}>
      {/* Breadcrumb */}
      <nav style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', marginBottom: '1.25rem' }}>
        <Link to="/" style={{ color: 'var(--color-text-muted)' }}>Shop</Link>
        <span style={{ margin: '0 0.5rem' }}>/</span>
        <span style={{ color: 'var(--color-text)' }}>{product.name}</span>
      </nav>

      <div className="pdp-grid">
        {/* Left - Image gallery */}
        <div className="pdp-gallery">
          <div className="pdp-main-img">
            {images.length > 0 ? (
              <img src={images[activeImg]?.image_url} alt={product.name} key={images[activeImg]?.id} />
            ) : (
              <div className="pdp-no-img">No image available</div>
            )}
          </div>
          {images.length > 1 && (
            <div className="pdp-thumbs">
              {images.map((img, idx) => (
                <button key={img.id} type="button" className={`pdp-thumb${idx === activeImg ? ' active' : ''}`} onClick={() => setActiveImg(idx)}>
                  <img src={img.image_url} alt="" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Right - Product info */}
        <div className="pdp-info">
          <h1 className="pdp-title">{product.name}</h1>

          {product.description && (
            <p className="pdp-description" style={{ whiteSpace: 'pre-line' }}>{product.description}</p>
          )}

          <div className="pdp-price">
            {addonsTotal > 0 ? (
              <>
                <span style={{ fontSize: '0.9rem', fontWeight: 400, color: 'var(--color-text-muted)', textDecoration: 'line-through', marginRight: '0.5rem' }}>
                  {formatPrice(variant?.unit_price ?? product.price, variant?.unit_price_pkr ?? product.price_pkr)}
                </span>
                {formatPrice(totalPrice, totalPrice)}
              </>
            ) : (
              formatPrice(variant?.unit_price ?? product.price, variant?.unit_price_pkr ?? product.price_pkr)
            )}
          </div>

          <div className="pdp-divider" />

          {/* Variant selector */}
          {product.variants?.length > 1 && (
            <div className="form-group" style={{ marginBottom: '1.25rem' }}>
              <label>Variant</label>
              <div className="pdp-variant-chips">
                {product.variants.map(v => (
                  <button key={v.id} type="button" className={`pdp-chip${selectedVariant?.id === v.id ? ' active' : ''}`} onClick={() => setSelectedVariant(v)}>
                    {v.sku}
                    {v.color && <span className="pdp-chip-sub">{v.color}</span>}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Addon groups */}
          {addonGroups.length > 0 && (
            <div style={{ marginBottom: '1.25rem' }}>
              <label style={{ display: 'block', fontWeight: 600, marginBottom: '0.5rem', fontSize: '0.95rem' }}>Customize your product</label>
              <div className="pdp-addon-groups">
                {addonGroups.map(g => {
                  const isOpen = openGroup === g.id
                  const chosen = selectedOptions[g.id]
                  const needsImage = g.requires_image && chosen
                  const imgEntry = addonImages[g.id]
                  return (
                    <div key={g.id} className="pdp-ag">
                      {/* Group header */}
                      <button
                        type="button"
                        className={`pdp-ag-header${chosen ? ' has-selection' : ''}`}
                        onClick={() => setOpenGroup(isOpen ? null : g.id)}
                      >
                        <div className="pdp-ag-left">
                          <span className="pdp-ag-arrow" style={{ transform: isOpen ? 'rotate(90deg)' : 'rotate(0)' }}>&#9654;</span>
                          <div>
                            <span className="pdp-ag-name">
                              {g.name}
                              {g.is_required && <span className="pdp-ag-req">Required</span>}
                              {g.requires_image && <span className="pdp-ag-req" style={{ background: '#fef3c7', color: '#92400e' }}>Image</span>}
                            </span>
                            {g.description && <span className="pdp-ag-desc">{g.description}</span>}
                          </div>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          {needsImage && (imgEntry?.uploadedUrl || hasPrescriptionValues(g.id)) && <span style={{ color: '#16a34a', fontSize: '0.78rem', fontWeight: 600 }}>Prescription added</span>}
                          {chosen ? (
                            <span className="pdp-ag-chosen">{chosen.name} &mdash; +{formatPrice(chosen.price, chosen.price_pkr)}</span>
                          ) : (
                            <span className="pdp-ag-choose">Select</span>
                          )}
                        </div>
                      </button>

                      {/* Expanded options */}
                      {isOpen && (
                        <div className="pdp-ag-options">
                          {g.options.map(o => {
                            const isSelected = chosen?.id === o.id
                            return (
                              <label key={o.id} className={`pdp-ao-card${isSelected ? ' selected' : ''}`}>
                                <input type="radio" name={`addon-${g.id}`} checked={isSelected} onChange={() => selectOption(g.id, o)} style={{ display: 'none' }} />
                                <div className="pdp-ao-radio">{isSelected && <div className="pdp-ao-dot" />}</div>
                                <div className="pdp-ao-body">
                                  <span className="pdp-ao-name">{o.name}</span>
                                  {o.description && <span className="pdp-ao-desc">{o.description}</span>}
                                </div>
                                <span className="pdp-ao-price">{getPrice(o.price, o.price_pkr) > 0 ? `+${formatPrice(o.price, o.price_pkr)}` : 'Free'}</span>
                              </label>
                            )
                          })}

                          {/* Prescription capture (either image upload or manual values) */}
                          {needsImage && (
                            <PrescriptionCapture
                              groupId={g.id}
                              addonImages={addonImages}
                              setAddonImages={setAddonImages}
                              addonPrescriptions={addonPrescriptions}
                              setAddonPrescriptions={setAddonPrescriptions}
                            />
                          )}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Quantity + Add to cart */}
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: '0.75rem', flexWrap: 'wrap' }}>
            <div className="form-group" style={{ margin: 0 }}>
              <label>Quantity</label>
              <div className="pdp-qty">
                <button type="button" onClick={() => setQty(q => Math.max(1, q - 1))} disabled={qty <= 1}>&#8722;</button>
                <input type="number" min={1} value={qty} onChange={e => setQty(Math.max(1, parseInt(e.target.value, 10) || 1))} />
                <button type="button" onClick={() => setQty(q => q + 1)}>+</button>
              </div>
            </div>
            <button
              type="button"
              className="btn btn-primary pdp-add-btn"
              onClick={handleAddToCart}
              disabled={adding || imageUploadPending}
              title={imageUploadPending ? 'Please upload required image(s) first' : undefined}
            >
              {adding ? 'Adding...' : `Add to cart \u2014 ${formatPrice(totalPrice * qty, totalPrice * qty)}`}
            </button>
          </div>

          {imageUploadPending && (
            <p style={{ fontSize: '0.82rem', color: '#b45309', marginTop: '0.5rem' }}>
              Please upload the required image(s) above before adding to cart.
            </p>
          )}

          {/* Selected addons summary */}
          {Object.keys(selectedOptions).length > 0 && (
            <div className="pdp-selection-summary">
              <strong>Selected addons:</strong>
              {Object.entries(selectedOptions).map(([gId, opt]) => {
                const group = addonGroups.find(g => g.id === Number(gId))
                return (
                  <div key={gId} className="pdp-sel-row">
                    <span>{group?.name}: <strong>{opt.name}</strong></span>
                    <span>+{formatPrice(opt.price, opt.price_pkr)}</span>
                  </div>
                )
              })}
              <div className="pdp-sel-row pdp-sel-total">
                <span>Total</span>
                <span>{formatPrice(totalPrice, totalPrice)}</span>
              </div>
            </div>
          )}

          {error && <p className="form-error" style={{ marginTop: '0.75rem' }}>{error}</p>}

          <div className="pdp-divider" />

          {/* Size guide link */}
          <Link to="/size-guide" className="pdp-size-link">
            <span>&#128208;</span> Not sure about your size? <strong>View Size Guide</strong>
          </Link>

          <div className="pdp-divider" />

          {/* Trust badges */}
          <div className="pdp-trust">
            <div className="pdp-trust-item"><span className="pdp-trust-icon">&#128666;</span><div><strong>Cash on Delivery</strong><span>Pay when you receive</span></div></div>
            <div className="pdp-trust-item"><span className="pdp-trust-icon">&#128260;</span><div><strong>Easy Returns</strong><span>7-day return policy</span></div></div>
            <div className="pdp-trust-item"><span className="pdp-trust-icon">&#10003;</span><div><strong>Authentic</strong><span>100% genuine product</span></div></div>
          </div>
        </div>
      </div>
    </div>
  )
}
