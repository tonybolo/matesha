import { useState } from 'react'
import { Tex } from '../components/Tex'
import { Stepper } from './Stepper'

const R = 6.5
const PX = 26
const SIZE = 2 * R * PX
const sx = (x: number) => SIZE / 2 + x * PX
const sy = (y: number) => SIZE / 2 - y * PX
const fmt = (v: number) => String(Math.round(v * 100) / 100).replace('.', ',').replace('-', '−')

type Preset = { k: number; m: number; c: number; tex: string }
const PRESETS: Preset[] = [
  { k: 4, m: 1, c: -3, tex: '\\dfrac{4}{x}=x-3' },
  { k: 4, m: 4, c: 0, tex: '\\dfrac{4}{x}=4x' },
  { k: 6, m: 1, c: 1, tex: '\\dfrac{6}{x}=x+1' },
  { k: -1, m: 1, c: -2, tex: '-\\dfrac{1}{x}=x-2' },
]
const K_PRESETS = [2, 6, 12, -4, -12]

function branch(k: number, sign: 1 | -1): string {
  const segs: string[] = []
  let cur = ''
  for (let i = 1; i <= 130; i++) {
    const x = sign * i * 0.05
    const y = k / x
    if (Math.abs(y) > 12) {
      if (cur) segs.push(cur)
      cur = ''
      continue
    }
    cur += `${cur ? 'L' : 'M'}${sx(x).toFixed(1)},${sy(y).toFixed(1)}`
  }
  if (cur) segs.push(cur)
  return segs.join('')
}

function crossings(k: number, m: number, c: number): number[] {
  if (m === 0) return c === 0 ? [] : [k / c]
  const D = c * c + 4 * m * k
  if (D < -1e-9) return []
  if (Math.abs(D) < 1e-9) return [-c / (2 * m)]
  return [(-c - Math.sqrt(D)) / (2 * m), (-c + Math.sqrt(D)) / (2 * m)].sort((p, q) => p - q)
}

/** График y = k/x; в режиме line добавляется прямая y = mx + c, и видны точки пересечения. */
export function HyperbolaViz({ preset }: { preset?: string }) {
  const withLine = preset === 'line'
  const [k, setK] = useState(withLine ? PRESETS[0].k : 6)
  const [m, setM] = useState(PRESETS[0].m)
  const [c, setC] = useState(PRESETS[0].c)
  const changeK = (v: number) => setK(v === 0 ? (v > k ? 1 : -1) : v)
  const roots = withLine ? crossings(k, m, c) : []
  const pts = roots.map((x) => ({ x, y: m * x + c }))
  return (
    <div className="viz">
      <div className="viz-title">{withLine ? 'Гипербола и прямая: где они пересекаются?' : 'График обратной пропорциональности y = k/x'}</div>
      <div className="chips">
        {withLine
          ? PRESETS.map((pr) => (
              <button
                key={pr.tex}
                className={`chip wide ${pr.k === k && pr.m === m && pr.c === c ? 'on' : ''}`}
                onClick={() => {
                  setK(pr.k)
                  setM(pr.m)
                  setC(pr.c)
                }}
              >
                <Tex tex={pr.tex} />
              </button>
            ))
          : K_PRESETS.map((v) => (
              <button key={v} className={`chip ${v === k ? 'on' : ''}`} onClick={() => setK(v)}>
                k = {fmt(v)}
              </button>
            ))}
      </div>
      <svg viewBox={`0 0 ${SIZE} ${SIZE}`} className="rug" role="img" aria-label={withLine ? 'Гипербола и прямая' : `Гипербола y = ${k}/x`}>
        {Array.from({ length: 13 }, (_, i) => i - 6).map((t) => (
          <g key={t}>
            <line x1={sx(t)} x2={sx(t)} y1={0} y2={SIZE} className="grid" />
            <line y1={sy(t)} y2={sy(t)} x1={0} x2={SIZE} className="grid" />
          </g>
        ))}
        <line x1={0} x2={SIZE} y1={sy(0)} y2={sy(0)} className="axis" />
        <line y1={0} y2={SIZE} x1={sx(0)} x2={sx(0)} className="axis" />
        {[-4, -2, 2, 4, 6].map((t) => (
          <g key={t}>
            <text x={sx(t)} y={sy(0) + 11} textAnchor="middle" fontSize={9} fill="currentColor" opacity={0.7}>
              {t}
            </text>
            <text x={sx(0) - 4} y={sy(t) + 3} textAnchor="end" fontSize={9} fill="currentColor" opacity={0.7}>
              {t}
            </text>
          </g>
        ))}
        <path d={branch(k, 1)} fill="none" className="curve" />
        <path d={branch(k, -1)} fill="none" className="curve" />
        {withLine && <line x1={sx(-R)} y1={sy(m * -R + c)} x2={sx(R)} y2={sy(m * R + c)} className="line2" />}
        {pts.map((p, i) => (
          <circle key={i} cx={sx(p.x)} cy={sy(p.y)} r={6} className="root" />
        ))}
      </svg>
      <div className="readout" aria-live="polite">
        {!withLine ? (
          <>
            <Tex tex={`y=${k < 0 ? '-' : ''}\\dfrac{${Math.abs(k)}}{x}`} />:{' '}
            {k > 0 ? 'ветки в первой и третьей четвертях' : 'ветки во второй и четвёртой четвертях'}. Для любой точки графика <Tex tex={`x\\cdot y=${k}`} />, например{' '}
            {[1, 2, 3, 6].map((x) => `(${x}; ${fmt(k / x)})`).join(', ')}.
          </>
        ) : pts.length === 0 ? (
          <>Графики не пересекаются: у уравнения нет корней.</>
        ) : (
          <>
            {pts.length === 1 ? 'Прямая касается гиперболы' : 'Пересечения'}: {pts.map((p) => `(${fmt(p.x)}; ${fmt(p.y)})`).join(', ')}. Значит {pts.length > 1 ? 'корни' : 'корень'}:{' '}
            <strong>x = {pts.map((p) => fmt(p.x)).join(' и ')}</strong>
          </>
        )}
      </div>
      <div className="steppers">
        <Stepper compact label="k" value={k} min={-12} max={12} step={1} onChange={changeK} format={fmt} />
        {withLine && (
          <>
            <Stepper compact label="наклон" value={m} min={-4} max={4} step={1} onChange={setM} format={fmt} />
            <Stepper compact label="сдвиг" value={c} min={-6} max={6} step={1} onChange={setC} format={fmt} />
          </>
        )}
      </div>
    </div>
  )
}
