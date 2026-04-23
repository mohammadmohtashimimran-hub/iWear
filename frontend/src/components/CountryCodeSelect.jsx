export const COUNTRY_CODES = [
  { code: 'PK', name: 'Pakistan', dial: '+92' },
  { code: 'US', name: 'United States', dial: '+1' },
  { code: 'GB', name: 'United Kingdom', dial: '+44' },
  { code: 'AE', name: 'UAE', dial: '+971' },
  { code: 'SA', name: 'Saudi Arabia', dial: '+966' },
  { code: 'IN', name: 'India', dial: '+91' },
  { code: 'BD', name: 'Bangladesh', dial: '+880' },
  { code: 'CA', name: 'Canada', dial: '+1' },
  { code: 'AU', name: 'Australia', dial: '+61' },
  { code: 'DE', name: 'Germany', dial: '+49' },
  { code: 'FR', name: 'France', dial: '+33' },
  { code: 'CN', name: 'China', dial: '+86' },
  { code: 'JP', name: 'Japan', dial: '+81' },
  { code: 'KR', name: 'South Korea', dial: '+82' },
  { code: 'TR', name: 'Turkey', dial: '+90' },
  { code: 'MY', name: 'Malaysia', dial: '+60' },
  { code: 'SG', name: 'Singapore', dial: '+65' },
  { code: 'QA', name: 'Qatar', dial: '+974' },
  { code: 'KW', name: 'Kuwait', dial: '+965' },
  { code: 'OM', name: 'Oman', dial: '+968' },
  { code: 'BH', name: 'Bahrain', dial: '+973' },
  { code: 'EG', name: 'Egypt', dial: '+20' },
  { code: 'NG', name: 'Nigeria', dial: '+234' },
  { code: 'ZA', name: 'South Africa', dial: '+27' },
  { code: 'KE', name: 'Kenya', dial: '+254' },
  { code: 'BR', name: 'Brazil', dial: '+55' },
  { code: 'MX', name: 'Mexico', dial: '+52' },
  { code: 'IT', name: 'Italy', dial: '+39' },
  { code: 'ES', name: 'Spain', dial: '+34' },
  { code: 'NL', name: 'Netherlands', dial: '+31' },
  { code: 'SE', name: 'Sweden', dial: '+46' },
  { code: 'NO', name: 'Norway', dial: '+47' },
  { code: 'NZ', name: 'New Zealand', dial: '+64' },
  { code: 'PH', name: 'Philippines', dial: '+63' },
  { code: 'TH', name: 'Thailand', dial: '+66' },
  { code: 'ID', name: 'Indonesia', dial: '+62' },
  { code: 'LK', name: 'Sri Lanka', dial: '+94' },
  { code: 'NP', name: 'Nepal', dial: '+977' },
  { code: 'AF', name: 'Afghanistan', dial: '+93' },
  { code: 'IR', name: 'Iran', dial: '+98' },
]

export default function CountryCodeSelect({ value, onChange, style }) {
  return (
    <select
      value={value}
      onChange={e => onChange(e.target.value)}
      style={{
        width: 110,
        minWidth: 110,
        flexShrink: 0,
        ...style,
      }}
    >
      {COUNTRY_CODES.map(c => (
        <option key={c.code} value={c.dial}>
          {c.dial} {c.code}
        </option>
      ))}
    </select>
  )
}
