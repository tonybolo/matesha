import { useMemo, useState } from 'react'
import { Tex } from '../components/Tex'

// ---------- Числовые доли ----------
const PAIRS: [[number, number], [number, number]][] = [
  [[1, 2], [1, 3]],
  [[1, 4], [1, 6]],
  [[2, 3], [1, 5]],
]

const gcd = (a: number, b: number): number => (b === 0 ? a : gcd(b, a % b))
const lcm = (a: number, b: number) => (a * b) / gcd(a, b)

function Bar({ cells, a, b }: { cells: number; a: number; b: number }) {
  const W = 320
  const w = W / cells
  return (
    <svg viewBox={`0 0 ${W + 4} 40`} className="bar small" role="img" aria-label={`Полоска из ${cells} долей`}>
      {Array.from({ length: cells }, (_, i) => (
        <rect key={i} x={2 + i * w} y={2} width={w} height={36} rx={4} className={`cell ${i < a ? 'a' : i < a + b ? 'b' : ''}`} />
      ))}
    </svg>
  )
}

function Numbers() {
  const [pi, setPi] = useState(0)
  const [phase, setPhase] = useState(0)
  const [[a, b], [c, d]] = PAIRS[pi]
  const L = lcm(b, d)
  const m1 = L / b
  const m2 = L / d

  return (
    <div className="viz">
      <div className="viz-title">Приводим доли к общему размеру</div>
      <div className="chips">
        {PAIRS.map(([[a1, b1], [c1, d1]], i) => (
          <button key={i} className={`chip wide ${i === pi ? 'on' : ''}`} onClick={() => { setPi(i); setPhase(0) }}>
            <Tex tex={`\\frac{${a1}}{${b1}}+\\frac{${c1}}{${d1}}`} />
          </button>
        ))}
      </div>
      {phase === 0 && (
        <>
          <Bar cells={b} a={a} b={0} />
          <Bar cells={d} a={0} b={c} />
          <p className="viz-msg">Доли разного размера: просто сложить количество нельзя.</p>
        </>
      )}
      {phase >= 1 && (
        <>
          <Bar cells={L} a={a * m1} b={0} />
          <Bar cells={L} a={0} b={c * m2} />
          <div className="readout">
            <Tex display tex={`\\frac{${a}}{${b}}=\\frac{${a}\\cdot ${m1}}{${b}\\cdot ${m1}}=\\frac{${a * m1}}{${L}},\\qquad \\frac{${c}}{${d}}=\\frac{${c}\\cdot ${m2}}{${d}\\cdot ${m2}}=\\frac{${c * m2}}{${L}}`} />
          </div>
        </>
      )}
      {phase >= 2 && (
        <>
          <Bar cells={L} a={a * m1} b={c * m2} />
          <div className="readout">
            <Tex display tex={`\\frac{${a * m1}}{${L}}+\\frac{${c * m2}}{${L}}=\\frac{${a * m1 + c * m2}}{${L}}`} />
          </div>
        </>
      )}
      <div className="viz-actions">
        {phase < 2 && (
          <button className="btn primary small" onClick={() => setPhase(phase + 1)}>
            {phase === 0 ? 'Разрезать на равные доли ▸' : 'Сложить ▸'}
          </button>
        )}
        {phase > 0 && (
          <button className="btn small ghost" onClick={() => setPhase(0)}>
            Заново
          </button>
        )}
      </div>
    </div>
  )
}

// ---------- Алгебраические знаменатели ----------
type Fr = { num: string; den: string[] }
type Preset = { expr: string; fracs: Fr[]; numerator: string; result: string }

const PRESETS: Preset[] = [
  {
    expr: '\\frac{3}{x-2}-\\frac{2}{x+2}',
    fracs: [
      { num: '3', den: ['x-2'] },
      { num: '2', den: ['x+2'] },
    ],
    numerator: '3(x+2)-2(x-2)=x+10',
    result: '\\frac{x+10}{x^2-4}',
  },
  {
    expr: '\\frac{2}{x^2-9}+\\frac{1}{x+3}',
    fracs: [
      { num: '2', den: ['x-3', 'x+3'] },
      { num: '1', den: ['x+3'] },
    ],
    numerator: '2+(x-3)=x-1',
    result: '\\frac{x-1}{x^2-9}',
  },
  {
    expr: '\\frac{1}{x}+\\frac{1}{y}',
    fracs: [
      { num: '1', den: ['x'] },
      { num: '1', den: ['y'] },
    ],
    numerator: 'y+x',
    result: '\\frac{x+y}{xy}',
  },
  {
    expr: '\\frac{5}{2a}+\\frac{3}{a^2}',
    fracs: [
      { num: '5', den: ['2', 'a'] },
      { num: '3', den: ['a', 'a'] },
    ],
    numerator: '5a+3\\cdot 2=5a+6',
    result: '\\frac{5a+6}{2a^2}',
  },
]

const count = (xs: string[], k: string) => xs.filter((x) => x === k).length

function lcdOf(dens: string[][]): string[] {
  const keys = [...new Set(dens.flat())]
  return keys.flatMap((k) => Array(Math.max(...dens.map((d) => count(d, k)))).fill(k) as string[])
}

function extraOf(lcd: string[], den: string[]): string[] {
  const left = [...den]
  const extra: string[] = []
  for (const k of lcd) {
    const i = left.indexOf(k)
    if (i >= 0) left.splice(i, 1)
    else extra.push(k)
  }
  return extra
}

const paren = (k: string) => (/[+-]/.test(k) ? `(${k})` : k)

function Tiles({ keys, order, dashed = false }: { keys: string[]; order: string[]; dashed?: boolean }) {
  if (keys.length === 0) return <span className="muted">1</span>
  return (
    <span className="tiles">
      {keys.map((k, i) => (
        <span key={i} className={`tile static c${order.indexOf(k) % 6} ${dashed ? 'dashed' : ''}`}>
          <Tex tex={paren(k)} />
        </span>
      ))}
    </span>
  )
}

function Algebra() {
  const [pi, setPi] = useState(0)
  const [phase, setPhase] = useState(0)
  const p = PRESETS[pi]
  const dens = p.fracs.map((f) => f.den)
  const lcd = useMemo(() => lcdOf(dens), [dens])
  const order = useMemo(() => [...new Set(dens.flat())], [dens])

  return (
    <div className="viz">
      <div className="viz-title">Общий знаменатель из «плиток»</div>
      <div className="chips">
        {PRESETS.map((q, i) => (
          <button key={i} className={`chip wide ${i === pi ? 'on' : ''}`} onClick={() => { setPi(i); setPhase(0) }}>
            <Tex tex={q.expr} />
          </button>
        ))}
      </div>
      <div className="readout">
        <Tex display tex={p.expr} />
      </div>
      <div className="denoms">
        <p className="muted">Знаменатели, разложенные на множители:</p>
        {p.fracs.map((f, i) => (
          <div key={i} className="den-row">
            <span className="muted">{i + 1}-я дробь:</span> <Tiles keys={f.den} order={order} />
          </div>
        ))}
      </div>
      {phase >= 1 && (
        <div className="denoms">
          <p className="muted">Общий знаменатель — все разные плитки, каждая в наибольшем количестве:</p>
          <div className="den-row">
            <Tiles keys={lcd} order={order} />
          </div>
        </div>
      )}
      {phase >= 2 && (
        <div className="denoms">
          <p className="muted">Чего не хватает каждой дроби — это её дополнительный множитель:</p>
          {p.fracs.map((f, i) => (
            <div key={i} className="den-row">
              <span className="muted">{i + 1}-я дробь: числитель ×</span> <Tiles keys={extraOf(lcd, f.den)} order={order} dashed />
            </div>
          ))}
        </div>
      )}
      {phase >= 3 && (
        <div className="readout">
          Числитель: <Tex tex={p.numerator} />
          <Tex display tex={`${p.expr}=${p.result}`} />
        </div>
      )}
      <div className="viz-actions">
        {phase < 3 && (
          <button className="btn primary small" onClick={() => setPhase(phase + 1)}>
            {['Найти общий знаменатель ▸', 'Найти дополнительные множители ▸', 'Сложить дроби ▸'][phase]}
          </button>
        )}
        {phase > 0 && (
          <button className="btn small ghost" onClick={() => setPhase(0)}>
            Заново
          </button>
        )}
      </div>
    </div>
  )
}

export function CommonDenomViz({ preset }: { preset?: string }) {
  return preset === 'algebra' ? <Algebra /> : <Numbers />
}
