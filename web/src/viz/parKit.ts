/** Геометрия и форматирование для картинок и рисунков темы «Параллелограмм, трапеция» (без React). */

export type Pt = { x: number; y: number }
export type VName = 'A' | 'B' | 'C' | 'D'
export type Quad = Record<VName, Pt>
/** Точка в координатах SVG (ось y вниз). */
export type XY = [number, number]

export const VERTS: VName[] = ['A', 'B', 'C', 'D']

export const P = (x: number, y: number): Pt => ({ x, y })
export const add = (p: Pt, q: Pt): Pt => P(p.x + q.x, p.y + q.y)
export const sub = (p: Pt, q: Pt): Pt => P(p.x - q.x, p.y - q.y)
export const mul = (p: Pt, k: number): Pt => P(p.x * k, p.y * k)
export const len = (p: Pt): number => Math.hypot(p.x, p.y)
export const dist = (p: Pt, q: Pt): number => len(sub(p, q))
export const dot = (p: Pt, q: Pt): number => p.x * q.x + p.y * q.y
export const cross = (p: Pt, q: Pt): number => p.x * q.y - p.y * q.x
export const mid = (p: Pt, q: Pt): Pt => P((p.x + q.x) / 2, (p.y + q.y) / 2)
export const unit = (p: Pt): Pt => {
  const l = len(p)
  return l < 1e-12 ? P(0, 0) : P(p.x / l, p.y / l)
}
export const toRad = (d: number): number => (d * Math.PI) / 180
export const toDeg = (r: number): number => (r * 180) / Math.PI
export const lerp = (p: Pt, q: Pt, t: number): Pt => P(p.x + (q.x - p.x) * t, p.y + (q.y - p.y) * t)

/** Параллелограмм: A(0;0), D(a;0), B = b·(cos α; sin α), C = B + (a;0). Здесь a = AD, b = AB, α = ∠A. */
export function parallelogram(a: number, b: number, angDeg: number): Quad {
  const r = toRad(angDeg)
  const B = P(b * Math.cos(r), b * Math.sin(r))
  return { A: P(0, 0), B, C: P(B.x + a, B.y), D: P(a, 0) }
}

/** Трапеция: A(0;0), D(a;0), B(s;h), C(s+b;h). Основания AD = a и BC = b, высота h, s — сдвиг вершины B. */
export function trapezoid(a: number, b: number, h: number, s: number): Quad {
  return { A: P(0, 0), B: P(s, h), C: P(s + b, h), D: P(a, 0) }
}

/** Угол POQ в градусах (от 0 до 180). */
export function angleAt(p: Pt, o: Pt, q: Pt): number {
  const u = sub(p, o)
  const v = sub(q, o)
  return toDeg(Math.atan2(Math.abs(cross(u, v)), dot(u, v)))
}

/** Пересечение прямых p1p2 и p3p4: точка и параметры t (вдоль первой) и u (вдоль второй); null, если прямые параллельны. */
export function intersect(p1: Pt, p2: Pt, p3: Pt, p4: Pt): { p: Pt; t: number; u: number } | null {
  const d1 = sub(p2, p1)
  const d2 = sub(p4, p3)
  const den = cross(d1, d2)
  if (Math.abs(den) < 1e-12 * Math.max(1, len(d1) * len(d2))) return null
  const w = sub(p3, p1)
  const t = cross(w, d2) / den
  const u = cross(w, d1) / den
  return { p: add(p1, mul(d1, t)), t, u }
}

/** Основание перпендикуляра из точки p на прямую ab. */
export function foot(p: Pt, a: Pt, b: Pt): Pt {
  const d = sub(b, a)
  const t = dot(sub(p, a), d) / dot(d, d)
  return add(a, mul(d, t))
}

/** Соседи вершины в четырёхугольнике ABCD. */
export const NEIGHBORS: Record<VName, [VName, VName]> = { A: ['D', 'B'], B: ['A', 'C'], C: ['B', 'D'], D: ['C', 'A'] }

/** Точка, где биссектриса угла при вершине `vertex` встречает прямую, проходящую через вершины `s1` и `s2`. */
export function bisectorHit(q: Quad, vertex: VName, s1: VName, s2: VName): Pt | null {
  const [n1, n2] = NEIGHBORS[vertex]
  const o = q[vertex]
  const d = add(unit(sub(q[n1], o)), unit(sub(q[n2], o)))
  if (len(d) < 1e-9) return null
  const r = intersect(o, add(o, d), q[s1], q[s2])
  return r && r.t > 0 ? r.p : null
}

// ---------- числа и подписи ----------

/** Число по-русски: десятичная запятая и настоящий минус. */
export function fmt(n: number, digits = 1): string {
  const k = 10 ** digits
  const v = Math.round(n * k) / k
  const s = String(Object.is(v, -0) ? 0 : v).replace('.', ',')
  return s.startsWith('-') ? '−' + s.slice(1) : s
}

/** Число из рисунка (строка «3,5» или «3.5») → число. */
export function parseNum(s: string): number {
  return Number(s.replace(',', '.').replace('−', '-'))
}

export type Mark = { name: string; value: string; unknown: boolean }

/** Подпись на рисунке: «AB=5», «BM=?», «A=40°», «CAD=30°». */
export function parseMark(m: string): Mark | null {
  const i = m.indexOf('=')
  if (i <= 0) return null
  const name = m.slice(0, i).trim()
  const value = m.slice(i + 1).trim()
  if (!/^[A-Z]{1,3}$/.test(name) || !value) return null
  return { name, value, unknown: value === '?' }
}

/** Описание рисунка для программ экранного чтения: что нарисовано и что подписано. */
export function describeFig(spec: { marks?: string[]; legend?: string }, what: string): string {
  const parts: string[] = []
  for (const raw of spec.marks ?? []) {
    const m = parseMark(raw)
    if (!m) continue
    const val = m.unknown ? 'нужно найти' : m.value
    parts.push(m.name.length === 2 ? `${m.name} = ${val}` : `угол ${m.name} = ${val}`)
  }
  if (spec.legend) parts.push(spec.legend)
  return `Рисунок: ${what}${parts.length ? '. ' + parts.join(', ') : ''}`
}

// ---------- проекция на экран ----------

export type View = {
  w: number
  h: number
  /** Масштаб: сколько пикселей SVG в одной единице чертежа. */
  k: number
  X: (p: Pt) => number
  Y: (p: Pt) => number
  /** Точка чертежа → точка SVG. */
  S: (p: Pt) => XY
}

/** Вписывает набор точек в SVG ширины w: ось y переворачивается, вокруг остаются поля под подписи. */
export function fitView(
  pts: Pt[],
  o: { w: number; maxH: number; padX: number; padTop: number; padBottom: number; maxK?: number },
): View {
  const xs = pts.map((p) => p.x)
  const ys = pts.map((p) => p.y)
  const minX = Math.min(...xs)
  const maxX = Math.max(...xs)
  const minY = Math.min(...ys)
  const maxY = Math.max(...ys)
  const bw = Math.max(maxX - minX, 1e-6)
  const bh = Math.max(maxY - minY, 1e-6)
  const k = Math.min((o.w - 2 * o.padX) / bw, o.maxH / bh, o.maxK ?? 60)
  const ox = (o.w - bw * k) / 2
  const h = o.padTop + bh * k + o.padBottom
  const X = (p: Pt) => ox + (p.x - minX) * k
  const Y = (p: Pt) => o.padTop + (maxY - p.y) * k
  return { w: o.w, h, k, X, Y, S: (p) => [X(p), Y(p)] }
}

// ---------- примитивы SVG ----------

const vec = (a: XY, b: XY): XY => [b[0] - a[0], b[1] - a[1]]
const norm = (v: XY): XY => {
  const l = Math.hypot(v[0], v[1])
  return l < 1e-9 ? [0, 0] : [v[0] / l, v[1] / l]
}
const r1 = (x: number): string => String(Math.round(x * 100) / 100)
export const xyStr = (p: XY): string => `${r1(p[0])} ${r1(p[1])}`

/** Дуга радиуса r вокруг o между направлениями u и v (меньший из двух углов). */
export function arcPath(o: XY, u: XY, v: XY, r: number): string {
  const a = norm(u)
  const b = norm(v)
  const p1: XY = [o[0] + r * a[0], o[1] + r * a[1]]
  const p2: XY = [o[0] + r * b[0], o[1] + r * b[1]]
  const sweep = a[0] * b[1] - a[1] * b[0] > 0 ? 1 : 0
  return `M${xyStr(p1)}A${r1(r)} ${r1(r)} 0 0 ${sweep} ${xyStr(p2)}`
}

/** Знак прямого угла: квадратик со стороной s в углу o между направлениями u и v. */
export function rightPath(o: XY, u: XY, v: XY, s: number): string {
  const a = norm(u)
  const b = norm(v)
  const p1: XY = [o[0] + s * a[0], o[1] + s * a[1]]
  const p2: XY = [p1[0] + s * b[0], p1[1] + s * b[1]]
  const p3: XY = [o[0] + s * b[0], o[1] + s * b[1]]
  return `M${xyStr(p1)}L${xyStr(p2)}L${xyStr(p3)}`
}

/** Чёрточки «равны» на отрезке pq: n штук поперёк, по центру. */
export function tickPath(p: XY, q: XY, n: number, size = 7, gap = 4.5): string {
  const d = norm(vec(p, q))
  const nrm: XY = [-d[1], d[0]]
  const m: XY = [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2]
  let s = ''
  for (let i = 0; i < n; i++) {
    const off = (i - (n - 1) / 2) * gap
    const c: XY = [m[0] + d[0] * off, m[1] + d[1] * off]
    s += `M${xyStr([c[0] + (nrm[0] * size) / 2, c[1] + (nrm[1] * size) / 2])}L${xyStr([c[0] - (nrm[0] * size) / 2, c[1] - (nrm[1] * size) / 2])}`
  }
  return s
}

/** Стрелочки «параллельно» на отрезке pq (направление от p к q): n штук. */
export function chevPath(p: XY, q: XY, n: number, size = 5, gap = 6): string {
  const d = norm(vec(p, q))
  const nrm: XY = [-d[1], d[0]]
  const m: XY = [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2]
  let s = ''
  for (let i = 0; i < n; i++) {
    const off = (i - (n - 1) / 2) * gap
    const c: XY = [m[0] + d[0] * off, m[1] + d[1] * off]
    const apex: XY = [c[0] + d[0] * size * 0.6, c[1] + d[1] * size * 0.6]
    const l: XY = [c[0] - d[0] * size * 0.6 + nrm[0] * size, c[1] - d[1] * size * 0.6 + nrm[1] * size]
    const r: XY = [c[0] - d[0] * size * 0.6 - nrm[0] * size, c[1] - d[1] * size * 0.6 - nrm[1] * size]
    s += `M${xyStr(l)}L${xyStr(apex)}L${xyStr(r)}`
  }
  return s
}

/** Куда ставить подпись угла: на биссектрисе угла между направлениями u и v, на расстоянии r от вершины o. */
export function angleLabelAt(o: XY, u: XY, v: XY, r: number): XY {
  const a = norm(u)
  const b = norm(v)
  let d: XY = [a[0] + b[0], a[1] + b[1]]
  if (Math.hypot(d[0], d[1]) < 1e-6) d = [-a[1], a[0]]
  d = norm(d)
  return [o[0] + r * d[0], o[1] + r * d[1]]
}

/** Сдвиг точки p от центра c наружу на расстояние d. */
export function pushOut(p: XY, c: XY, d: number): XY {
  const u = norm(vec(c, p))
  return [p[0] + u[0] * d, p[1] + u[1] * d]
}

export const lerpXY = (p: XY, q: XY, t: number): XY => [p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t]

/** Лежит ли точка внутри многоугольника (метод луча). */
export function inPoly(p: XY, poly: XY[]): boolean {
  let inside = false
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i]
    const [xj, yj] = poly[j]
    if (yi > p[1] !== yj > p[1] && p[0] < ((xj - xi) * (p[1] - yi)) / (yj - yi) + xi) inside = !inside
  }
  return inside
}

/** Куда ставить подпись отрезка pq: точка на доле t отрезка, сдвинутая перпендикулярно от точки c (центра фигуры) на d. */
export function segLabelAt(p: XY, q: XY, c: XY, d: number, t = 0.5): XY {
  const m: XY = lerpXY(p, q, t)
  const tan = norm(vec(p, q))
  let n: XY = [-tan[1], tan[0]]
  const away = n[0] * (m[0] - c[0]) + n[1] * (m[1] - c[1])
  if (Math.abs(away) < 2) {
    // отрезок проходит через центр: подпись над ним (а у отвесного — слева)
    n = Math.abs(n[1]) < 0.2 ? [-Math.abs(n[0]), 0] : n[1] > 0 ? [-n[0], -n[1]] : n
  } else if (away < 0) {
    n = [-n[0], -n[1]]
  }
  return [m[0] + n[0] * d, m[1] + n[1] * d]
}

/** Середина набора точек: от неё подписи отодвигаются наружу. */
export function centroid(pts: XY[]): XY {
  const n = pts.length
  return [pts.reduce((s, p) => s + p[0], 0) / n, pts.reduce((s, p) => s + p[1], 0) / n]
}
