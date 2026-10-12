import { useState } from 'react'
import { Tex } from '../components/Tex'

const MIN = -8
const MAX = 8
const W = 360
const px = (x: number) => 18 + ((x - MIN) / (MAX - MIN)) * (W - 36)
const fmt = (v: number) => String(Math.round(v * 100) / 100).replace('.', ',').replace('-', '−')

const PRESETS: [number, number][] = [
  [-16, 0],
  [4, 0],
  [1, -3],
  [-1, 5],
]

function Stepper({ label, value, min, max, onChange }: { label: string; value: number; min: number; max: number; onChange: (n: number) => void }) {
  return (
    <span className="stepper">
      <span className="muted">{label}</span>
      <button className="key" onClick={() => onChange(Math.max(min, value - 1))} disabled={value <= min} aria-label={`${label}: меньше`}>
        −
      </button>
      <strong>{fmt(value)}</strong>
      <button className="key" onClick={() => onChange(Math.min(max, value + 1))} disabled={value >= max} aria-label={`${label}: больше`}>
        +
      </button>
    </span>
  )
}

const poly = (a: number, b: number) => `${a === 1 ? '' : a === -1 ? '-' : a}x${b === 0 ? '' : b > 0 ? `+${b}` : `${b}`}`

/** Когда √(ax+b) существует: подкоренное число не может быть отрицательным. */
export function DomainViz() {
  const [[a, b], setV] = useState(PRESETS[0])
  const [x, setX] = useState(2)
  const set = (i: number, v: number) => setV(([p, q]) => (i === 0 ? [v === 0 ? 1 : v, q] : [p, v]))
  const boundary = -b / a
  const inner = a * x + b
  const ok = inner >= 0
  const from = a > 0 ? boundary : MIN
  const to = a > 0 ? MAX : boundary
  const clamp = (v: number) => Math.max(MIN, Math.min(MAX, v))
  return (
    <div className="viz">
      <div className="viz-title">Когда корень существует?</div>
      <div className="chips">
        {PRESETS.map(([p, q], i) => (
          <button key={i} className={`chip wide ${p === a && q === b ? 'on' : ''}`} onClick={() => setV([p, q])}>
            <Tex tex={`\\sqrt{${poly(p, q)}}`} />
          </button>
        ))}
      </div>
      <div className="steppers">
        <Stepper label="число при x" value={a} min={-9} max={9} onChange={(v) => set(0, v)} />
        <Stepper label="свободное число" value={b} min={-9} max={9} onChange={(v) => set(1, v)} />
      </div>
      <svg viewBox={`0 0 ${W} 70`} className="numline" role="img" aria-label="Числовая прямая: где корень существует">
        <line x1={14} x2={W - 14} y1={38} y2={38} stroke="currentColor" strokeWidth={2} opacity={0.6} />
        <rect x={px(clamp(from))} y={30} width={Math.max(0, px(clamp(to)) - px(clamp(from)))} height={16} className="good-zone" />
        {Array.from({ length: MAX - MIN + 1 }, (_, i) => MIN + i).map((t) => (
          <g key={t}>
            <line x1={px(t)} x2={px(t)} y1={34} y2={42} stroke="currentColor" opacity={0.5} />
            {t % 2 === 0 && (
              <text x={px(t)} y={62} textAnchor="middle" fontSize={11} fill="currentColor" opacity={0.7}>
                {t < 0 ? `−${-t}` : t}
              </text>
            )}
          </g>
        ))}
        {boundary >= MIN && boundary <= MAX && <circle cx={px(boundary)} cy={38} r={6} fill="var(--accent)" stroke="var(--bg)" strokeWidth={2} />}
        <path d={`M${px(x)} 31 l-6 -12 h12 z`} fill={ok ? 'var(--ok)' : 'var(--bad)'} />
      </svg>
      <input className="slider" type="range" min={MIN} max={MAX} step={0.5} value={x} onChange={(e) => setX(Number(e.target.value))} aria-label="Значение x" />
      <div className={`readout ${ok ? '' : 'bad'}`} aria-live="polite">
        При <strong>x = {fmt(x)}</strong> под корнем получается <strong>{fmt(inner)}</strong>:{' '}
        {ok ? (
          <>
            корень существует, <Tex tex={`\\sqrt{${fmt(inner).replace('−', '-')}}`.replace(',', '{,}')} />
          </>
        ) : (
          <>отрицательное число, корня нет 💥</>
        )}
        <div className="muted">
          Зелёная полоса — подходящие значения: <Tex tex={`x\\ ${a > 0 ? '\\ge' : '\\le'}\\ ${fmt(boundary).replace('−', '-').replace(',', '{,}')}`} />
        </div>
      </div>
    </div>
  )
}
