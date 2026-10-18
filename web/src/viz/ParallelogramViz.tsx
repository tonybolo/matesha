import { useState } from 'react'
import { Tex } from '../components/Tex'
import './ParallelogramViz.css'
import { Arc, Chevs, Num, RightMark, Seg, Shape, Ticks, Txt, VertexLabels } from './parDraw'
import {
  NEIGHBORS,
  P,
  Placer,
  VERTS,
  centroid,
  cross,
  dist,
  fixedView,
  fmt,
  intersect,
  parFromDiagonals,
  parallelogram,
  placeAngle,
  placeSeg,
  pushOut,
  sub,
  tn,
  trapezoid,
  type Quad,
  type VName,
  type XY,
} from './parKit'
import { Stepper } from './Stepper'

const W = 320
const deg = (n: number) => `${fmt(n, 0)}°`
const dirTo = (from: XY, to: XY): XY => [to[0] - from[0], to[1] - from[1]]
const mid2 = (p: XY, q: XY): XY => [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2]

/** Ползунок со счётчиком «−/+»: угол, длина и т. п. */
function Dial({ label, value, min, max, step, onChange, format }: { label: string; value: number; min: number; max: number; step: number; onChange: (n: number) => void; format: (n: number) => string }) {
  return (
    <>
      <div className="pk-slider-row">
        <span className="slider-label">{label}</span>
        <Stepper compact aria={label} value={value} min={min} max={max} step={step} onChange={onChange} format={format} />
      </div>
      <input className="slider" type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(Number(e.target.value))} aria-label={label} />
    </>
  )
}

/** Параллелограмм из картинки урока: стороны, углы, диагонали или признаки (режим задаёт preset). */
export function ParallelogramViz({ preset }: { preset?: string }) {
  if (preset === 'angles') return <AnglesPanel />
  if (preset === 'diagonals') return <DiagonalsPanel />
  if (preset === 'signs') return <SignsPanel />
  return <SidesPanel />
}

// ---------------------------------------------------------------------------
// Стороны и периметр
// ---------------------------------------------------------------------------

const SIDE_PRESETS: { name: string; a: number; b: number; ang: number }[] = [
  { name: 'Обычный', a: 7, b: 4, ang: 65 },
  { name: 'Низкий и длинный', a: 9, b: 3, ang: 35 },
  { name: 'Прямоугольник', a: 6, b: 4, ang: 90 },
  { name: 'Ромб', a: 5, b: 5, ang: 70 },
]

function SidesPanel() {
  const [s, setS] = useState({ a: 7, b: 4, ang: 65 })
  const { a, b, ang } = s
  const set = (patch: Partial<typeof s>) => setS((p) => ({ ...p, ...patch }))
  const q = parallelogram(a, b, ang)
  const view = fixedView(VERTS.map((n) => q[n]), { w: W, h: 152, k: 17, padBottom: 32, padTop: 18 })
  const pts = Object.fromEntries(VERTS.map((n) => [n, view.S(q[n])])) as Record<VName, XY>
  const c = centroid(VERTS.map((n) => pts[n]))
  const pl = new Placer()
  for (const n of VERTS) pl.fix(pushOut(pts[n], c, 13), n)
  const sides: { p: VName; q: VName; cls: string; tick: string; n: number; len: number }[] = [
    { p: 'A', q: 'B', cls: 'pk-s1', tick: 'pk-tick c1', n: 1, len: b },
    { p: 'C', q: 'D', cls: 'pk-s1', tick: 'pk-tick c1', n: 1, len: b },
    { p: 'B', q: 'C', cls: 'pk-s2', tick: 'pk-tick c2', n: 2, len: a },
    { p: 'A', q: 'D', cls: 'pk-s2', tick: 'pk-tick c2', n: 2, len: a },
  ]
  for (const sd of sides) pl.dot(mid2(pts[sd.p], pts[sd.q]))
  const labels = sides.map((sd) => ({ sd, at: placeSeg(pl, pts[sd.p], pts[sd.q], c, fmt(sd.len)) }))
  const note =
    ang === 90 ? 'Угол 90°: получился прямоугольник. Он тоже параллелограмм.' : a === b ? 'Все стороны равны: это ромб. Он тоже параллелограмм.' : 'Меняй наклон: стороны и периметр остаются прежними.'
  return (
    <div className="viz">
      <div className="viz-title">Крутим параллелограмм: что остаётся одинаковым?</div>
      <div className="chips">
        {SIDE_PRESETS.map((p) => (
          <button key={p.name} className={`chip wide ${p.a === a && p.b === b && p.ang === ang ? 'on' : ''}`} onClick={() => setS({ a: p.a, b: p.b, ang: p.ang })}>
            {p.name}
          </button>
        ))}
      </div>
      <svg viewBox={`0 0 ${W} 152`} className="pk-svg" role="img" aria-label={`Параллелограмм ABCD: AB = CD = ${fmt(b)}, BC = AD = ${fmt(a)}, угол A равен ${deg(ang)}`}>
        <Shape pts={VERTS.map((n) => pts[n])} edge="" />
        {sides.map((sd) => (
          <Seg key={sd.p + sd.q} p={pts[sd.p]} q={pts[sd.q]} className={sd.cls} />
        ))}
        {sides.map((sd) => (
          <Ticks key={'t' + sd.p + sd.q} p={pts[sd.p]} q={pts[sd.q]} n={sd.n} className={sd.tick} />
        ))}
        {ang === 90 &&
          VERTS.map((n) => {
            const [n1, n2] = NEIGHBORS[n]
            return <RightMark key={n} o={pts[n]} u={dirTo(pts[n], pts[n1])} v={dirTo(pts[n], pts[n2])} s={8} />
          })}
        {labels.map(({ sd, at }) => (
          <Txt key={'l' + sd.p + sd.q} at={at} className="pk-m">
            {fmt(sd.len)}
          </Txt>
        ))}
        <VertexLabels V={q} view={view} center={c} />
      </svg>
      <div className="pk-controls">
        <Num label="AD =" aria="сторона AD" value={a} min={3} max={9} onChange={(v) => set({ a: v })} format={(n) => fmt(n, 0)} />
        <Num label="AB =" aria="сторона AB" value={b} min={2} max={6} onChange={(v) => set({ b: v })} format={(n) => fmt(n, 0)} />
      </div>
      <Dial label="Наклон (угол A)" value={ang} min={30} max={150} step={5} onChange={(v) => set({ ang: v })} format={deg} />
      <div className="readout pk-readout" aria-live="polite">
        <p>
          Напротив друг друга: <Tex tex={`AB=CD=${tn(b)}`} /> и <Tex tex={`BC=AD=${tn(a)}`} />. Противоположные стороны равны.
        </p>
        <p>
          Периметр: <Tex tex={`P=${tn(b)}+${tn(a)}+${tn(b)}+${tn(a)}=${tn(2 * (a + b))}`} />, то есть <Tex tex={`2\\cdot(${tn(a)}+${tn(b)})=${tn(2 * (a + b))}`} />.
        </p>
        <p className="muted">{note}</p>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Углы
// ---------------------------------------------------------------------------

function AnglesPanel() {
  const [ang, setAng] = useState(65)
  const other = 180 - ang
  const q = parallelogram(7, 4, ang)
  const H = 206
  const view = fixedView(VERTS.map((n) => q[n]), { w: W, h: H - 56, k: 24, padBottom: 30, padTop: 24 })
  const pts = Object.fromEntries(VERTS.map((n) => [n, view.S(q[n])])) as Record<VName, XY>
  const c = centroid(VERTS.map((n) => pts[n]))
  const pl = new Placer()
  for (const n of VERTS) pl.fix(pushOut(pts[n], c, 13), n)
  const acute: VName[] = ['A', 'C']
  const labelNodes = VERTS.map((n) => {
    const [n1, n2] = NEIGHBORS[n]
    const u = dirTo(pts[n], pts[n1])
    const v = dirTo(pts[n], pts[n2])
    const first = acute.includes(n)
    const val = first ? ang : other
    const at = placeAngle(pl, pts[n], u, v, first ? 20 : 25, deg(val))
    return { n, u, v, first, val, at }
  })
  // полоска «развёрнутый угол»: соседние углы вместе заполняют 180°
  const bx = 20
  const bw = W - 40
  const by = H - 40
  const split = bx + (ang / 180) * bw
  const sum = ang + other
  return (
    <div className="viz">
      <div className="viz-title">Углы параллелограмма: качаем рамку</div>
      <div className="chips">
        {[40, 65, 90, 130].map((v) => (
          <button key={v} className={`chip ${ang === v ? 'on' : ''}`} onClick={() => setAng(v)} aria-label={`Угол A равен ${v} градусов`}>
            {v}°
          </button>
        ))}
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="pk-svg" role="img" aria-label={`Параллелограмм ABCD: углы A и C по ${deg(ang)}, углы B и D по ${deg(other)}. Соседние углы вместе дают 180 градусов`}>
        <Shape pts={VERTS.map((n) => pts[n])} />
        <Chevs p={pts.A} q={pts.D} n={1} />
        <Chevs p={pts.B} q={pts.C} n={1} />
        <Chevs p={pts.A} q={pts.B} n={2} />
        <Chevs p={pts.D} q={pts.C} n={2} />
        {labelNodes.map((l) => (
          <g key={l.n}>
            <Arc o={pts[l.n]} u={l.u} v={l.v} r={20} className={l.first ? 'pk-arc c1' : 'pk-arc c2'} />
            {!l.first && <Arc o={pts[l.n]} u={l.u} v={l.v} r={25} className="pk-arc c2" />}
          </g>
        ))}
        {labelNodes.map((l) => (
          <Txt key={'t' + l.n} at={l.at} className="pk-m in">
            {deg(l.val)}
          </Txt>
        ))}
        <VertexLabels V={q} view={view} center={c} />
        <rect x={bx} y={by} width={split - bx} height={20} className="pv-bar a" />
        <rect x={split} y={by} width={bx + bw - split} height={20} className="pv-bar b" />
        <Txt at={[(bx + split) / 2, by + 10]} className="pk-m flat">{`A ${deg(ang)}`}</Txt>
        <Txt at={[(split + bx + bw) / 2, by + 10]} className="pk-m flat">{`B ${deg(other)}`}</Txt>
        <Txt at={[W / 2, by + 34]} className="pk-note">{`рядом лежащие углы A и B вместе: ${deg(sum)}`}</Txt>
      </svg>
      <Dial label="Угол A" value={ang} min={30} max={150} step={5} onChange={setAng} format={deg} />
      <div className="readout pk-readout" aria-live="polite">
        <p>
          Напротив: <Tex tex={`\\angle A=\\angle C=${tn(ang, 0)}^\\circ`} />, <Tex tex={`\\angle B=\\angle D=${tn(other, 0)}^\\circ`} />. Противоположные углы равны.
        </p>
        <p>
          Рядом: <Tex tex={`\\angle A+\\angle B=${tn(ang, 0)}^\\circ+${tn(other, 0)}^\\circ=180^\\circ`} />.
        </p>
        <p>
          Все четыре: <Tex tex={`2\\cdot(${tn(ang, 0)}^\\circ+${tn(other, 0)}^\\circ)=360^\\circ`} />.
        </p>
        {ang === 90 && <p className="muted">Все углы по 90°: это прямоугольник. Он тоже параллелограмм.</p>}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Диагонали
// ---------------------------------------------------------------------------

function DiagonalsPanel() {
  const [s, setS] = useState({ d1: 12, d2: 8, phi: 60 })
  const { d1, d2, phi } = s
  const set = (patch: Partial<typeof s>) => setS((p) => ({ ...p, ...patch }))
  const sh = parFromDiagonals(d1, d2, phi)
  const q = parallelogram(sh.a, sh.b, sh.ang)
  const o = intersect(q.A, q.C, q.B, q.D)!.p
  const H = 180
  const view = fixedView([...VERTS.map((n) => q[n]), o], { w: W, h: H, k: 16, padBottom: 32, padTop: 22 })
  const pts = Object.fromEntries(VERTS.map((n) => [n, view.S(q[n])])) as Record<VName, XY>
  const O = view.S(o)
  const c = centroid(VERTS.map((n) => pts[n]))
  const pl = new Placer()
  for (const n of VERTS) pl.fix(pushOut(pts[n], c, 13), n)
  pl.dot(O)
  pl.fix([O[0], O[1] - 12], 'O')
  const halves: { p: XY; q: XY; v: number; name: string; cls: string; n: number; tick: string }[] = [
    { p: pts.A, q: O, v: d1 / 2, name: 'AO', cls: 'pk-s2', n: 1, tick: 'pk-tick c2' },
    { p: O, q: pts.C, v: d1 / 2, name: 'OC', cls: 'pk-s2', n: 1, tick: 'pk-tick c2' },
    { p: pts.B, q: O, v: d2 / 2, name: 'BO', cls: 'pk-s4', n: 2, tick: 'pk-tick' },
    { p: O, q: pts.D, v: d2 / 2, name: 'OD', cls: 'pk-s4', n: 2, tick: 'pk-tick' },
  ]
  for (const h of halves) pl.dot(mid2(h.p, h.q))
  const labels = halves.map((h) => ({ h, at: placeSeg(pl, h.p, h.q, O, fmt(h.v)) }))
  const AB = dist(q.A, q.B)
  const perim = d1 / 2 + d2 / 2 + AB
  return (
    <div className="viz">
      <div className="viz-title">Диагонали параллелограмма делятся пополам</div>
      <svg viewBox={`0 0 ${W} ${H}`} className="pk-svg" role="img" aria-label={`Параллелограмм ABCD с диагоналями AC = ${d1} и BD = ${d2}, точка O делит каждую диагональ пополам: AO = OC = ${d1 / 2}, BO = OD = ${d2 / 2}`}>
        <Shape pts={VERTS.map((n) => pts[n])} />
        <Seg p={pts.A} q={pts.C} className="pk-diag" />
        <Seg p={pts.B} q={pts.D} className="pk-diag" />
        {halves.map((h) => (
          <Seg key={h.name} p={h.p} q={h.q} className={h.cls} />
        ))}
        {halves.map((h) => (
          <Ticks key={'t' + h.name} p={h.p} q={h.q} n={h.n} className={h.tick} />
        ))}
        <Arc o={O} u={dirTo(O, pts.A)} v={dirTo(O, pts.B)} r={13} className="pk-arc c3" />
        <circle cx={O[0]} cy={O[1]} r={3.4} className="pk-dot" />
        {labels.map(({ h, at }) => (
          <Txt key={'l' + h.name} at={at} className="pk-m in">
            {fmt(h.v)}
          </Txt>
        ))}
        <Txt at={[O[0], O[1] - 12]} className="pk-pt in">O</Txt>
        <VertexLabels V={q} view={view} center={c} />
      </svg>
      <div className="pk-controls">
        <Num label="AC =" aria="диагональ AC" value={d1} min={8} max={12} step={2} onChange={(v) => set({ d1: v })} format={(n) => fmt(n, 0)} />
        <Num label="BD =" aria="диагональ BD" value={d2} min={6} max={10} step={2} onChange={(v) => set({ d2: v })} format={(n) => fmt(n, 0)} />
      </div>
      <Dial label="Угол AOB между диагоналями" value={phi} min={30} max={150} step={5} onChange={(v) => set({ phi: v })} format={deg} />
      <div className="readout pk-readout" aria-live="polite">
        <p>
          Диагональ <Tex tex={`AC=${d1}`} /> делится пополам: <Tex tex={`AO=OC=${d1 / 2}`} />.
        </p>
        <p>
          Диагональ <Tex tex={`BD=${d2}`} /> тоже: <Tex tex={`BO=OD=${d2 / 2}`} />.
        </p>
        <p>
          Треугольник <Tex tex="AOB" />: стороны <Tex tex={`${d1 / 2}`} />, <Tex tex={`${d2 / 2}`} /> и <Tex tex={`AB\\approx ${tn(AB)}`} />, периметр <Tex tex={`\\approx ${tn(perim)}`} />.
        </p>
        <p className="muted">Меняй длины и угол: половинки каждой диагонали всегда остаются равными.</p>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Признаки: что получается, если выполнено одно условие
// ---------------------------------------------------------------------------

type Sel = 0 | 1 | 2 | 3 | 4 | 5

const SIGN_CHIPS: { sel: Sel; label: string }[] = [
  { sel: 0, label: 'Признак 1' },
  { sel: 1, label: 'Признак 2' },
  { sel: 2, label: 'Признак 3' },
]
const FEW_CHIPS: { sel: Sel; label: string }[] = [
  { sel: 3, label: 'только BC ∥ AD' },
  { sel: 4, label: 'только AB = CD' },
  { sel: 5, label: 'только AO = OC' },
]

/** Параметр ползунка для выбранного условия: [мин, макс, шаг, по умолчанию, подпись]. */
const DIAL: Record<Sel, [number, number, number, number, string]> = {
  0: [40, 140, 5, 65, 'Наклон (угол A)'],
  1: [40, 140, 5, 65, 'Наклон (угол A)'],
  2: [40, 140, 5, 65, 'Наклон (угол A)'],
  3: [2, 6, 1, 3, 'Длина верхней стороны BC'],
  4: [2, 6, 1, 3, 'Длина верхней стороны BC'],
  5: [1, 3, 0.5, 1.5, 'Длина нижней половинки OD'],
}

function signShape(sel: Sel, p: number): Quad {
  if (sel <= 2) return parallelogram(7, 4, p)
  if (sel === 3) return trapezoid(7, p, 3, 1)
  if (sel === 4) return trapezoid(7, p, 3, (7 - p) / 2)
  return { A: P(-3, 0), B: P(0, 3.5), C: P(3, 0), D: P(0, -p) }
}

const near = (x: number, y: number) => Math.abs(x - y) < 1e-6 * Math.max(1, Math.abs(x), Math.abs(y))

type Row = { key: string; tex: string; ok: boolean; vals?: [number, number]; given: boolean }

function signRows(sel: Sel, q: Quad): { rows: Row[]; isPar: boolean; name: string } {
  const AB = dist(q.A, q.B)
  const BC = dist(q.B, q.C)
  const CD = dist(q.C, q.D)
  const AD = dist(q.A, q.D)
  const parAB = Math.abs(cross(sub(q.B, q.A), sub(q.C, q.D))) < 1e-6 * AB * CD
  const parBC = Math.abs(cross(sub(q.C, q.B), sub(q.D, q.A))) < 1e-6 * BC * AD
  const o = intersect(q.A, q.C, q.B, q.D)!.p
  const AO = dist(q.A, o)
  const OC = dist(o, q.C)
  const BO = dist(q.B, o)
  const OD = dist(o, q.D)
  const given: Record<Sel, string[]> = { 0: ['pAB', 'eAB'], 1: ['eAB', 'eBC'], 2: ['eAO', 'eBO'], 3: ['pBC'], 4: ['eAB'], 5: ['eAO'] }
  const all: Omit<Row, 'given'>[] = [
    { key: 'pAB', tex: 'AB\\parallel CD', ok: parAB },
    { key: 'pBC', tex: 'BC\\parallel AD', ok: parBC },
    { key: 'eAB', tex: 'AB=CD', ok: near(AB, CD), vals: [AB, CD] },
    { key: 'eBC', tex: 'BC=AD', ok: near(BC, AD), vals: [BC, AD] },
    { key: 'eAO', tex: 'AO=OC', ok: near(AO, OC), vals: [AO, OC] },
    { key: 'eBO', tex: 'BO=OD', ok: near(BO, OD), vals: [BO, OD] },
  ]
  const show = sel === 2 || sel === 5 ? all : all.slice(0, 4)
  const isPar = parAB && parBC
  let name = 'параллелограмм'
  if (!isPar) {
    if (parAB !== parBC) name = near(AB, CD) ? 'равнобедренная трапеция' : 'трапеция'
    else if (near(AB, BC) && near(CD, AD)) name = '«воздушный змей»'
    else name = 'обычный четырёхугольник'
  }
  return { rows: show.map((r) => ({ ...r, given: given[sel].includes(r.key) })), isPar, name }
}

function SignsPanel() {
  const [sel, setSel] = useState<Sel>(0)
  const [val, setVal] = useState(DIAL[0][3])
  const pick = (s: Sel) => {
    setSel(s)
    setVal(DIAL[s][3])
  }
  const [min, max, step, , dialLabel] = DIAL[sel]
  const q = signShape(sel, val)
  const H = 168
  const view = fixedView(VERTS.map((n) => q[n]), { w: W, h: H, k: 26, padBottom: 30, padTop: 26, center: true })
  const pts = Object.fromEntries(VERTS.map((n) => [n, view.S(q[n])])) as Record<VName, XY>
  const c = centroid(VERTS.map((n) => pts[n]))
  const o = intersect(q.A, q.C, q.B, q.D)!.p
  const O = view.S(o)
  const { rows, isPar, name } = signRows(sel, q)
  const showDiag = sel === 2 || sel === 5
  const tick = (p: XY, qq: XY, n: number, cls = 'pk-tick c1') => <Ticks p={p} q={qq} n={n} className={cls} />
  const sideLen = (a: VName, b: VName) => fmt(dist(q[a], q[b]))
  return (
    <div className="viz">
      <div className="viz-title">Признаки: что гарантирует параллелограмм?</div>
      <div className="chips">
        {SIGN_CHIPS.map((x) => (
          <button key={x.sel} className={`chip wide ${sel === x.sel ? 'on' : ''}`} onClick={() => pick(x.sel)}>
            {x.label}
          </button>
        ))}
      </div>
      <div className="pv-few">Мало условий:</div>
      <div className="chips">
        {FEW_CHIPS.map((x) => (
          <button key={x.sel} className={`chip wide ${sel === x.sel ? 'on' : ''}`} onClick={() => pick(x.sel)}>
            {x.label}
          </button>
        ))}
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="pk-svg" role="img" aria-label={`Четырёхугольник ABCD. Условие: ${SIGN_CHIPS.concat(FEW_CHIPS).find((x) => x.sel === sel)?.label}. Получилось: ${name}`}>
        <Shape pts={VERTS.map((n) => pts[n])} edge="" />
        {showDiag && <Seg p={pts.A} q={pts.C} className="pk-diag" />}
        {showDiag && <Seg p={pts.B} q={pts.D} className="pk-diag" />}
        {(sel === 0 || sel === 4 || sel === 1) && (
          <>
            {tick(pts.A, pts.B, 1)}
            {tick(pts.C, pts.D, 1)}
          </>
        )}
        {sel === 1 && (
          <>
            {tick(pts.B, pts.C, 2, 'pk-tick c2')}
            {tick(pts.A, pts.D, 2, 'pk-tick c2')}
          </>
        )}
        {sel === 0 && (
          <>
            <Chevs p={pts.A} q={pts.B} n={1} />
            <Chevs p={pts.D} q={pts.C} n={1} />
          </>
        )}
        {sel === 3 && (
          <>
            <Chevs p={pts.B} q={pts.C} n={1} />
            <Chevs p={pts.A} q={pts.D} n={1} />
          </>
        )}
        {sel === 2 && (
          <>
            {tick(pts.A, O, 1)}
            {tick(O, pts.C, 1)}
            {tick(pts.B, O, 2, 'pk-tick c2')}
            {tick(O, pts.D, 2, 'pk-tick c2')}
          </>
        )}
        {sel === 5 && (
          <>
            {tick(pts.A, O, 1)}
            {tick(O, pts.C, 1)}
          </>
        )}
        <Shape pts={VERTS.map((n) => pts[n])} fill="" />
        {showDiag && <circle cx={O[0]} cy={O[1]} r={3.2} className="pk-dot" />}
        {showDiag && (
          <Txt at={[O[0] + 11, O[1] - 9]} className="pk-pt in">
            O
          </Txt>
        )}
        <VertexLabels V={q} view={view} center={c} />
      </svg>
      <Dial label={dialLabel} value={val} min={min} max={max} step={step} onChange={setVal} format={(n) => (sel <= 2 ? deg(n) : fmt(n))} />
      <div className="readout pk-readout" aria-live="polite">
        <ul className="pv-rows">
          {rows.map((r) => (
            <li key={r.key}>
              <Tex tex={r.tex} />
              {r.vals && (
                <span className="muted">
                  {' '}
                  ({fmt(r.vals[0])} и {fmt(r.vals[1])})
                </span>
              )}{' '}
              <span className={r.ok ? 'pk-ok' : 'pk-no'}>{r.ok ? '✔ да' : '✘ нет'}</span>
              {r.given && <span className="pk-tag">дано</span>}
            </li>
          ))}
        </ul>
        <p className="pv-verdict">
          {isPar ? (
            <>
              Это <span className="pk-ok">параллелограмм</span>: условие выполнено, и остальное получилось само.
            </>
          ) : (
            <>
              Это не параллелограмм, а <span className="pk-no">{name}</span>. Одного условия мало: проверь строки без отметки «дано».
            </>
          )}
        </p>
        {sel === 4 && !isPar && (
          <p className="muted">
            Боковые стороны <Tex tex={`AB=CD=${tn(dist(q.A, q.B))}`} />, а основания разные: <Tex tex={`BC=${tn(dist(q.B, q.C))}`} /> и <Tex tex={`AD=${sideLen('A', 'D')}`} />.
          </p>
        )}
      </div>
    </div>
  )
}
