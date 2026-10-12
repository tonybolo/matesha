const defaultFormat = (v: number) => String(Math.round(v * 100) / 100).replace('.', ',').replace('-', '−')

/** Число с кнопками «−» и «+» (удобнее ползунка на телефоне). */
export function Stepper({
  label,
  aria,
  value,
  min,
  max,
  step,
  onChange,
  format = defaultFormat,
  compact = false,
}: {
  label?: string
  aria?: string
  value: number
  min: number
  max: number
  step: number
  onChange: (n: number) => void
  format?: (n: number) => string
  compact?: boolean
}) {
  return (
    <span className={`stepper ${compact ? 'compact' : ''}`}>
      {label && <span className="muted">{label}</span>}
      <button className="key" onClick={() => onChange(Math.max(min, Math.round((value - step) * 100) / 100))} disabled={value <= min} aria-label={`${label ?? aria ?? 'число'}: меньше`}>
        −
      </button>
      <strong>{format(value)}</strong>
      <button className="key" onClick={() => onChange(Math.min(max, Math.round((value + step) * 100) / 100))} disabled={value >= max} aria-label={`${label ?? aria ?? 'число'}: больше`}>
        +
      </button>
    </span>
  )
}
