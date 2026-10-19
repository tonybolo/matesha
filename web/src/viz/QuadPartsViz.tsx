import { useState, type ReactNode } from 'react'
import './QuadPartsViz.css'

type P = [number, number]

const U = 20 // одна клетка = 20 пикселей
const W = 340
const H = 230
const NAMES = ['A', 'B', 'C', 'D']
const BASE: P[] = [
  [3, 8],
  [12, 9],
  [15, 3],
  [4, 2],
]
const MODES = ['вершины', 'стороны', 'диагонали', 'соседние', 'противоположные']
const n = (i: number) => NAMES[((i % 4) + 4) % 4]

/** Положения вершины D, при которых что-то интересное происходит. */
const D_PRESETS: { label: string; d: P }[] = [
  { label: 'Обычный', d: [4, 2] },
  { label: 'Вмятина', d: [10, 7] },
  { label: 'Бантик', d: [8, 10] },
  { label: 'Три на одной прямой', d: [13, 7] },
]

const cross = (a: P, b: P, c: P) => (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
/** Отрезки p1p2 и p3p4 пересекаются во внутренней точке. */
const segCross = (p1: P, p2: P, p3: P, p4: P) => cross(p3, p4, p1) * cross(p3, p4, p2) < 0 && cross(p1, p2, p3) * cross(p1, p2, p4) < 0

type Status = { ok: boolean; text: ReactNode }

/** Проверяем определение: вершины не совпадают, никакие три не на одной прямой, стороны не пересекаются. */
function check(P: P[]): Status {
  for (let i = 0; i < 4; i++) {
    for (let j = i + 1; j < 4; j++) {
      if (P[i][0] === P[j][0] && P[i][1] === P[j][1]) {
        return { ok: false, text: <>Вершины {n(i)} и {n(j)} совпали — это уже не четыре разные точки. Не четырёхугольник.</> }
      }
    }
  }
  for (let i = 0; i < 4; i++) {
    for (let j = i + 1; j < 4; j++) {
      for (let k = j + 1; k < 4; k++) {
        if (cross(P[i], P[j], P[k]) === 0) {
          return { ok: false, text: <>Вершины {n(i)}, {n(j)} и {n(k)} лежат на одной прямой — так нельзя. Это уже не четырёхугольник.</> }
        }
      }
    }
  }
  if (segCross(P[0], P[1], P[2], P[3])) return { ok: false, text: <>Стороны AB и CD пересеклись — получился «бантик». Это не четырёхугольник.</> }
  if (segCross(P[1], P[2], P[3], P[0])) return { ok: false, text: <>Стороны BC и DA пересеклись — получился «бантик». Это не четырёхугольник.</> }
  const turns = [0, 1, 2, 3].map((i) => cross(P[i], P[(i + 1) % 4], P[(i + 2) % 4]))
  const pos = turns.filter((t) => t > 0).length
  if (pos === 4 || pos === 0) {
    return { ok: true, text: <>Это четырёхугольник: четыре вершины, никакие три не на одной прямой, стороны не пересекаются. Он выпуклый, «без вмятин».</> }
  }
  const odd = pos === 1 ? turns.findIndex((t) => t > 0) : turns.findIndex((t) => t < 0)
  return {
    ok: true,
    text: (
      <>
        Это тоже четырёхугольник, но невыпуклый: у вершины {n(odd + 1)} «вмятина» (угол больше 180°). В этой теме мы работаем с выпуклыми.
      </>
    ),
  }
}

function explain(mode: number, focus: number): ReactNode {
  const v = focus % 4
  switch (mode) {
    case 0:
      return (
        <>
          <strong>Вершина {n(v)}</strong> — одна из четырёх точек-углов. Всего вершин четыре: A, B, C, D. Из вершины {n(v)} выходят две стороны: {n(v)}
          {n(v - 1)} и {n(v)}
          {n(v + 1)}.
        </>
      )
    case 1:
      return (
        <>
          <strong>
            Сторона {n(focus)}
            {n(focus + 1)}
          </strong>{' '}
          — отрезок между вершинами {n(focus)} и {n(focus + 1)}. Всего сторон четыре: AB, BC, CD, DA. Они идут по кругу и друг друга не пересекают.
        </>
      )
    case 2: {
      const a = focus % 2
      return (
        <>
          <strong>
            Диагональ {n(a)}
            {n(a + 2)}
          </strong>{' '}
          соединяет противоположные вершины {n(a)} и {n(a + 2)}. Диагоналей две: AC и BD. Внутри фигуры они пересекаются.
        </>
      )
    }
    case 3:
      return (
        <>
          Соседи вершины <strong>{n(v)}</strong> — вершины {n(v - 1)} и {n(v + 1)}: с каждой из них {n(v)} соединена стороной. Соседние стороны при вершине {n(v)}:{' '}
          {n(v)}
          {n(v - 1)} и {n(v)}
          {n(v + 1)}. Вершина {n(v + 2)} — не сосед.
        </>
      )
    default:
      return (
        <>
          Вершине <strong>{n(v)}</strong> противоположна вершина <strong>{n(v + 2)}</strong>: стороны между ними нет, их соединяет только диагональ {n(v)}
          {n(v + 2)}. Противоположные стороны — те, у которых нет общей вершины: AB и CD, а также BC и DA.
        </>
      )
  }
}

/** Части четырёхугольника: вершины, стороны, диагонали, соседние и противоположные. Внизу можно двигать вершину D и проверять определение. */
export function QuadPartsViz() {
  const [mode, setMode] = useState(0)
  const [focus, setFocus] = useState(0)
  const [d, setD] = useState<P>(BASE[3])

  const P: P[] = [BASE[0], BASE[1], BASE[2], d]
  const px = P.map(([x, y]) => ({ x: x * U, y: y * U }))
  const cx = px.reduce((s, p) => s + p.x, 0) / 4
  const cy = px.reduce((s, p) => s + p.y, 0) / 4
  const status = check(P)

  const picks = mode === 1 ? ['AB', 'BC', 'CD', 'DA'] : mode === 2 ? ['AC', 'BD'] : NAMES
  const pickLabel = mode === 1 ? 'Сторона' : mode === 2 ? 'Диагональ' : 'Вершина'
  const f = Math.min(focus, picks.length - 1)
  const v = f % 4
  const opp = (v + 2) % 4

  const sideClass = (i: number) => {
    if (mode === 1) return i === f ? 'sel' : 'on'
    if (mode === 3) return i === v || i === (v + 3) % 4 ? 'nb' : ''
    if (mode === 4) return i % 2 === 0 ? 'p1' : 'p2'
    return ''
  }
  const dotClass = (i: number) => {
    if (mode === 0) return i === f ? 'sel' : 'on'
    if (mode === 2) return i === f % 2 || i === (f % 2) + 2 ? 'sel' : ''
    if (mode === 3) return i === v ? 'sel' : i === (v + 1) % 4 || i === (v + 3) % 4 ? 'nb' : i === opp ? 'opp' : ''
    if (mode === 4) return i === v ? 'sel' : i === opp ? 'opp' : ''
    return ''
  }

  const label = (i: number, k: number) => {
    const dx = px[i].x - cx
    const dy = px[i].y - cy
    const l = Math.hypot(dx, dy) || 1
    return { x: px[i].x + (dx / l) * k, y: px[i].y + (dy / l) * k }
  }
  const mid = (i: number, j: number, k = 0) => {
    const x = (px[i].x + px[j].x) / 2
    const y = (px[i].y + px[j].y) / 2
    const dx = x - cx
    const dy = y - cy
    const l = Math.hypot(dx, dy) || 1
    return { x: x + (dx / l) * k, y: y + (dy / l) * k }
  }

  const move = (dx: number, dy: number) => setD(([x, y]) => [x + dx, y + dy])
  const canMove = (dx: number, dy: number) => d[0] + dx >= 1 && d[0] + dx <= 15 && d[1] + dy >= 1 && d[1] + dy <= 10

  return (
    <div className="viz qp">
      <div className="viz-title">Части четырёхугольника</div>

      <div className="viz-step">
        <span className="viz-num">1</span> Что показать?
      </div>
      <div className="chips">
        {MODES.map((m, i) => (
          <button key={m} className={`chip wide ${i === mode ? 'on' : ''}`} onClick={() => setMode(i)}>
            {m}
          </button>
        ))}
      </div>
      <div className="qp-pick" role="group" aria-label={`${pickLabel}: выбери`}>
        <span className="muted">{pickLabel}:</span>
        {picks.map((name, i) => (
          <button key={name} className={`chip ${i === f ? 'on' : ''}`} onClick={() => setFocus(i)} aria-label={`${pickLabel} ${name}`}>
            {name}
          </button>
        ))}
      </div>

      <svg viewBox={`0 0 ${W} ${H}`} className="qp-svg" role="img" aria-label="Четырёхугольник ABCD: вершины, стороны и диагонали">
        <polygon className="qp-poly" points={px.map((p) => `${p.x},${p.y}`).join(' ')} />
        {/* диагонали */}
        {mode === 2 &&
          [0, 1].map((k) => (
            <line key={k} className={`qp-diag ${k === f % 2 ? 'sel' : ''}`} x1={px[k].x} y1={px[k].y} x2={px[k + 2].x} y2={px[k + 2].y} />
          ))}
        {mode === 4 && <line className="qp-diag sel" x1={px[v].x} y1={px[v].y} x2={px[opp].x} y2={px[opp].y} />}
        {/* стороны */}
        {px.map((p, i) => {
          const q = px[(i + 1) % 4]
          return <line key={i} className={`qp-side ${sideClass(i)}`} x1={p.x} y1={p.y} x2={q.x} y2={q.y} />
        })}
        {mode === 1 &&
          px.map((_, i) => {
            const m = mid(i, (i + 1) % 4, 15)
            return (
              <text key={i} className={`qp-sidename ${i === f ? 'sel' : ''}`} x={m.x} y={m.y} textAnchor="middle" dy=".35em">
                {n(i)}
                {n(i + 1)}
              </text>
            )
          })}
        {mode === 2 &&
          [0, 1].map((k) => {
            const a = px[k]
            const b = px[k + 2]
            return (
              <text key={k} className="qp-sidename sel" x={a.x + (b.x - a.x) * 0.22} y={a.y + (b.y - a.y) * 0.22 - 9} textAnchor="middle" dy=".35em">
                {n(k)}
                {n(k + 2)}
              </text>
            )
          })}
        {/* вершины */}
        {px.map((p, i) => {
          const t = label(i, 17)
          return (
            <g key={i}>
              <circle className={`qp-dot ${dotClass(i)}`} cx={p.x} cy={p.y} r={5} />
              <text className="qp-name" x={t.x} y={t.y} textAnchor="middle" dy=".35em">
                {n(i)}
              </text>
            </g>
          )
        })}
        {!status.ok && (
          <text className="qp-warn" x={10} y={20}>
            ✗ не четырёхугольник
          </text>
        )}
      </svg>

      <div className="readout" aria-live="polite">
        {explain(mode, f)}
      </div>

      <div className="viz-step">
        <span className="viz-num">2</span> А если подвинуть вершину D?
      </div>
      <div className="qp-move">
        <div className="qp-pad" role="group" aria-label="Двигать вершину D">
          <button className="key qp-up" onClick={() => move(0, -1)} disabled={!canMove(0, -1)} aria-label="вершину D вверх">
            ↑
          </button>
          <button className="key qp-left" onClick={() => move(-1, 0)} disabled={!canMove(-1, 0)} aria-label="вершину D влево">
            ←
          </button>
          <button className="key qp-down" onClick={() => move(0, 1)} disabled={!canMove(0, 1)} aria-label="вершину D вниз">
            ↓
          </button>
          <button className="key qp-right" onClick={() => move(1, 0)} disabled={!canMove(1, 0)} aria-label="вершину D вправо">
            →
          </button>
        </div>
        <div className="chips qp-presets">
          {D_PRESETS.map((p) => (
            <button key={p.label} className={`chip wide ${d[0] === p.d[0] && d[1] === p.d[1] ? 'on' : ''}`} onClick={() => setD(p.d)}>
              {p.label}
            </button>
          ))}
        </div>
      </div>
      <div className={`readout ${status.ok ? '' : 'bad'}`} aria-live="polite">
        {status.ok ? '✓ ' : '✗ '}
        {status.text}
      </div>
    </div>
  )
}
