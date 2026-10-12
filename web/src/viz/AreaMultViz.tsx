import { useState } from 'react'
import { Tex } from '../components/Tex'
import { Stepper } from './Stepper'

const SIZE = 240
const OFF = 34
const gcd = (a: number, b: number): number => (b === 0 ? a : gcd(b, a % b))
const PRESETS: [number, number, number, number][] = [
  [2, 3, 3, 4],
  [1, 2, 1, 3],
  [3, 4, 2, 5],
  [2, 3, 3, 5],
]

/** Умножение дробей как площадь пересечения: p/q столбцов и r/s строк единичного квадрата. */
export function AreaMultViz() {
  const [[p, q, r, s], setV] = useState<[number, number, number, number]>(PRESETS[0])
  const set = (i: number, v: number) =>
    setV(([P, Q, R, S]) => {
      const next: [number, number, number, number] = [P, Q, R, S]
      next[i] = v
      next[0] = Math.min(next[0], next[1])
      next[2] = Math.min(next[2], next[3])
      return next
    })
  const cw = SIZE / q
  const ch = SIZE / s
  const num = p * r
  const den = q * s
  const g = gcd(num, den)
  return (
    <div className="viz">
      <div className="viz-title">Умножаем дроби: сколько клеточек закрашено дважды?</div>
      <div className="chips">
        {PRESETS.map((pr) => (
          <button key={pr.join()} className={`chip wide ${pr.join() === [p, q, r, s].join() ? 'on' : ''}`} onClick={() => setV(pr)}>
            <Tex tex={`\\dfrac{${pr[0]}}{${pr[1]}}\\cdot\\dfrac{${pr[2]}}{${pr[3]}}`} />
          </button>
        ))}
      </div>
      <svg viewBox={`0 0 ${SIZE + OFF + 16} ${SIZE + OFF + 16}`} className="rug" role="img" aria-label={`Квадрат разрезан на ${q} столбцов и ${s} строк, дважды закрашено ${num} клеток из ${den}`}>
        <rect x={OFF} y={OFF} width={p * cw} height={SIZE} className="am-col" />
        <rect x={OFF} y={OFF} width={SIZE} height={r * ch} className="am-row" />
        <rect x={OFF} y={OFF} width={p * cw} height={r * ch} className="am-both" />
        {Array.from({ length: q + 1 }, (_, i) => (
          <line key={`v${i}`} x1={OFF + i * cw} x2={OFF + i * cw} y1={OFF} y2={OFF + SIZE} className="grid" />
        ))}
        {Array.from({ length: s + 1 }, (_, j) => (
          <line key={`h${j}`} y1={OFF + j * ch} y2={OFF + j * ch} x1={OFF} x2={OFF + SIZE} className="grid" />
        ))}
        <text x={OFF + (p * cw) / 2} y={OFF - 10} textAnchor="middle" fontSize={15} fontWeight={700} className="am-label-col">
          {p}/{q}
        </text>
        <text x={OFF - 8} y={OFF + (r * ch) / 2} textAnchor="end" dominantBaseline="middle" fontSize={15} fontWeight={700} className="am-label-row">
          {r}/{s}
        </text>
      </svg>
      <div className="readout" aria-live="polite">
        <Tex
          tex={`\\dfrac{${p}}{${q}}\\cdot\\dfrac{${r}}{${s}}=\\dfrac{${p}\\cdot ${r}}{${q}\\cdot ${s}}=\\dfrac{${num}}{${den}}${g > 1 ? `=\\dfrac{${num / g}}{${den / g}}` : ''}`}
          display
        />
        Дважды закрашено <strong>{num}</strong> клеточек из <strong>{den}</strong>.
      </div>
      <div className="steppers">
        <div className="frac-row">
          <span className="muted">1-я дробь</span>
          <Stepper compact aria="числитель" value={p} min={1} max={q} step={1} onChange={(v) => set(0, v)} format={String} />
          <span className="slash" aria-hidden>/</span>
          <Stepper compact aria="знаменатель" value={q} min={2} max={6} step={1} onChange={(v) => set(1, v)} format={String} />
        </div>
        <div className="frac-row">
          <span className="muted">2-я дробь</span>
          <Stepper compact aria="числитель" value={r} min={1} max={s} step={1} onChange={(v) => set(2, v)} format={String} />
          <span className="slash" aria-hidden>/</span>
          <Stepper compact aria="знаменатель" value={s} min={2} max={6} step={1} onChange={(v) => set(3, v)} format={String} />
        </div>
      </div>
    </div>
  )
}
