import { useState } from 'react'
import { Tex } from '../components/Tex'

const W = 330
const H = 270
const X0 = 6
const Y0 = 9
const sx = (x: number) => (W / (2 * X0)) * (x + X0)
const sy = (y: number) => (H / (2 * Y0)) * (Y0 - y)
const fmt = (v: number) => String(Math.round(v * 100) / 100).replace('.', ',').replace('-', '−')

const PRESETS: [number, number, number][] = [
  [2, 3, -5],
  [1, -4, 4],
  [1, 2, 5],
  [1, -5, 0],
]

function Stepper({ label, value, min, max, step, onChange }: { label: string; value: number; min: number; max: number; step: number; onChange: (n: number) => void }) {
  return (
    <span className="stepper">
      <span className="muted">{label}</span>
      <button className="key" onClick={() => onChange(Math.max(min, value - step))} disabled={value <= min} aria-label={`${label}: меньше`}>
        −
      </button>
      <strong>{fmt(value)}</strong>
      <button className="key" onClick={() => onChange(Math.min(max, value + step))} disabled={value >= max} aria-label={`${label}: больше`}>
        +
      </button>
    </span>
  )
}

/** Парабола — «мяч»: сколько раз она касается «земли» (оси x)? Светофор дискриминанта. */
export function ParabolaViz() {
  const [[a, b, c], setV] = useState(PRESETS[0])
  const set = (i: number, v: number) => setV((p) => p.map((x, j) => (j === i ? v : x)) as [number, number, number])
  const D = b * b - 4 * a * c
  const pts: string[] = []
  for (let x = -X0; x <= X0 + 1e-9; x += 0.1) {
    const y = a * x * x + b * x + c
    pts.push(`${sx(x).toFixed(1)},${sy(Math.max(-Y0 - 2, Math.min(Y0 + 2, y))).toFixed(1)}`)
  }
  const roots = D > 0 ? [(-b - Math.sqrt(D)) / (2 * a), (-b + Math.sqrt(D)) / (2 * a)] : D === 0 ? [-b / (2 * a)] : []
  const sign = (v: number) => (v < 0 ? `-${-v}` : `+${v}`)
  const eq = `${a === 1 ? '' : a === -1 ? '-' : a}x^2${b === 0 ? '' : `${sign(b)}x`}${c === 0 ? '' : sign(c)}=0`
  return (
    <div className="viz">
      <div className="viz-title">Парабола как мяч: сколько раз коснётся земли?</div>
      <div className="chips">
        {PRESETS.map((p, i) => (
          <button key={i} className={`chip wide ${p.join() === [a, b, c].join() ? 'on' : ''}`} onClick={() => setV(p)}>
            <Tex tex={`${p[0] === 1 ? '' : p[0]}x^2${p[1] === 0 ? '' : (p[1] < 0 ? '-' : '+') + (Math.abs(p[1]) === 1 ? '' : Math.abs(p[1])) + 'x'}${p[2] === 0 ? '' : (p[2] < 0 ? '-' : '+') + Math.abs(p[2])}`} />
          </button>
        ))}
      </div>
      <div className="steppers">
        <Stepper label="a" value={a} min={-3} max={3} step={0.5} onChange={(v) => set(0, v === 0 ? 0.5 : v)} />
        <Stepper label="b" value={b} min={-8} max={8} step={1} onChange={(v) => set(1, v)} />
        <Stepper label="c" value={c} min={-8} max={8} step={1} onChange={(v) => set(2, v)} />
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="rug" role="img" aria-label="График параболы">
        {Array.from({ length: 2 * X0 + 1 }, (_, i) => i - X0).map((x) => (
          <line key={`vx${x}`} x1={sx(x)} x2={sx(x)} y1={0} y2={H} className="grid" />
        ))}
        {Array.from({ length: 2 * Y0 + 1 }, (_, i) => i - Y0).map((y) => (
          <line key={`hy${y}`} y1={sy(y)} y2={sy(y)} x1={0} x2={W} className="grid" />
        ))}
        <line x1={0} x2={W} y1={sy(0)} y2={sy(0)} className="axis ground" />
        <line y1={0} y2={H} x1={sx(0)} x2={sx(0)} className="axis" />
        <text x={W - 4} y={sy(0) - 4} textAnchor="end" fontSize={10} fill="currentColor" opacity={0.7}>
          земля (ось x)
        </text>
        <polyline points={pts.join(' ')} fill="none" className="curve" />
        {roots.map((r, i) => (
          <circle key={i} cx={sx(r)} cy={sy(0)} r={6} className="root" />
        ))}
      </svg>
      <div className="light-row" aria-live="polite">
        <span className={`light ${D < 0 ? 'on bad' : ''}`} title="нет корней" />
        <span className={`light ${D === 0 ? 'on mid' : ''}`} title="один корень" />
        <span className={`light ${D > 0 ? 'on good' : ''}`} title="два корня" />
        <span>
          <Tex tex={eq} />: <Tex tex={`D=${b}^2-4\\cdot ${a < 0 ? `(${a})` : a}\\cdot ${c < 0 ? `(${c})` : c}=${fmt(D)}`} />
          {' '}
          {D > 0 ? <strong>два корня: {roots.map(fmt).join(' и ')}</strong> : D === 0 ? <strong>один корень: {fmt(roots[0])}</strong> : <strong>корней нет</strong>}
        </span>
      </div>
    </div>
  )
}
