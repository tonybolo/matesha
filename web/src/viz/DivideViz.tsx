import { useState } from 'react'
import { Tex } from '../components/Tex'
import { Stepper } from './Stepper'

const X0 = 12
const UNIT = 100
const gcd = (a: number, b: number): number => (b === 0 ? a : gcd(b, a % b))
const PRESETS: [number, number, number, number][] = [
  [3, 4, 1, 4],
  [2, 1, 1, 3],
  [3, 4, 3, 8],
  [1, 2, 1, 6],
  [5, 6, 1, 3],
]

const fracTex = (n: number, d: number) => {
  const g = gcd(n, d)
  const [a, b] = [n / g, d / g]
  return b === 1 ? String(a) : `\\dfrac{${a}}{${b}}`
}

/** Деление как «сколько поместится»: полоска длиной a/b и кусочки по c/d. */
export function DivideViz() {
  const [[a, b, c, d], setV] = useState<[number, number, number, number]>(PRESETS[0])
  const set = (i: number, v: number) =>
    setV(([A, B, C, D]) => {
      const next: [number, number, number, number] = [A, B, C, D]
      next[i] = v
      next[0] = Math.min(next[0], 3 * next[1])
      return next
    })
  const total = a / b
  const piece = c / d
  const n = (a * d) / (b * c)
  const pieces: { start: number; len: number }[] = []
  for (let i = 0; i * piece < total - 1e-9; i++) pieces.push({ start: i * piece, len: Math.min(piece, total - i * piece) })
  const whole = Math.floor(n + 1e-9)
  const rest = n - whole
  return (
    <div className="viz">
      <div className="viz-title">Сколько кусочков поместится?</div>
      <div className="chips">
        {PRESETS.map((pr) => (
          <button key={pr.join()} className={`chip wide ${pr.join() === [a, b, c, d].join() ? 'on' : ''}`} onClick={() => setV(pr)}>
            <Tex tex={`${fracTex(pr[0], pr[1])}:${fracTex(pr[2], pr[3])}`} />
          </button>
        ))}
      </div>
      <svg viewBox={`0 0 ${3 * UNIT + 2 * X0} 120`} className="rug" role="img" aria-label={`В отрезок длиной ${a}/${b} помещается ${n} кусочков по ${c}/${d}`}>
        {[0, 1, 2, 3].map((t) => (
          <g key={t}>
            <line x1={X0 + t * UNIT} x2={X0 + t * UNIT} y1={14} y2={96} className="grid" />
            <text x={X0 + t * UNIT} y={112} textAnchor="middle" fontSize={11} fill="currentColor" opacity={0.7}>
              {t}
            </text>
          </g>
        ))}
        <rect x={X0} y={18} width={total * UNIT} height={26} className="dv-total" />
        <text x={X0 + (total * UNIT) / 2} y={36} textAnchor="middle" fontSize={13} fontWeight={700} fill="currentColor">
          {a}/{b}
        </text>
        {pieces.map((pc, i) => {
          const full = pc.len >= piece - 1e-9
          return (
            <g key={i}>
              <rect x={X0 + pc.start * UNIT} y={56} width={pc.len * UNIT} height={30} className={full ? 'dv-piece' : 'dv-part'} />
              {pc.len * UNIT > 14 && (
                <text x={X0 + (pc.start + pc.len / 2) * UNIT} y={76} textAnchor="middle" fontSize={12} fontWeight={700} fill="currentColor">
                  {full ? i + 1 : ''}
                </text>
              )}
            </g>
          )
        })}
      </svg>
      <div className="readout" aria-live="polite">
        <Tex tex={`${fracTex(a, b)}:${fracTex(c, d)}=${fracTex(a, b)}\\cdot ${fracTex(d, c)}=\\dfrac{${a}\\cdot ${d}}{${b}\\cdot ${c}}=${fracTex(a * d, b * c)}`} display />
        {rest < 1e-9 ? (
          <>
            Кусочков по <Tex tex={fracTex(c, d)} /> помещается ровно <strong>{whole}</strong>.
          </>
        ) : (
          <>
            Целых кусочков помещается <strong>{whole}</strong>, и ещё остаётся часть кусочка (на картинке она пунктиром).
          </>
        )}
      </div>
      <div className="steppers">
        <div className="frac-row">
          <span className="muted">Делимое</span>
          <Stepper compact aria="числитель" value={a} min={1} max={3 * b} step={1} onChange={(v) => set(0, v)} format={String} />
          <span className="slash" aria-hidden>/</span>
          <Stepper compact aria="знаменатель" value={b} min={1} max={6} step={1} onChange={(v) => set(1, v)} format={String} />
        </div>
        <div className="frac-row">
          <span className="muted">Делитель</span>
          <Stepper compact aria="числитель" value={c} min={1} max={6} step={1} onChange={(v) => set(2, v)} format={String} />
          <span className="slash" aria-hidden>/</span>
          <Stepper compact aria="знаменатель" value={d} min={1} max={6} step={1} onChange={(v) => set(3, v)} format={String} />
        </div>
      </div>
    </div>
  )
}
