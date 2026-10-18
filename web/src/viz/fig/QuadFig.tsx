import type { FigValue } from '../../content/types'

/**
 * Рисунок к заданию: четырёхугольник по четырём вершинам.
 * Параметры (props):
 *   pts   — координаты вершин подряд [x1, y1, x2, y2, x3, y3, x4, y4], y растёт вверх;
 *   names — буквы вершин (по умолчанию «ABCD»);
 *   grid  — рисовать клетчатую плоскость с числами на осях (для задач на координаты);
 *   eq1, eq2  — номера сторон (0 — AB, 1 — BC, 2 — CD, 3 — DA), которые отмечены одной и двумя чёрточками (равенство сторон);
 *   par1, par2 — номера сторон, отмеченных одной и двумя стрелками (параллельность);
 *   rt    — номера вершин с отметкой прямого угла;
 *   sides — подписи сторон (например «7 см»), по одной на сторону;
 *   angs  — подписи углов («70°», «?»), по одной на вершину;
 *   diag  — две вершины, соединённые пунктирной диагональю, например [0, 2];
 *   view  — [x0, y0, x1, y1]: окно рисунка в тех же координатах (масштаб не зависит от фигуры; нужно картинкам урока).
 */
type Props = Record<string, FigValue>
type Pt = { x: number; y: number }

const W = 320
const nums = (v: FigValue | undefined): number[] => (Array.isArray(v) ? v.map(Number) : [])
const strs = (v: FigValue | undefined): string[] => (Array.isArray(v) ? v.map(String) : [])
const unit = (a: Pt): Pt => {
  const l = Math.hypot(a.x, a.y) || 1
  return { x: a.x / l, y: a.y / l }
}
const at = (p: Pt, d: Pt, k: number): Pt => ({ x: p.x + d.x * k, y: p.y + d.y * k })
const f = (n: number) => Math.round(n * 100) / 100
const pt = (p: Pt) => `${f(p.x)},${f(p.y)}`

export function QuadFig(props: Props) {
  const raw = nums(props.pts)
  if (raw.length !== 8 || raw.some((v) => !Number.isFinite(v))) return null
  const names = typeof props.names === 'string' && props.names.length === 4 ? props.names : 'ABCD'
  const grid = props.grid === true
  const eq1 = nums(props.eq1)
  const eq2 = nums(props.eq2)
  const par1 = nums(props.par1)
  const par2 = nums(props.par2)
  const rt = nums(props.rt)
  const sides = strs(props.sides)
  const angs = strs(props.angs)
  const diag = nums(props.diag)
  const view = nums(props.view)

  const M = [0, 1, 2, 3].map((i) => ({ x: raw[2 * i], y: raw[2 * i + 1] }))
  const xs = M.map((p) => p.x)
  const ys = M.map((p) => p.y)
  let x0 = Math.min(...xs)
  let x1 = Math.max(...xs)
  let y0 = Math.min(...ys)
  let y1 = Math.max(...ys)
  if (grid) {
    x0 = Math.floor(x0) - 1
    x1 = Math.ceil(x1) + 1
    y0 = Math.floor(y0) - 1
    y1 = Math.ceil(y1) + 1
  }
  const fixed = view.length === 4 && view.every((v) => Number.isFinite(v))
  if (fixed) [x0, y0, x1, y1] = view
  const padL = grid ? 26 : fixed ? 26 : 38
  const padR = grid ? 12 : fixed ? 26 : 38
  const padT = grid ? 12 : fixed ? 22 : 30
  const padB = grid ? 22 : fixed ? 22 : 30
  const bw = Math.max(x1 - x0, 0.5)
  const bh = Math.max(y1 - y0, 0.5)
  const s = Math.min((W - padL - padR) / bw, (230 - padT - padB) / bh, grid ? 46 : 62)
  const H = Math.round(bh * s + padT + padB)
  const ox = (W - padL - padR - bw * s) / 2
  const X = (x: number) => padL + ox + (x - x0) * s
  const Y = (y: number) => padT + (y1 - y) * s

  const Q: Pt[] = M.map((p) => ({ x: X(p.x), y: Y(p.y) }))
  const c: Pt = { x: (Q[0].x + Q[1].x + Q[2].x + Q[3].x) / 4, y: (Q[0].y + Q[1].y + Q[2].y + Q[3].y) / 4 }
  const out = (p: Pt) => unit({ x: p.x - c.x, y: p.y - c.y })

  const step = bw > 12 ? 2 : 1
  const gridX: number[] = []
  const gridY: number[] = []
  if (grid) {
    for (let g = Math.ceil(x0); g <= x1; g++) gridX.push(g)
    for (let g = Math.ceil(y0); g <= y1; g++) gridY.push(g)
  }

  /** Середина стороны i, единичный вектор вдоль неё и «наружу». */
  const side = (i: number) => {
    const a = Q[i]
    const b = Q[(i + 1) % 4]
    const mid = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 }
    let dir = unit({ x: b.x - a.x, y: b.y - a.y })
    const nrm = unit({ x: -dir.y, y: dir.x })
    const outward = (mid.x - c.x) * nrm.x + (mid.y - c.y) * nrm.y >= 0 ? nrm : { x: -nrm.x, y: -nrm.y }
    // стрелки параллельности у обеих сторон пары смотрят в одну сторону
    if (dir.x < -1e-9 || (Math.abs(dir.x) <= 1e-9 && dir.y < 0)) dir = { x: -dir.x, y: -dir.y }
    return { mid, dir, outward }
  }

  const ticks = (i: number, count: number) => {
    const { mid, outward } = side(i)
    const along = unit({ x: Q[(i + 1) % 4].x - Q[i].x, y: Q[(i + 1) % 4].y - Q[i].y })
    const lines = []
    for (let k = 0; k < count; k++) {
      const shift = (k - (count - 1) / 2) * 5
      const m = at(mid, along, shift)
      const p1 = at(m, outward, -6)
      const p2 = at(m, outward, 6)
      lines.push(<line key={k} x1={f(p1.x)} y1={f(p1.y)} x2={f(p2.x)} y2={f(p2.y)} stroke="var(--c0)" strokeWidth={2.4} strokeLinecap="round" />)
    }
    return <g key={`t${i}${count}`}>{lines}</g>
  }

  const arrows = (i: number, count: number) => {
    const { mid, dir, outward } = side(i)
    const chevrons = []
    for (let k = 0; k < count; k++) {
      const shift = (k - (count - 1) / 2) * 7
      const m = at(mid, dir, shift)
      const tip = at(m, dir, 3.5)
      const l = at(at(m, dir, -3.5), outward, 5)
      const r = at(at(m, dir, -3.5), outward, -5)
      chevrons.push(<polyline key={k} points={`${pt(l)} ${pt(tip)} ${pt(r)}`} fill="none" stroke="var(--c1)" strokeWidth={2.4} strokeLinecap="round" strokeLinejoin="round" />)
    }
    return <g key={`a${i}${count}`}>{chevrons}</g>
  }

  const rightMark = (i: number) => {
    const v = Q[i]
    const u = unit({ x: Q[(i + 3) % 4].x - v.x, y: Q[(i + 3) % 4].y - v.y })
    const w = unit({ x: Q[(i + 1) % 4].x - v.x, y: Q[(i + 1) % 4].y - v.y })
    const a = 10
    const p1 = at(v, u, a)
    const p3 = at(v, w, a)
    const p2 = at(p1, w, a)
    return <polyline key={`r${i}`} points={`${pt(p1)} ${pt(p2)} ${pt(p3)}`} fill="none" stroke="var(--c0)" strokeWidth={2} strokeLinejoin="round" />
  }

  /** Дуга и подпись угла при вершине i. */
  const angle = (i: number, label: string) => {
    const v = Q[i]
    const u = unit({ x: Q[(i + 3) % 4].x - v.x, y: Q[(i + 3) % 4].y - v.y })
    const w = unit({ x: Q[(i + 1) % 4].x - v.x, y: Q[(i + 1) % 4].y - v.y })
    const bis = unit({ x: u.x + w.x, y: u.y + w.y })
    const r = 15
    const a = at(v, u, r)
    const b = at(v, w, r)
    const sweep = u.x * w.y - u.y * w.x > 0 ? 1 : 0
    const unknown = label === '?'
    const dist = unknown ? 30 : 34
    const lp = at(v, bis, dist)
    return (
      <g key={`g${i}`}>
        {!rt.includes(i) && <path d={`M ${pt(a)} A ${r} ${r} 0 0 ${sweep} ${pt(b)}`} fill="none" stroke={unknown ? 'var(--bad)' : 'var(--muted)'} strokeWidth={1.8} />}
        <text x={f(lp.x)} y={f(lp.y)} textAnchor="middle" dy=".35em" fontSize={unknown ? 16 : 12} fontWeight={unknown ? 800 : 600} fill={unknown ? 'var(--bad)' : 'var(--text)'}>
          {label}
        </text>
      </g>
    )
  }

  const label = grid
    ? ({ stroke: 'var(--card)', strokeWidth: 3, paintOrder: 'stroke' } as const)
    : ({} as const)

  return (
    <svg viewBox={`0 0 ${W} ${H}`} width={W} height={H} role="img" aria-label={`Четырёхугольник ${names}${grid ? ' на клетчатой плоскости' : ''}`}>
      {grid && (
        <g>
          {gridX.map((g) => (
            <line key={`x${g}`} x1={f(X(g))} x2={f(X(g))} y1={f(Y(y0))} y2={f(Y(y1))} stroke={g === 0 ? 'var(--muted)' : 'var(--line)'} strokeWidth={g === 0 ? 1.6 : 1} />
          ))}
          {gridY.map((g) => (
            <line key={`y${g}`} y1={f(Y(g))} y2={f(Y(g))} x1={f(X(x0))} x2={f(X(x1))} stroke={g === 0 ? 'var(--muted)' : 'var(--line)'} strokeWidth={g === 0 ? 1.6 : 1} />
          ))}
          {gridX.filter((g) => g % step === 0).map((g) => (
            <text key={`tx${g}`} x={f(X(g))} y={f(Y(y0) + 15)} textAnchor="middle" fontSize={11} fill="var(--muted)">
              {g < 0 ? `−${-g}` : g}
            </text>
          ))}
          {gridY.filter((g) => g % step === 0).map((g) => (
            <text key={`ty${g}`} x={f(X(x0) - 5)} y={f(Y(g))} textAnchor="end" dy=".35em" fontSize={11} fill="var(--muted)">
              {g < 0 ? `−${-g}` : g}
            </text>
          ))}
        </g>
      )}
      <polygon points={Q.map(pt).join(' ')} fill="var(--accent-soft)" fillOpacity={0.7} stroke="var(--accent)" strokeWidth={2.6} strokeLinejoin="round" />
      {diag.length === 2 && <line x1={f(Q[diag[0]].x)} y1={f(Q[diag[0]].y)} x2={f(Q[diag[1]].x)} y2={f(Q[diag[1]].y)} stroke="var(--muted)" strokeWidth={2} strokeDasharray="6 4" />}
      {eq1.map((i) => ticks(i, 1))}
      {eq2.map((i) => ticks(i, 2))}
      {par1.map((i) => arrows(i, 1))}
      {par2.map((i) => arrows(i, 2))}
      {rt.map((i) => rightMark(i))}
      {angs.map((a, i) => (a ? angle(i, a) : null))}
      {sides.map((t, i) => {
        if (!t) return null
        const { mid, outward } = side(i)
        const p = at(mid, outward, 16)
        return (
          <text key={`s${i}`} x={f(p.x)} y={f(p.y)} textAnchor="middle" dy=".35em" fontSize={12} fontWeight={700} fill="var(--text)" {...label}>
            {t}
          </text>
        )
      })}
      {Q.map((p, i) => {
        const d = out(p)
        const lp = at(p, d, 15)
        return (
          <g key={`v${i}`}>
            <circle cx={f(p.x)} cy={f(p.y)} r={3.6} fill="var(--accent)" />
            <text x={f(lp.x)} y={f(lp.y)} textAnchor="middle" dy=".35em" fontSize={15} fontWeight={800} fill="var(--text)" {...label}>
              {names[i]}
            </text>
          </g>
        )
      })}
    </svg>
  )
}
