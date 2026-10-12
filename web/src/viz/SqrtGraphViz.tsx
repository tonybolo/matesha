import { useState } from 'react'
import { Tex } from '../components/Tex'
import { Stepper } from './Stepper'

const W = 340
const H = 260
const X0 = 0
const X1 = 17
const Y0 = -2
const Y1 = 8
const sx = (x: number) => 20 + ((x - X0) / (X1 - X0)) * (W - 30)
const sy = (y: number) => 10 + ((Y1 - y) / (Y1 - Y0)) * (H - 24)
const fmt = (v: number) => String(Math.round(v * 100) / 100).replace('.', ',').replace('-', '−')

const PRESETS: { k: number; b: number; tex: string }[] = [
  { k: -0.5, b: 4, tex: '\\sqrt{x}=4-\\dfrac{x}{2}' },
  { k: -1 / 3, b: 6, tex: '\\sqrt{x}=6-\\dfrac{x}{3}' },
  { k: 0.25, b: 0.75, tex: '\\sqrt{x}=\\dfrac{3}{4}+\\dfrac{x}{4}' },
  { k: -1, b: 2, tex: '\\sqrt{x}=2-x' },
]

/** График y = √x и прямая y = kx + b: корни уравнения √x = kx + b — абсциссы точек пересечения. */
export function SqrtGraphViz() {
  const [[k, b], setV] = useState<[number, number]>([PRESETS[0].k, PRESETS[0].b])
  const set = (i: number, v: number) => setV(([p, q]) => (i === 0 ? [v, q] : [p, v]))
  // √x = kx + b  ⇒ t = √x ≥ 0:  k t² − t + b = 0
  const pts: { x: number; y: number }[] = []
  const roots: number[] = []
  if (Math.abs(k) < 1e-9) roots.push(b)
  else {
    const D = 1 - 4 * k * b
    if (D >= 0) roots.push((1 - Math.sqrt(D)) / (2 * k), (1 + Math.sqrt(D)) / (2 * k))
  }
  for (const t of roots) if (t >= -1e-9) pts.push({ x: t * t, y: t })
  const uniq = pts.filter((p, i) => pts.findIndex((q) => Math.abs(q.x - p.x) < 1e-6) === i)
  const curve: string[] = []
  for (let x = 0; x <= X1 + 1e-9; x += 0.1) curve.push(`${sx(x).toFixed(1)},${sy(Math.sqrt(x)).toFixed(1)}`)
  const lineY = (x: number) => k * x + b
  return (
    <div className="viz">
      <div className="viz-title">Графическое решение: √x = kx + b</div>
      <div className="chips">
        {PRESETS.map((pr) => (
          <button key={pr.tex} className={`chip wide ${Math.abs(pr.k - k) < 1e-6 && Math.abs(pr.b - b) < 1e-6 ? 'on' : ''}`} onClick={() => setV([pr.k, pr.b])}>
            <Tex tex={pr.tex} />
          </button>
        ))}
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="rug" role="img" aria-label="Графики корня и прямой">
        {Array.from({ length: X1 - X0 + 1 }, (_, i) => X0 + i).map((x) => (
          <line key={`v${x}`} x1={sx(x)} x2={sx(x)} y1={10} y2={H - 14} className="grid" />
        ))}
        {Array.from({ length: Y1 - Y0 + 1 }, (_, i) => Y0 + i).map((y) => (
          <line key={`h${y}`} y1={sy(y)} y2={sy(y)} x1={20} x2={W - 10} className="grid" />
        ))}
        <line x1={20} x2={W - 10} y1={sy(0)} y2={sy(0)} className="axis" />
        <line y1={10} y2={H - 14} x1={sx(0)} x2={sx(0)} className="axis" />
        {[0, 4, 9, 16].map((x) => (
          <text key={x} x={sx(x)} y={sy(0) + 12} textAnchor="middle" fontSize={9} fill="currentColor" opacity={0.7}>
            {x}
          </text>
        ))}
        <polyline points={curve.join(' ')} fill="none" className="curve" />
        <line x1={sx(0)} y1={sy(lineY(0))} x2={sx(X1)} y2={sy(lineY(X1))} className="line2" />
        {uniq.map((p, i) => (
          <circle key={i} cx={sx(p.x)} cy={sy(p.y)} r={6} className="root" />
        ))}
      </svg>
      <div className="readout" aria-live="polite">
        {uniq.length === 0 ? (
          <>Графики не пересекаются: у уравнения нет корней.</>
        ) : (
          <>
            Пересечения: {uniq.map((p) => `(${fmt(p.x)}; ${fmt(p.y)})`).join(', ')}. Значит {uniq.length > 1 ? 'корни' : 'корень'}: <strong>x = {uniq.map((p) => fmt(p.x)).join(' и ')}</strong>
          </>
        )}
      </div>
      <div className="steppers">
        <Stepper compact label="k" value={k} min={-2} max={2} step={0.25} onChange={(v) => set(0, v)} format={fmt} />
        <Stepper compact label="b" value={b} min={-3} max={8} step={0.5} onChange={(v) => set(1, v)} format={fmt} />
      </div>
    </div>
  )
}
