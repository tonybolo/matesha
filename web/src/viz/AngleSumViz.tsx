import { useState, type ReactNode } from 'react'
import { Tex } from '../components/Tex'
import './AngleSumViz.css'

type P = [number, number]

const U = 20 // одна клетка = 20 пикселей
const W = 340
const H = 230
const NAMES = ['A', 'B', 'C', 'D']

const PRESETS: { label: string; pts: P[] }[] = [
  {
    label: 'Обычный',
    pts: [
      [3, 8],
      [12, 9],
      [15, 3],
      [4, 2],
    ],
  },
  {
    label: 'Параллелограмм',
    pts: [
      [3, 8],
      [11, 8],
      [15, 3],
      [7, 3],
    ],
  },
  {
    label: 'Трапеция',
    pts: [
      [2, 8],
      [14, 8],
      [11, 3],
      [5, 3],
    ],
  },
  {
    label: 'Прямоугольник',
    pts: [
      [3, 8],
      [14, 8],
      [14, 3],
      [3, 3],
    ],
  },
]

const sub = (a: P, b: P): P => [a[0] - b[0], a[1] - b[1]]
const cr = (a: P, b: P) => a[0] * b[1] - a[1] * b[0]
const dt = (a: P, b: P) => a[0] * b[0] + a[1] * b[1]
const ln = (a: P) => Math.hypot(a[0], a[1])
/** Угол при вершине v между лучами на a и на b, в градусах. */
const deg = (v: P, a: P, b: P) => {
  const u = sub(a, v)
  const w = sub(b, v)
  return (Math.acos(Math.max(-1, Math.min(1, dt(u, w) / (ln(u) * ln(w))))) * 180) / Math.PI
}

function convex(p: P[]) {
  const t = [0, 1, 2, 3].map((i) => cr(sub(p[(i + 1) % 4], p[i]), sub(p[(i + 2) % 4], p[(i + 1) % 4])))
  return t.every((x) => x > 0) || t.every((x) => x < 0)
}

/** Можно ли так поставить вершины: фигура остаётся выпуклой, не слишком вытянутой и в пределах рисунка. */
function valid(p: P[]) {
  if (!p.every(([x, y]) => x >= 2 && x <= 15 && y >= 2 && y <= 9)) return false
  if (!convex(p)) return false
  for (let i = 0; i < 4; i++) {
    if (ln(sub(p[(i + 1) % 4], p[i])) < 2) return false
    const a = deg(p[i], p[(i + 3) % 4], p[(i + 1) % 4])
    if (a < 12 || a > 168) return false
  }
  return true
}

/** Округление до целых так, чтобы сумма была ровно total (метод наибольших остатков). */
function roundTo(vals: number[], total: number): number[] {
  const fl = vals.map(Math.floor)
  let need = total - fl.reduce((s, v) => s + v, 0)
  const order = vals.map((v, i) => ({ i, r: v - Math.floor(v) })).sort((a, b) => b.r - a.r)
  const out = [...fl]
  for (let k = 0; need > 0 && k < order.length; k++, need--) out[order[k].i]++
  return out
}

type Model = {
  full: number[]
  /** Если проведена диагональ: концы e1, e2; другие вершины o1 = e1+1 и o2 = e1+3; части углов в двух треугольниках. */
  diag?: { e1: number; e2: number; o1: number; o2: number; a1: number; a2: number; g1: number; g2: number }
}

function model(p: P[], diag: number): Model {
  const exact = [0, 1, 2, 3].map((i) => deg(p[i], p[(i + 3) % 4], p[(i + 1) % 4]))
  const full = roundTo(exact, 360)
  if (diag === 0) return { full }
  const e1 = diag === 1 ? 0 : 1
  const e2 = e1 + 2
  const o1 = (e1 + 1) % 4
  const o2 = (e1 + 3) % 4
  const part = deg(p[e1], p[o1], p[e2]) // часть угла при e1 в треугольнике e1-o1-e2
  const rest = 180 - full[o1]
  const lo = Math.max(1, rest - (full[e2] - 1))
  const hi = Math.min(full[e1] - 1, rest - 1)
  const a1 = Math.max(lo, Math.min(hi, Math.round(part)))
  const g1 = rest - a1
  return { full, diag: { e1, e2, o1, o2, a1, a2: full[e1] - a1, g1, g2: full[e2] - g1 } }
}

const unit = (a: P): P => {
  const l = ln(a) || 1
  return [a[0] / l, a[1] / l]
}
const px = (p: P): P => [p[0] * U, p[1] * U]
const f1 = (n: number) => Math.round(n * 10) / 10

type Mark = { v: number; a: number; b: number; value: number; cls: string }

/** Дуга (или значок прямого угла) и число при вершине v между лучами на вершины a и b. */
function AngleMark({ pts, m }: { pts: P[]; m: Mark }) {
  const v = px(pts[m.v])
  const ua = unit(sub(px(pts[m.a]), v))
  const ub = unit(sub(px(pts[m.b]), v))
  const bis = unit([ua[0] + ub[0], ua[1] + ub[1]])
  const real = deg(pts[m.v], pts[m.a], pts[m.b])
  const r = real < 28 ? 24 : 17
  const label: P = [v[0] + bis[0] * (r + 15), v[1] + bis[1] * (r + 15)]
  const sweep = ua[0] * ub[1] - ua[1] * ub[0] > 0 ? 1 : 0
  const right = Math.abs(real - 90) < 0.6
  const s = 11
  return (
    <g className={`as-mark ${m.cls}`}>
      {right ? (
        <polyline points={`${f1(v[0] + ua[0] * s)},${f1(v[1] + ua[1] * s)} ${f1(v[0] + (ua[0] + ub[0]) * s)},${f1(v[1] + (ua[1] + ub[1]) * s)} ${f1(v[0] + ub[0] * s)},${f1(v[1] + ub[1] * s)}`} className="as-arc" />
      ) : (
        <path className="as-arc" d={`M ${f1(v[0] + ua[0] * r)} ${f1(v[1] + ua[1] * r)} A ${r} ${r} 0 0 ${sweep} ${f1(v[0] + ub[0] * r)} ${f1(v[1] + ub[1] * r)}`} />
      )}
      <text className="as-num" x={f1(label[0])} y={f1(label[1])} textAnchor="middle" dy=".35em">
        {m.value}°
      </text>
    </g>
  )
}

/** Сумма углов четырёхугольника: двигаем вершины, смотрим на углы, режем диагональю на два треугольника. */
export function AngleSumViz() {
  const [pts, setPts] = useState<P[]>(PRESETS[0].pts)
  const [sel, setSel] = useState(0)
  const [diag, setDiag] = useState(0)

  const m = model(pts, diag)
  const q = pts.map(px)
  const move = (dx: number, dy: number) => {
    const next = pts.map((p, i) => (i === sel ? ([p[0] + dx, p[1] + dy] as P) : p))
    if (valid(next)) setPts(next)
  }
  const can = (dx: number, dy: number) => valid(pts.map((p, i) => (i === sel ? ([p[0] + dx, p[1] + dy] as P) : p)))

  const marks: Mark[] = []
  if (!m.diag) {
    for (let i = 0; i < 4; i++) marks.push({ v: i, a: (i + 3) % 4, b: (i + 1) % 4, value: m.full[i], cls: 'all' })
  } else {
    const { e1, e2, o1, o2, a1, a2, g1, g2 } = m.diag
    marks.push({ v: o1, a: e1, b: e2, value: m.full[o1], cls: 't1' })
    marks.push({ v: o2, a: e2, b: e1, value: m.full[o2], cls: 't2' })
    marks.push({ v: e1, a: o1, b: e2, value: a1, cls: 't1' })
    marks.push({ v: e1, a: e2, b: o2, value: a2, cls: 't2' })
    marks.push({ v: e2, a: e1, b: o1, value: g1, cls: 't1' })
    marks.push({ v: e2, a: o2, b: e1, value: g2, cls: 't2' })
  }

  let readout: ReactNode
  if (!m.diag) {
    const [a, b, c, d] = m.full
    readout = (
      <>
        <div className="viz-calc">
          <Tex tex={`\\angle A+\\angle B+\\angle C+\\angle D=${a}^\\circ+${b}^\\circ+${c}^\\circ+${d}^\\circ=${a + b + c + d}^\\circ`} />
        </div>
        <div className="muted">Подвигай вершины: углы меняются, а сумма всегда {a + b + c + d}°. Проведи диагональ — и увидишь почему.</div>
      </>
    )
  } else {
    const { e1, e2, o1, o2, a1, a2, g1, g2 } = m.diag
    const t1 = `${NAMES[e1]}${NAMES[o1]}${NAMES[e2]}`
    const t2 = `${NAMES[e1]}${NAMES[e2]}${NAMES[o2]}`
    const s1 = a1 + m.full[o1] + g1
    const s2 = a2 + g2 + m.full[o2]
    readout = (
      <>
        <div>
          Диагональ <strong>{NAMES[e1]}{NAMES[e2]}</strong> режет четырёхугольник на два треугольника.
        </div>
        <div className="viz-calc as-t1">
          <Tex tex={`\\triangle ${t1}:\\ ${a1}^\\circ+${m.full[o1]}^\\circ+${g1}^\\circ=${s1}^\\circ`} />
        </div>
        <div className="viz-calc as-t2">
          <Tex tex={`\\triangle ${t2}:\\ ${a2}^\\circ+${g2}^\\circ+${m.full[o2]}^\\circ=${s2}^\\circ`} />
        </div>
        <div>
          Вместе <Tex tex={`${s1}^\\circ+${s2}^\\circ=${s1 + s2}^\\circ`} /> — это и есть сумма углов четырёхугольника.
        </div>
      </>
    )
  }

  return (
    <div className="viz as">
      <div className="viz-title">Сумма углов четырёхугольника</div>

      <div className="viz-step">
        <span className="viz-num">1</span> Выбери вершину и подвигай её
      </div>
      <div className="chips">
        {NAMES.map((name, i) => (
          <button key={name} className={`chip ${i === sel ? 'on' : ''}`} onClick={() => setSel(i)} aria-label={`Выбрать вершину ${name}`}>
            {name}
          </button>
        ))}
        <span className="as-pad" role="group" aria-label={`Двигать вершину ${NAMES[sel]}`}>
          <button className="key" onClick={() => move(-1, 0)} disabled={!can(-1, 0)} aria-label={`вершину ${NAMES[sel]} влево`}>
            ←
          </button>
          <button className="key" onClick={() => move(0, -1)} disabled={!can(0, -1)} aria-label={`вершину ${NAMES[sel]} вверх`}>
            ↑
          </button>
          <button className="key" onClick={() => move(0, 1)} disabled={!can(0, 1)} aria-label={`вершину ${NAMES[sel]} вниз`}>
            ↓
          </button>
          <button className="key" onClick={() => move(1, 0)} disabled={!can(1, 0)} aria-label={`вершину ${NAMES[sel]} вправо`}>
            →
          </button>
        </span>
      </div>
      <div className="chips">
        {PRESETS.map((p) => (
          <button key={p.label} className={`chip wide ${p.pts.every((pt, i) => pt[0] === pts[i][0] && pt[1] === pts[i][1]) ? 'on' : ''}`} onClick={() => setPts(p.pts)}>
            {p.label}
          </button>
        ))}
      </div>

      <svg viewBox={`0 0 ${W} ${H}`} className="as-svg" role="img" aria-label="Четырёхугольник ABCD с подписанными углами">
        {m.diag && (
          <>
            <polygon className="as-tri t1" points={[m.diag.e1, m.diag.o1, m.diag.e2].map((i) => `${q[i][0]},${q[i][1]}`).join(' ')} />
            <polygon className="as-tri t2" points={[m.diag.e2, m.diag.o2, m.diag.e1].map((i) => `${q[i][0]},${q[i][1]}`).join(' ')} />
          </>
        )}
        <polygon className={`as-poly ${m.diag ? 'cut' : ''}`} points={q.map((p) => `${p[0]},${p[1]}`).join(' ')} />
        {m.diag && <line className="as-diag" x1={q[m.diag.e1][0]} y1={q[m.diag.e1][1]} x2={q[m.diag.e2][0]} y2={q[m.diag.e2][1]} />}
        {marks.map((mk, i) => (
          <AngleMark key={i} pts={pts} m={mk} />
        ))}
        {q.map((p, i) => {
          const cx = q.reduce((s, r) => s + r[0], 0) / 4
          const cy = q.reduce((s, r) => s + r[1], 0) / 4
          const d = unit([p[0] - cx, p[1] - cy])
          return (
            <g key={i}>
              <circle className={`as-dot ${i === sel ? 'sel' : ''}`} cx={p[0]} cy={p[1]} r={i === sel ? 8 : 5} />
              <circle className="as-hit" cx={p[0]} cy={p[1]} r={17} onClick={() => setSel(i)} />
              <text className="as-name" x={p[0] + d[0] * 30} y={p[1] + d[1] * 30 + 1} textAnchor="middle" dy=".35em">
                {NAMES[i]}
              </text>
            </g>
          )
        })}
      </svg>

      <div className="viz-step">
        <span className="viz-num">2</span> Проведи диагональ
      </div>
      <div className="chips">
        {['без диагонали', 'диагональ AC', 'диагональ BD'].map((label, i) => (
          <button key={label} className={`chip wide ${i === diag ? 'on' : ''}`} onClick={() => setDiag(i)}>
            {label}
          </button>
        ))}
      </div>
      <div className="readout" aria-live="polite">
        {readout}
      </div>
    </div>
  )
}
