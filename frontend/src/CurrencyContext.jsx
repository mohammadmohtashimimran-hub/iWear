import { createContext, useContext, useState, useCallback } from 'react'

const CurrencyContext = createContext(null)

const CURRENCIES = {
  USD: { code: 'USD', symbol: '$', label: 'USD ($)', position: 'before' },
  PKR: { code: 'PKR', symbol: 'Rs', label: 'PKR (Rs)', position: 'before' },
}

const PAKISTAN_COUNTRY_NAMES = ['pakistan', 'pk', 'pak']

export function CurrencyProvider({ children }) {
  const [currency, setCurrency] = useState('USD')

  const detectFromCountry = useCallback((countryName) => {
    if (!countryName) return
    const lower = countryName.toLowerCase().trim()
    if (PAKISTAN_COUNTRY_NAMES.some(n => lower.includes(n))) {
      setCurrency('PKR')
    } else {
      setCurrency('USD')
    }
  }, [])

  const formatPrice = useCallback((usdPrice, pkrPrice) => {
    if (currency === 'PKR' && pkrPrice != null) {
      return `Rs ${Number(pkrPrice).toLocaleString('en-PK', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
    }
    if (usdPrice == null) return '—'
    return `$${Number(usdPrice).toFixed(2)}`
  }, [currency])

  const getPrice = useCallback((usdPrice, pkrPrice) => {
    if (currency === 'PKR' && pkrPrice != null) return Number(pkrPrice)
    return Number(usdPrice) || 0
  }, [currency])

  const currencyInfo = CURRENCIES[currency]

  return (
    <CurrencyContext.Provider value={{
      currency, setCurrency, currencyInfo,
      formatPrice, getPrice, detectFromCountry,
      currencies: Object.values(CURRENCIES),
    }}>
      {children}
    </CurrencyContext.Provider>
  )
}

export function useCurrency() {
  const ctx = useContext(CurrencyContext)
  if (!ctx) throw new Error('useCurrency must be inside CurrencyProvider')
  return ctx
}
