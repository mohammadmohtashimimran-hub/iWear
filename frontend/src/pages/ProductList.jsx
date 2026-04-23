import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { getProducts, getSettings, getCategories, getBrands } from '../api'
import { useCurrency } from '../CurrencyContext'

function HeroSvg() {
  return (
    <svg viewBox="0 0 200 80" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <defs>
        <linearGradient id="lens" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#818cf8" stopOpacity=".7" />
          <stop offset="100%" stopColor="#c084fc" stopOpacity=".25" />
        </linearGradient>
      </defs>
      <circle cx="60" cy="40" r="30" fill="url(#lens)" stroke="#fff" strokeWidth="3" />
      <circle cx="140" cy="40" r="30" fill="url(#lens)" stroke="#fff" strokeWidth="3" />
      <line x1="90" y1="40" x2="110" y2="40" stroke="#fff" strokeWidth="3" />
      <line x1="30" y1="36" x2="6" y2="30" stroke="#fff" strokeWidth="3" strokeLinecap="round" />
      <line x1="170" y1="36" x2="194" y2="30" stroke="#fff" strokeWidth="3" strokeLinecap="round" />
    </svg>
  )
}

function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="skeleton skeleton-card-img" />
      <div className="skeleton-card-body">
        <div className="skeleton skeleton-line w-80" />
        <div className="skeleton skeleton-line w-40" />
      </div>
    </div>
  )
}

export default function ProductList() {
  const { formatPrice } = useCurrency()
  const [products, setProducts] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [storeName, setStoreName] = useState('iWear')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [categories, setCategories] = useState([])
  const [brands, setBrands] = useState([])
  // Filter state
  const [categoryId, setCategoryId] = useState('')
  const [brandId, setBrandId] = useState('')
  const [minPrice, setMinPrice] = useState('')
  const [maxPrice, setMaxPrice] = useState('')
  const [sort, setSort] = useState('')
  const [search, setSearch] = useState('')

  useEffect(() => {
    getSettings().then(s => setStoreName(s.store_name || 'iWear')).catch(() => {})
    getCategories().then(setCategories).catch(() => setCategories([]))
    getBrands().then(setBrands).catch(() => setBrands([]))
  }, [])

  const queryParams = useMemo(() => {
    const p = { page, per_page: 12 }
    if (categoryId) p.category_id = categoryId
    if (brandId) p.brand_id = brandId
    if (minPrice) p.min_price = minPrice
    if (maxPrice) p.max_price = maxPrice
    if (sort) p.sort = sort
    if (search) p.search = search
    return p
  }, [page, categoryId, brandId, minPrice, maxPrice, sort, search])

  useEffect(() => {
    setLoading(true)
    setError(null)
    getProducts(queryParams)
      .then(data => {
        setProducts(data.items || [])
        setTotal(data.total || 0)
      })
      .catch(() => setError('Could not load products. Please try again.'))
      .finally(() => setLoading(false))
  }, [queryParams])

  // Reset page when filters change
  useEffect(() => { setPage(1) }, [categoryId, brandId, minPrice, maxPrice, sort, search])

  const totalPages = Math.ceil(total / 12) || 1

  const clearFilters = () => {
    setCategoryId(''); setBrandId(''); setMinPrice(''); setMaxPrice(''); setSort(''); setSearch('')
  }

  return (
    <div>
      {/* Hero */}
      <section className="hero">
        <div className="hero-inner">
          <div>
            <span className="hero-eyebrow">New Collection · 2026</span>
            <h1>See the world clearly. In style.</h1>
            <p>
              {storeName} brings you premium eyewear with prescription customisation,
              expertly crafted lenses, and cash-on-delivery convenience.
            </p>
            <div className="hero-actions">
              <a href="#shop" className="btn btn-primary">Shop frames</a>
              <Link to="/size-guide" className="btn btn-secondary">Find your fit</Link>
            </div>
            <div className="hero-meta">
              <div className="hero-meta-item">
                <strong>{total || '40+'}</strong>
                <span>Frames in stock</span>
              </div>
              <div className="hero-meta-item">
                <strong>5★</strong>
                <span>Lens options</span>
              </div>
              <div className="hero-meta-item">
                <strong>COD</strong>
                <span>Pay on delivery</span>
              </div>
            </div>
          </div>
          <div className="hero-visual">
            <div className="hero-visual-frame"><HeroSvg /></div>
          </div>
        </div>
      </section>

      <h2 className="section-title" id="shop">Browse the collection</h2>
      <p className="section-subtitle">{total} {total === 1 ? 'product' : 'products'} available</p>

      <div className="shop-layout">
        {/* Sidebar */}
        <aside className="filter-sidebar">
          <h3>Filters</h3>
          <div className="filter-group">
            <label htmlFor="search">Search</label>
            <input id="search" type="text" placeholder="Frame name…" value={search} onChange={e => setSearch(e.target.value)} />
          </div>
          <div className="filter-group">
            <label htmlFor="category">Category</label>
            <select id="category" value={categoryId} onChange={e => setCategoryId(e.target.value)}>
              <option value="">All categories</option>
              {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div className="filter-group">
            <label htmlFor="brand">Brand</label>
            <select id="brand" value={brandId} onChange={e => setBrandId(e.target.value)}>
              <option value="">All brands</option>
              {brands.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
            </select>
          </div>
          <div className="filter-group">
            <label>Price range</label>
            <div className="filter-price-row">
              <input type="number" placeholder="Min" value={minPrice} onChange={e => setMinPrice(e.target.value)} min="0" />
              <input type="number" placeholder="Max" value={maxPrice} onChange={e => setMaxPrice(e.target.value)} min="0" />
            </div>
          </div>
          <div className="filter-group">
            <label htmlFor="sort">Sort by</label>
            <select id="sort" value={sort} onChange={e => setSort(e.target.value)}>
              <option value="">Default</option>
              <option value="price_asc">Price — low to high</option>
              <option value="price_desc">Price — high to low</option>
              <option value="newest">Newest first</option>
            </select>
          </div>
          <button type="button" className="filter-clear" onClick={clearFilters}>Clear filters</button>
        </aside>

        {/* Grid */}
        <div>
          {error && <p className="form-error">{error}</p>}

          {loading && (
            <div className="product-grid">
              {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
            </div>
          )}

          {!loading && !error && products.length === 0 && (
            <div className="empty-state">
              <span className="empty-icon">○○</span>
              <p><strong>No products match your filters.</strong></p>
              <p>Try clearing them and browsing the full catalogue.</p>
            </div>
          )}

          {!loading && !error && products.length > 0 && (
            <>
              <div className="product-grid">
                {products.map(p => (
                  <article key={p.id} className="card">
                    <Link to={`/product/${p.id}`}>
                      {p.image_url ? (
                        <img src={p.image_url} alt={p.name} className="card-img" />
                      ) : (
                        <div className="card-img" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-text-soft)', fontSize: '0.9rem' }}>
                          No image
                        </div>
                      )}
                    </Link>
                    <div className="card-body">
                      <span className="pill pill-accent">In stock</span>
                      <h3 className="card-title">
                        <Link to={`/product/${p.id}`}>{p.name}</Link>
                      </h3>
                      <p className="card-price">
                        {formatPrice(p.price, p.price_pkr)}
                      </p>
                      <Link to={`/product/${p.id}`} className="btn btn-primary" style={{ marginTop: '0.6rem', fontSize: '0.86rem', padding: '0.55rem 1rem' }}>
                        View details
                      </Link>
                    </div>
                  </article>
                ))}
              </div>
              {totalPages > 1 && (
                <div className="pagination">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    disabled={page <= 1}
                    onClick={() => setPage(p => p - 1)}
                  >
                    ← Previous
                  </button>
                  <span style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>
                    Page {page} of {totalPages}
                  </span>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    disabled={page >= totalPages}
                    onClick={() => setPage(p => p + 1)}
                  >
                    Next →
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
