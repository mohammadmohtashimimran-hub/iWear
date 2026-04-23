import { useState, useEffect, useCallback } from 'react'
import {
  getCountries, createCountry, updateCountry, deleteCountry,
  getCities, createCity, updateCity, deleteCity,
} from '../../api'

export default function AdminLocations() {
  const [countries, setCountries] = useState([])
  const [cities, setCities] = useState([])
  const [selectedCountry, setSelectedCountry] = useState(null)
  const [loading, setLoading] = useState(true)

  const [newCountry, setNewCountry] = useState('')
  const [editCountryId, setEditCountryId] = useState(null)
  const [editCountryName, setEditCountryName] = useState('')

  const [newCity, setNewCity] = useState('')
  const [editCityId, setEditCityId] = useState(null)
  const [editCityName, setEditCityName] = useState('')

  const [busy, setBusy] = useState(false)

  const loadCountries = useCallback(async () => {
    const data = await getCountries()
    setCountries(data || [])
  }, [])

  const loadCities = useCallback(async (countryId) => {
    if (!countryId) { setCities([]); return }
    const data = await getCities(countryId)
    setCities(data || [])
  }, [])

  useEffect(() => {
    loadCountries().finally(() => setLoading(false))
  }, [loadCountries])

  useEffect(() => {
    loadCities(selectedCountry)
  }, [selectedCountry, loadCities])

  const handleCreateCountry = async (e) => {
    e.preventDefault()
    if (!newCountry.trim()) return
    setBusy(true)
    try {
      await createCountry(newCountry.trim())
      setNewCountry('')
      await loadCountries()
    } catch (err) { alert(err.message) }
    finally { setBusy(false) }
  }

  const handleUpdateCountry = async (id) => {
    if (!editCountryName.trim()) return
    setBusy(true)
    try {
      await updateCountry(id, editCountryName.trim())
      setEditCountryId(null)
      await loadCountries()
      if (selectedCountry === id) loadCities(id)
    } catch (err) { alert(err.message) }
    finally { setBusy(false) }
  }

  const handleDeleteCountry = async (id, name) => {
    if (!window.confirm(`Delete "${name}" and all its cities?`)) return
    try {
      await deleteCountry(id)
      if (selectedCountry === id) { setSelectedCountry(null); setCities([]) }
      await loadCountries()
    } catch (err) { alert(err.message) }
  }

  const handleCreateCity = async (e) => {
    e.preventDefault()
    if (!newCity.trim() || !selectedCountry) return
    setBusy(true)
    try {
      await createCity(newCity.trim(), selectedCountry)
      setNewCity('')
      await loadCities(selectedCountry)
    } catch (err) { alert(err.message) }
    finally { setBusy(false) }
  }

  const handleUpdateCity = async (id) => {
    if (!editCityName.trim()) return
    setBusy(true)
    try {
      await updateCity(id, editCityName.trim())
      setEditCityId(null)
      await loadCities(selectedCountry)
    } catch (err) { alert(err.message) }
    finally { setBusy(false) }
  }

  const handleDeleteCity = async (id, name) => {
    if (!window.confirm(`Delete city "${name}"?`)) return
    try {
      await deleteCity(id)
      await loadCities(selectedCountry)
    } catch (err) { alert(err.message) }
  }

  if (loading) return <div className="loading">Loading...</div>

  return (
    <div>
      <div className="admin-header">
        <h1>Countries &amp; Cities</h1>
      </div>
      <p style={{ color: 'var(--color-text-muted)', margin: '-0.75rem 0 1.25rem', fontSize: '0.9rem' }}>
        Manage the countries and cities available for customer checkout.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', alignItems: 'start' }}>
        {/* Countries */}
        <div className="card" style={{ padding: '1.25rem' }}>
          <h3 style={{ margin: '0 0 0.75rem', fontSize: '1rem', fontWeight: 600 }}>Countries</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', marginBottom: '0.75rem' }}>
            {countries.length === 0 && <span style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>No countries yet</span>}
            {countries.map(c => (
              <div
                key={c.id}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.5rem',
                  padding: '0.4rem 0.5rem', borderBottom: '1px solid var(--color-border)',
                  borderRadius: 4, cursor: 'pointer',
                  background: selectedCountry === c.id ? 'rgba(14,165,233,.08)' : 'transparent',
                }}
                onClick={() => { setSelectedCountry(c.id); setEditCountryId(null) }}
              >
                {editCountryId === c.id ? (
                  <>
                    <input
                      value={editCountryName}
                      onChange={e => setEditCountryName(e.target.value)}
                      onKeyDown={e => e.key === 'Enter' && handleUpdateCountry(c.id)}
                      onClick={e => e.stopPropagation()}
                      style={{ flex: 1, padding: '0.35rem 0.5rem', fontSize: '0.9rem', border: '1px solid var(--color-accent)', borderRadius: 4, outline: 'none' }}
                      autoFocus
                    />
                    <button type="button" className="btn btn-primary" style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }} onClick={(e) => { e.stopPropagation(); handleUpdateCountry(c.id) }} disabled={busy}>Save</button>
                    <button type="button" className="btn btn-secondary" style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }} onClick={(e) => { e.stopPropagation(); setEditCountryId(null) }}>Cancel</button>
                  </>
                ) : (
                  <>
                    <span style={{ flex: 1, fontSize: '0.9rem', fontWeight: selectedCountry === c.id ? 600 : 400 }}>{c.name}</span>
                    <button type="button" className="btn btn-secondary" style={{ padding: '0.25rem 0.5rem', fontSize: '0.78rem' }} onClick={(e) => { e.stopPropagation(); setEditCountryId(c.id); setEditCountryName(c.name) }}>Edit</button>
                    <button type="button" className="btn btn-secondary" style={{ padding: '0.25rem 0.5rem', fontSize: '0.78rem', color: 'var(--color-error)' }} onClick={(e) => { e.stopPropagation(); handleDeleteCountry(c.id, c.name) }}>Delete</button>
                  </>
                )}
              </div>
            ))}
          </div>
          <form onSubmit={handleCreateCountry} style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              value={newCountry}
              onChange={e => setNewCountry(e.target.value)}
              placeholder="New country name"
              style={{ flex: 1, padding: '0.4rem 0.6rem', fontSize: '0.9rem', border: '1px solid var(--color-border)', borderRadius: 4 }}
            />
            <button type="submit" className="btn btn-primary" style={{ padding: '0.4rem 0.85rem', fontSize: '0.85rem' }} disabled={busy || !newCountry.trim()}>
              Add
            </button>
          </form>
        </div>

        {/* Cities */}
        <div className="card" style={{ padding: '1.25rem' }}>
          <h3 style={{ margin: '0 0 0.75rem', fontSize: '1rem', fontWeight: 600 }}>
            Cities
            {selectedCountry && (
              <span style={{ fontWeight: 400, fontSize: '0.85rem', color: 'var(--color-text-muted)', marginLeft: '0.5rem' }}>
                — {countries.find(c => c.id === selectedCountry)?.name}
              </span>
            )}
          </h3>

          {!selectedCountry ? (
            <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>Select a country to manage its cities.</p>
          ) : (
            <>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', marginBottom: '0.75rem' }}>
                {cities.length === 0 && <span style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>No cities yet</span>}
                {cities.map(c => (
                  <div key={c.id} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.4rem 0', borderBottom: '1px solid var(--color-border)' }}>
                    {editCityId === c.id ? (
                      <>
                        <input
                          value={editCityName}
                          onChange={e => setEditCityName(e.target.value)}
                          onKeyDown={e => e.key === 'Enter' && handleUpdateCity(c.id)}
                          style={{ flex: 1, padding: '0.35rem 0.5rem', fontSize: '0.9rem', border: '1px solid var(--color-accent)', borderRadius: 4, outline: 'none' }}
                          autoFocus
                        />
                        <button type="button" className="btn btn-primary" style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }} onClick={() => handleUpdateCity(c.id)} disabled={busy}>Save</button>
                        <button type="button" className="btn btn-secondary" style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }} onClick={() => setEditCityId(null)}>Cancel</button>
                      </>
                    ) : (
                      <>
                        <span style={{ flex: 1, fontSize: '0.9rem' }}>{c.name}</span>
                        <button type="button" className="btn btn-secondary" style={{ padding: '0.25rem 0.5rem', fontSize: '0.78rem' }} onClick={() => { setEditCityId(c.id); setEditCityName(c.name) }}>Edit</button>
                        <button type="button" className="btn btn-secondary" style={{ padding: '0.25rem 0.5rem', fontSize: '0.78rem', color: 'var(--color-error)' }} onClick={() => handleDeleteCity(c.id, c.name)}>Delete</button>
                      </>
                    )}
                  </div>
                ))}
              </div>
              <form onSubmit={handleCreateCity} style={{ display: 'flex', gap: '0.5rem' }}>
                <input
                  value={newCity}
                  onChange={e => setNewCity(e.target.value)}
                  placeholder="New city name"
                  style={{ flex: 1, padding: '0.4rem 0.6rem', fontSize: '0.9rem', border: '1px solid var(--color-border)', borderRadius: 4 }}
                />
                <button type="submit" className="btn btn-primary" style={{ padding: '0.4rem 0.85rem', fontSize: '0.85rem' }} disabled={busy || !newCity.trim()}>
                  Add
                </button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
