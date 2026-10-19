import type { ReactNode } from 'react'
import './parKit.css'
import { Stepper } from './Stepper'
import {
  NEIGHBORS,
  Placer,
  VERTS,
  arcPath,
  bisectorHit,
  centroid,
  chevPath,
  fitView,
  foot,
  inPoly,
  intersect,
  lerpXY,
  mid,
  parseMark,
  placeAngle,
  placeSeg,
  pushOut,
  rightPath,
  tickPath,
  type Pt,
  type Quad,
  type VName,
  type View,
  type XY,
} from './parKit'

/** Число с кнопками «−/+» и коротким подписанным названием (две такие пары помещаются в одну строку телефона). */
export function Num({ label, aria, value, min, max, step = 1, onChange, format }: { label: string; aria: string; value: number; min: number; max: number; step?: number; onChange: (n: number) => void; format?: (n: number) => string }) {
  return (
    <span className="pk-num">
      <span className="muted">{label}</span>
      <Stepper compact aria={aria} value={value} min={min} max={max} step={step} onChange={onChange} format={format} />
    </span>
  )
}

/** Подпись в SVG: текст по центру точки at. */
export function Txt({ at, className, children }: { at: XY; className: string; children: ReactNode }) {
  return (
    <text x={at[0]} y={at[1]} dy="0.35em" className={className}>
      {children}
    </text>
  )
}

export function Seg({ p, q, className }: { p: XY; q: XY; className: string }) {
  return <line x1={p[0]} y1={p[1]} x2={q[0]} y2={q[1]} className={className} />
}

/** Многоугольник: заливка (по желанию) и контур. */
export function Shape({ pts, fill = 'pk-fill', edge = 'pk-edge' }: { pts: XY[]; fill?: string; edge?: string }) {
  const d = pts.map((p) => `${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(' ')
  return (
    <>
      {fill && <polygon points={d} className={fill} />}
      {edge && <polygon points={d} className={edge} />}
    </>
  )
}

/** Дуга угла в вершине o между направлениями u и v. */
export function Arc({ o, u, v, r, className = 'pk-arc' }: { o: XY; u: XY; v: XY; r: number; className?: string }) {
  return <path d={arcPath(o, u, v, r)} className={className} />
}

export function RightMark({ o, u, v, s = 9 }: { o: XY; u: XY; v: XY; s?: number }) {
  return <path d={rightPath(o, u, v, s)} className="pk-right" />
}

export function Ticks({ p, q, n = 1, className = 'pk-tick' }: { p: XY; q: XY; n?: number; className?: string }) {
  return <path d={tickPath(p, q, n)} className={className} />
}

export function Chevs({ p, q, n = 1 }: { p: XY; q: XY; n?: number }) {
  return <path d={chevPath(p, q, n)} className="pk-chev" />
}

export function Dot({ at, r = 3.2, className = 'pk-dot' }: { at: XY; r?: number; className?: string }) {
  return <circle cx={at[0]} cy={at[1]} r={r} className={className} />
}

/** Подпись вершины A, B, C, D снаружи фигуры. */
export function VertexLabels({ V, view, center, names = VERTS }: { V: Quad; view: View; center: XY; names?: VName[] }) {
  return (
    <>
      {names.map((n) => (
        <Txt key={n} at={pushOut(view.S(V[n]), center, 13)} className="pk-v">
          {n}
        </Txt>
      ))}
    </>
  )
}

// ---------------------------------------------------------------------------
// Рисунок к заданию: параллелограмм или трапеция с необходимыми подписями.
// ---------------------------------------------------------------------------

export type FigSpec = {
  V: Quad
  /** Подписи: «AB=5», «BM=?», «A=40°», «CAD=30°». */
  marks?: string[]
  /** true — обе диагонали и точка O; 'AC' или 'BD' — одна диагональ. */
  diag?: boolean | string
  /** Высоты: «B>AD:H» — из вершины B на прямую AD, основание H. */
  ht?: string[]
  /** Биссектрисы: «A>BC:M» — из вершины A до прямой BC, точка M. */
  bis?: string[]
  /** Равные углы, помеченные дугами: «BAC», «CAD». */
  arcs?: string[]
  /** Чёрточки «равны» на боковых сторонах AB и CD. */
  ticks?: boolean
  /** Прямые углы при вершинах A и B. */
  right?: boolean
  /** Средняя линия MN. */
  mid?: boolean
  /** Точки P и Q: где средняя линия пересекает диагонали. */
  midx?: boolean
  legend?: string
  label: string
}

type Hit = { from: VName; s1: VName; s2: VName; name: string }

function parseHit(s: string): Hit | null {
  const m = /^([A-D])>([A-D])([A-D]):([A-Z])$/.exec(s)
  return m ? { from: m[1] as VName, s1: m[2] as VName, s2: m[3] as VName, name: m[4] } : null
}

const W = 320

/** Универсальный рисунок: четыре вершины и всё, что просит задание. */
export function GeoFigure({ spec }: { spec: FigSpec }) {
  const { V } = spec
  const pts: Record<string, Pt> = { ...V }
  const showAC = spec.diag === true || spec.diag === 'AC'
  const showBD = spec.diag === true || spec.diag === 'BD'

  let O: Pt | null = null
  if (spec.diag === true) {
    const r = intersect(V.A, V.C, V.B, V.D)
    if (r) {
      O = r.p
      pts.O = O
    }
  }
  const M = mid(V.A, V.B)
  const N = mid(V.C, V.D)
  if (spec.mid) {
    pts.M = M
    pts.N = N
  }
  let P: Pt | null = null
  let Q: Pt | null = null
  if (spec.mid && spec.midx) {
    if (showAC) P = intersect(M, N, V.A, V.C)?.p ?? null
    if (showBD) Q = intersect(M, N, V.B, V.D)?.p ?? null
    if (P) pts.P = P
    if (Q) pts.Q = Q
  }
  const heights = (spec.ht ?? []).map(parseHit).filter((h): h is Hit => !!h)
  const heightFeet = heights.map((h) => ({ ...h, at: foot(V[h.from], V[h.s1], V[h.s2]) }))
  for (const h of heightFeet) pts[h.name] = h.at
  const bisectors = (spec.bis ?? []).map(parseHit).filter((h): h is Hit => !!h)
  const bisHits = bisectors.map((h) => ({ ...h, at: bisectorHit(V, h.from, h.s1, h.s2) })).filter((h): h is typeof h & { at: Pt } => !!h.at)
  for (const h of bisHits) pts[h.name] = h.at

  const legendH = spec.legend ? 24 : 0
  const view = fitView(Object.values(pts), { w: W, maxH: 160, padX: 36, padTop: 30, padBottom: 30 + legendH })
  const S = view.S
  const poly = VERTS.map((n) => S(V[n]))
  const c = centroid(poly)
  const sp = (name: string): XY | null => (pts[name] ? S(pts[name]) : null)
  const dirTo = (from: XY, to: XY): XY => [to[0] - from[0], to[1] - from[1]]

  const nodes: ReactNode[] = []
  let key = 0
  const add = (node: ReactNode) => nodes.push(<g key={key++}>{node}</g>)

  // заливка
  add(<Shape pts={poly} edge="" />)

  // диагонали
  if (showAC) add(<Seg p={S(V.A)} q={S(V.C)} className="pk-diag" />)
  if (showBD) add(<Seg p={S(V.B)} q={S(V.D)} className="pk-diag" />)

  // высоты
  for (const h of heightFeet) {
    const from = S(V[h.from])
    const at = S(h.at)
    const a1 = S(V[h.s1])
    const a2 = S(V[h.s2])
    // если основание высоты вне стороны, продолжаем сторону пунктиром
    const lo = Math.min(a1[0], a2[0])
    const hi = Math.max(a1[0], a2[0])
    if (at[0] < lo - 0.5) add(<Seg p={at} q={a1[0] <= a2[0] ? a1 : a2} className="pk-aux" />)
    if (at[0] > hi + 0.5) add(<Seg p={at} q={a1[0] >= a2[0] ? a1 : a2} className="pk-aux" />)
    add(<Seg p={from} q={at} className="pk-height" />)
    const sgn = c[0] >= at[0] ? 1 : -1
    add(<RightMark o={at} u={dirTo(at, from)} v={[sgn, 0]} />)
  }

  // биссектрисы
  bisHits.forEach((h, i) => {
    const from = S(V[h.from])
    const at = S(h.at)
    add(<Seg p={from} q={at} className="pk-bis" />)
    const [n1, n2] = NEIGHBORS[h.from]
    add(<Arc o={from} u={dirTo(from, S(V[n1]))} v={dirTo(from, at)} r={22} className="pk-arc c2" />)
    add(<Arc o={from} u={dirTo(from, at)} v={dirTo(from, S(V[n2]))} r={22 + (i ? 4 : 0)} className="pk-arc c2" />)
  })

  // средняя линия
  if (spec.mid) add(<Seg p={S(M)} q={S(N)} className="pk-mid" />)

  // контур
  add(<Shape pts={poly} fill="" />)

  if (spec.ticks) {
    add(<Ticks p={S(V.A)} q={S(V.B)} />)
    add(<Ticks p={S(V.C)} q={S(V.D)} />)
  }
  if (spec.right) {
    add(<RightMark o={S(V.A)} u={dirTo(S(V.A), S(V.D))} v={dirTo(S(V.A), S(V.B))} />)
    add(<RightMark o={S(V.B)} u={dirTo(S(V.B), S(V.A))} v={dirTo(S(V.B), S(V.C))} />)
  }

  // равные углы, помеченные дугами
  const arcNames = new Set(spec.arcs ?? [])
  for (const name of arcNames) {
    if (name.length !== 3 || !pts[name[0]] || !pts[name[1]] || !pts[name[2]]) continue
    const o = S(pts[name[1]])
    add(<Arc o={o} u={dirTo(o, S(pts[name[0]]))} v={dirTo(o, S(pts[name[2]]))} r={26} className="pk-arc c1" />)
  }

  // ---- подписи: раскладываем так, чтобы они не налезали друг на друга ----
  const placer = new Placer()
  for (const n of VERTS) placer.fix(pushOut(S(V[n]), c, 13), n)
  if (spec.ticks) {
    placer.dot(lerpXY(S(V.A), S(V.B), 0.5))
    placer.dot(lerpXY(S(V.C), S(V.D), 0.5))
  }
  const dots: [string, Pt][] = []
  if (O) dots.push(['O', O])
  if (spec.mid) dots.push(['M', M], ['N', N])
  if (P) dots.push(['P', P])
  if (Q) dots.push(['Q', Q])
  for (const h of heightFeet) dots.push([h.name, h.at])
  for (const h of bisHits) dots.push([h.name, h.at])
  for (const [, p] of dots) placer.dot(S(p))

  const pointLabels = dots.map(([name, p]) => {
    const at = S(p)
    const up = name === 'O' || name === 'P' || name === 'Q'
    const below = heightFeet.some((h) => h.name === name)
    const cands: XY[] = up
      ? [[at[0], at[1] - 12], [at[0] + 14, at[1] - 6], [at[0] - 14, at[1] - 6], [at[0], at[1] + 14]]
      : below
        ? [[at[0], at[1] + 14], [at[0] + 15, at[1] + 12], [at[0] - 15, at[1] + 12]]
        : [pushOut(at, c, 13), pushOut(at, c, 20), [at[0], at[1] - 13], [at[0], at[1] + 14]]
    return { name, at: placer.place(cands, name) }
  })

  const markNodes: ReactNode[] = []
  for (const raw of spec.marks ?? []) {
    const m = parseMark(raw)
    if (!m) continue
    const cls = `pk-m${m.unknown ? ' q' : ''}`
    if (m.name.length === 2) {
      const p = sp(m.name[0])
      const q = sp(m.name[1])
      if (!p || !q) continue
      const at = placeSeg(placer, p, q, c, m.value)
      markNodes.push(
        <Txt key={raw} at={at} className={`${cls}${inPoly(at, poly) ? ' in' : ''}`}>
          {m.value}
        </Txt>,
      )
      continue
    }
    const [x, o, y] = m.name.length === 1 ? [NEIGHBORS[m.name as VName][0], m.name, NEIGHBORS[m.name as VName][1]] : [m.name[0], m.name[1], m.name[2]]
    const px = sp(x)
    const po = sp(o)
    const py = sp(y)
    if (!px || !po || !py) continue
    const u = dirTo(po, px)
    const v = dirTo(po, py)
    const r = m.name.length === 1 ? 19 : 26
    if (!arcNames.has(m.name)) add(<Arc o={po} u={u} v={v} r={r} className={m.unknown ? 'pk-arc c3' : 'pk-arc'} />)
    const at = placeAngle(placer, po, u, v, r, m.value)
    markNodes.push(
      <Txt key={raw} at={at} className={`${cls} in`}>
        {m.value}
      </Txt>,
    )
  }

  for (const [, p] of dots) add(<Dot at={S(p)} r={3} />)
  for (const l of pointLabels) add(<Txt at={l.at} className="pk-pt">{l.name}</Txt>)
  for (const n of VERTS) add(<Txt at={pushOut(S(V[n]), c, 13)} className="pk-v">{n}</Txt>)
  nodes.push(...markNodes)

  if (spec.legend) {
    add(<Txt at={[view.w / 2, view.h - 12]} className="pk-leg">{spec.legend}</Txt>)
  }

  return (
    <svg viewBox={`0 0 ${view.w} ${Math.ceil(view.h)}`} className="pk-svg" role="img" aria-label={spec.label}>
      {nodes}
    </svg>
  )
}
