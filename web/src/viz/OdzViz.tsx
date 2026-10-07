import { useMemo, useState } from 'react'
import { Tex } from '../components/Tex'
import { tryParse } from '../lib/expr'

type Frac = { key: string; tex: string; num: string; den: string; bad: number[]; why: string }

const FRACS: Frac[] = [
  { key: 'a', tex: '\\frac{x+1}{x-2}', num: 'x+1', den: 'x-2', bad: [2], why: 'x-2=0 при x=2' },
  { key: 'b', tex: '\\frac{5}{x^2-9}', num: '5', den: 'x^2-9', bad: [-3, 3], why: 'x²-9=0 при x=3 и x=-3' },
  { key: 'c', tex: '\\frac{x}{x^2+1}', num: 'x', den: 'x^2+1', bad: [], why: 'x²+1 всегда больше нуля' },
]

const MIN = -6
const MAX = 6
const W = 360
const px = (x: number) => 18 + ((x - MIN) / (MAX - MIN)) * (W - 36)
const fmt = (v: number) => String(Math.round(v * 1000) / 1000).replace('.', ',').replace('-', '−')

export function OdzViz() {
  const [fi, setFi] = useState(0)
  const [x, setX] = useState(0)
  const f = FRACS[fi]
  const num = useMemo(() => tryParse(f.num)!, [f])
  const den = useMemo(() => tryParse(f.den)!, [f])
  const n = num.fn({ x })
  const d = den.fn({ x })
  const broken = d === 0

  return (
    <div className="viz odz">
      <div className="viz-title">Рулетка: когда дробь «ломается»</div>
      <div className="chips">
        {FRACS.map((c, i) => (
          <button
            key={c.key}
            className={`chip wide ${i === fi ? 'on' : ''}`}
            onClick={() => {
              setFi(i)
              setX(0)
            }}
            aria-label={`Дробь ${i + 1}`}
          >
            <Tex tex={c.tex} />
          </button>
        ))}
      </div>
      <svg viewBox={`0 0 ${W} 74`} className="numline" role="img" aria-label="Числовая прямая">
        <line x1={14} x2={W - 14} y1={38} y2={38} stroke="currentColor" strokeWidth={2} opacity={0.6} />
        {Array.from({ length: MAX - MIN + 1 }, (_, i) => MIN + i).map((t) => (
          <g key={t}>
            <line x1={px(t)} x2={px(t)} y1={33} y2={43} stroke="currentColor" opacity={0.5} />
            <text x={px(t)} y={62} textAnchor="middle" fontSize={11} fill="currentColor" opacity={0.7}>
              {t < 0 ? `−${-t}` : t}
            </text>
          </g>
        ))}
        {f.bad.map((b) => (
          <g key={b}>
            <circle cx={px(b)} cy={38} r={7} fill="var(--bg)" stroke="var(--bad)" strokeWidth={3} />
            <text x={px(b)} y={20} textAnchor="middle" fontSize={11} fontWeight={700} fill="var(--bad)">
              ≠ {b < 0 ? `−${-b}` : b}
            </text>
          </g>
        ))}
        <g transform={`translate(${px(x)},0)`} className={broken ? 'marker boom' : 'marker'}>
          <path d="M0 33 L-7 20 L7 20 Z" fill={broken ? 'var(--bad)' : 'var(--accent)'} />
        </g>
      </svg>
      <input
        className="slider"
        type="range"
        min={MIN}
        max={MAX}
        step={0.5}
        value={x}
        onChange={(e) => setX(Number(e.target.value))}
        aria-label="Значение x"
      />
      <div className={`readout ${broken ? 'bad' : ''}`} aria-live="polite">
        <div>
          <strong>x = {fmt(x)}</strong>
        </div>
        {broken ? (
          <div>
            Знаменатель равен <strong>0</strong> → делить нельзя 💥 Дробь не имеет смысла.
          </div>
        ) : (
          <div>
            Числитель {n === null ? '?' : fmt(n)}, знаменатель {d === null ? '?' : fmt(d)} → значение дроби{' '}
            <strong>{n !== null && d !== null ? fmt(n / d) : '?'}</strong>
          </div>
        )}
      </div>
      <div className="viz-actions">
        {f.bad.length > 0 && (
          <button className="btn small ghost" onClick={() => setX(f.bad[0])}>
            Показать запретную точку
          </button>
        )}
        <span className="muted">{f.why}</span>
      </div>
    </div>
  )
}
