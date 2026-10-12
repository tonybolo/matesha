import { useState } from 'react'
import { Tex } from '../components/Tex'

const PRESETS: [number, number, number, number][] = [
  [5, 3, 4, 5],
  [3, 5, 2, 10],
  [4, 2, 3, 3],
]

function Stepper({ label, value, min, max, onChange }: { label: string; value: number; min: number; max: number; onChange: (n: number) => void }) {
  return (
    <span className="stepper">
      <span className="muted">{label}</span>
      <button className="key" onClick={() => onChange(Math.max(min, value - 1))} disabled={value <= min} aria-label={`${label}: меньше`}>
        −
      </button>
      <strong>{value}</strong>
      <button className="key" onClick={() => onChange(Math.min(max, value + 1))} disabled={value >= max} aria-label={`${label}: больше`}>
        +
      </button>
    </span>
  )
}

function Rug({ k, b, scale, x, label }: { k: number; b: number; scale: number; x: number; label: string }) {
  const cell = Math.sqrt(b) * scale
  const big = k * cell
  return (
    <g>
      {Array.from({ length: k * k }, (_, i) => (
        <rect key={i} x={x + (i % k) * cell} y={10 + Math.floor(i / k) * cell} width={cell} height={cell} className="mini-cell" />
      ))}
      <rect x={x} y={10} width={big} height={big} className="big-frame" />
      <text x={x + big / 2} y={10 + big + 16} textAnchor="middle" fontSize={12} fill="currentColor">
        {label}
      </text>
    </g>
  )
}

/** Внести множитель под корень: a√b — это большой квадрат из a×a ковриков площадью b. */
export function BringInViz() {
  const [[a, b, c, d], setV] = useState(PRESETS[0])
  const set = (i: number, v: number) => setV((p) => p.map((x, j) => (j === i ? v : x)) as [number, number, number, number])
  const s1 = a * Math.sqrt(b)
  const s2 = c * Math.sqrt(d)
  const scale = 130 / Math.max(s1, s2)
  const A = a * a * b
  const B = c * c * d
  const sign = A < B ? '<' : A > B ? '>' : '='
  return (
    <div className="viz">
      <div className="viz-title">Сложим коврики в один большой квадрат</div>
      <div className="chips">
        {PRESETS.map((p, i) => (
          <button key={i} className={`chip wide ${p.join() === [a, b, c, d].join() ? 'on' : ''}`} onClick={() => setV(p)}>
            <Tex tex={`${p[0]}\\sqrt{${p[1]}}\\ \\text{и}\\ ${p[2]}\\sqrt{${p[3]}}`} />
          </button>
        ))}
      </div>
      <div className="steppers">
        <Stepper label="a" value={a} min={1} max={7} onChange={(v) => set(0, v)} />
        <Stepper label="b" value={b} min={2} max={10} onChange={(v) => set(1, v)} />
        <Stepper label="c" value={c} min={1} max={7} onChange={(v) => set(2, v)} />
        <Stepper label="d" value={d} min={2} max={10} onChange={(v) => set(3, v)} />
      </div>
      <svg viewBox="0 0 320 170" className="rug" role="img" aria-label="Два больших квадрата из одинаковых ковриков">
        <Rug k={a} b={b} scale={scale} x={10} label={`${a}×${a} ковриков по ${b}`} />
        <Rug k={c} b={d} scale={scale} x={170} label={`${c}×${c} ковриков по ${d}`} />
      </svg>
      <div className="readout" aria-live="polite">
        <Tex display tex={`(${a}\\sqrt{${b}})^2=${a}^2\\cdot ${b}=${A}\\qquad (${c}\\sqrt{${d}})^2=${c}^2\\cdot ${d}=${B}`} />
        Площадь больше у {A > B ? 'первого' : A < B ? 'второго' : 'обоих поровну'}, поэтому <Tex tex={`${a}\\sqrt{${b}}\\ ${sign}\\ ${c}\\sqrt{${d}}`} />
      </div>
    </div>
  )
}
