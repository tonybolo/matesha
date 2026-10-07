import { useState } from 'react'
import { Tex } from '../components/Tex'

function Bar({ cells, parts }: { cells: number; parts: { count: number; cls: string }[] }) {
  const W = 320
  const w = W / cells
  let idx = 0
  const fills: string[] = Array(cells).fill('')
  for (const p of parts) for (let i = 0; i < p.count && idx < cells; i++) fills[idx++] = p.cls
  return (
    <svg viewBox={`0 0 ${W + 4} 44`} className="bar" role="img" aria-label={`Полоска из ${cells} долей`}>
      {fills.map((cls, i) => (
        <rect key={i} x={2 + i * w} y={2} width={w} height={40} rx={4} className={`cell ${cls}`} />
      ))}
    </svg>
  )
}

function Stepper({ label, value, min, max, onChange }: { label: string; value: number; min: number; max: number; onChange: (n: number) => void }) {
  return (
    <div className="stepper">
      <span className="muted">{label}</span>
      <button className="key" onClick={() => onChange(Math.max(min, value - 1))} disabled={value <= min} aria-label={`${label}: меньше`}>
        −
      </button>
      <strong>{value}</strong>
      <button className="key" onClick={() => onChange(Math.min(max, value + 1))} disabled={value >= max} aria-label={`${label}: больше`}>
        +
      </button>
    </div>
  )
}

const BASES: [number, number][] = [
  [1, 2],
  [2, 3],
  [3, 4],
]

function Equal() {
  const [bi, setBi] = useState(0)
  const [k, setK] = useState(1)
  const [n, d] = BASES[bi]
  return (
    <div className="viz">
      <div className="viz-title">Режем доли на более мелкие — дробь не меняется</div>
      <div className="chips">
        {BASES.map(([a, b], i) => (
          <button key={i} className={`chip wide ${i === bi ? 'on' : ''}`} onClick={() => { setBi(i); setK(1) }}>
            <Tex tex={`\\frac{${a}}{${b}}`} />
          </button>
        ))}
      </div>
      <Bar cells={d * k} parts={[{ count: n * k, cls: 'a' }]} />
      <Stepper label="Разрезать каждую долю на" value={k} min={1} max={6} onChange={setK} />
      <div className="readout">
        <Tex display tex={`\\frac{${n}}{${d}}=\\frac{${n}\\cdot ${k}}{${d}\\cdot ${k}}=\\frac{${n * k}}{${d * k}}`} />
        <span className="muted">Закрашенная часть полоски одна и та же.</span>
      </div>
    </div>
  )
}

function AddSame() {
  const [c, setC] = useState(7)
  const [a, setA] = useState(2)
  const [b, setB] = useState(3)
  const clampA = (v: number) => Math.min(v, c - b)
  const aa = clampA(a)
  return (
    <div className="viz">
      <div className="viz-title">Одинаковые доли — складываем только количество</div>
      <Bar cells={c} parts={[{ count: aa, cls: 'a' }, { count: b, cls: 'b' }]} />
      <div className="steppers">
        <Stepper label="Всего долей" value={c} min={4} max={10} onChange={(v) => { setC(v); setB(Math.min(b, v - 1)); setA((p) => Math.min(p, v - Math.min(b, v - 1))) }} />
        <Stepper label="Синих" value={aa} min={1} max={c - b} onChange={setA} />
        <Stepper label="Оранжевых" value={b} min={1} max={c - aa} onChange={setB} />
      </div>
      <div className="readout">
        <Tex display tex={`\\frac{${aa}}{${c}}+\\frac{${b}}{${c}}=\\frac{${aa}+${b}}{${c}}=\\frac{${aa + b}}{${c}}`} />
      </div>
    </div>
  )
}

export function BarsViz({ preset }: { preset?: string }) {
  return preset === 'addSame' ? <AddSame /> : <Equal />
}
