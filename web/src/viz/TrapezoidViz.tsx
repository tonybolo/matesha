import { useState, type ReactNode } from 'react'
import { Tex } from '../components/Tex'
import { Arc, Chevs, Num, RightMark, Seg, Shape, Ticks, Txt, VertexLabels } from './parDraw'
import { NEIGHBORS, Placer, VERTS, angleAt, centroid, dist, fixedView, fmt, foot, placeAngle, placeSeg, pushOut, tn, trapezoid, trapezoidKind, type VName, type XY } from './parKit'
import { Stepper } from './Stepper'

const W = 320
const H = 168
const deg = (n: number) => `${fmt(n, 0)}°`
const dirTo = (from: XY, to: XY): XY => [to[0] - from[0], to[1] - from[1]]

type State = { a: number; b: number; h: number; s: number }

const PRESETS: { name: string; v: State }[] = [
  { name: 'Равнобедренная', v: { a: 10, b: 4, h: 4, s: 3 } },
  { name: 'Прямоугольная', v: { a: 9, b: 5, h: 4, s: 0 } },
  { name: 'Обычная', v: { a: 10, b: 4, h: 3, s: 1 } },
]

/** Трапеция: основания, боковые стороны, высота; фигура сама называет свой вид. */
export function TrapezoidViz() {
  const [v, setV] = useState<State>(PRESETS[0].v)
  const [diag, setDiag] = useState(false)
  const { a, b, h, s } = v
  const set = (patch: Partial<State>) =>
    setV((p) => {
      const n = { ...p, ...patch }
      n.b = Math.min(n.b, n.a - 1)
      n.s = Math.max(-2, Math.min(n.a - n.b + 2, n.s))
      return n
    })
  const kind = trapezoidKind(a, b, s)

  const q = trapezoid(a, b, h, s)
  const view = fixedView(VERTS.map((n) => q[n]), { w: W, h: H, k: 21, padBottom: 32, padTop: 24 })
  const pts = Object.fromEntries(VERTS.map((n) => [n, view.S(q[n])])) as Record<VName, XY>
  const c = centroid(VERTS.map((n) => pts[n]))
  const base = foot(q.B, q.A, q.D)
  const HF = view.S(base)
  const AB = dist(q.A, q.B)
  const CD = dist(q.C, q.D)
  const angs = Object.fromEntries(VERTS.map((n) => [n, angleAt(q[NEIGHBORS[n][0]], q[n], q[NEIGHBORS[n][1]])])) as Record<VName, number>
  const AC = dist(q.A, q.C)
  const BD = dist(q.B, q.D)

  const pl = new Placer()
  for (const n of VERTS) pl.fix(pushOut(pts[n], c, 13), n)
  pl.dot([(pts.A[0] + pts.B[0]) / 2, (pts.A[1] + pts.B[1]) / 2])
  pl.dot([(pts.C[0] + pts.D[0]) / 2, (pts.C[1] + pts.D[1]) / 2])

  const nodes: ReactNode[] = []
  let key = 0
  const add = (n: ReactNode) => nodes.push(<g key={key++}>{n}</g>)

  add(<Shape pts={VERTS.map((n) => pts[n])} edge="" />)
  if (diag) {
    add(<Seg p={pts.A} q={pts.C} className="pk-diag" />)
    add(<Seg p={pts.B} q={pts.D} className="pk-diag" />)
  }
  // высота (если боковая сторона AB сама перпендикулярна основаниям, она и есть высота: отдельно не рисуем)
  const heightIsSide = s === 0
  const sgn = c[0] >= HF[0] ? 1 : -1
  if (!heightIsSide) {
    if (HF[0] < pts.A[0] - 0.5) add(<Seg p={HF} q={pts.A} className="pk-aux" />)
    if (HF[0] > pts.D[0] + 0.5) add(<Seg p={HF} q={pts.D} className="pk-aux" />)
    add(<Seg p={pts.B} q={HF} className="pk-height" />)
    add(<RightMark o={HF} u={dirTo(HF, pts.B)} v={[sgn, 0]} s={8} />)
  }
  // стороны: основания — жёлтые, боковые — синие
  add(<Seg p={pts.A} q={pts.D} className="pk-s2" />)
  add(<Seg p={pts.B} q={pts.C} className="pk-s2" />)
  add(<Seg p={pts.A} q={pts.B} className="pk-s1" />)
  add(<Seg p={pts.D} q={pts.C} className="pk-s1" />)
  add(<Chevs p={pts.A} q={pts.D} n={1} />)
  add(<Chevs p={pts.B} q={pts.C} n={1} />)
  if (kind === 'iso') {
    add(<Ticks p={pts.A} q={pts.B} n={1} className="pk-tick c1" />)
    add(<Ticks p={pts.D} q={pts.C} n={1} className="pk-tick c1" />)
  }
  if (kind === 'right') {
    const rv: VName[] = s === 0 ? ['A', 'B'] : ['D', 'C']
    for (const n of rv) {
      const [n1, n2] = NEIGHBORS[n]
      add(<RightMark o={pts[n]} u={dirTo(pts[n], pts[n1])} v={dirTo(pts[n], pts[n2])} s={9} />)
    }
  }
  if (!heightIsSide) pl.dot([(pts.B[0] + HF[0]) / 2, (pts.B[1] + HF[1]) / 2])

  // углы (прямые углы помечены квадратиком, без дуги)
  const angleNodes: ReactNode[] = []
  for (const n of VERTS) {
    const [n1, n2] = NEIGHBORS[n]
    const u = dirTo(pts[n], pts[n1])
    const w = dirTo(pts[n], pts[n2])
    const isRightAngle = Math.abs(angs[n] - 90) < 1e-6
    if (!isRightAngle) add(<Arc o={pts[n]} u={u} v={w} r={17} className="pk-arc" />)
    const at = placeAngle(pl, pts[n], u, w, 17, deg(angs[n]))
    angleNodes.push(
      <Txt key={'g' + n} at={at} className="pk-m in">
        {deg(angs[n])}
      </Txt>,
    )
  }
  // длины
  const sideLabels: ReactNode[] = []
  const sl = (p: XY, q2: XY, text: string, k: string) => {
    const at = placeSeg(pl, p, q2, c, text)
    sideLabels.push(
      <Txt key={k} at={at} className="pk-m">
        {text}
      </Txt>,
    )
  }
  sl(pts.A, pts.D, fmt(a), 'ad')
  sl(pts.B, pts.C, fmt(b), 'bc')
  sl(pts.A, pts.B, fmt(AB), 'ab')
  sl(pts.D, pts.C, fmt(CD), 'cd')
  if (!heightIsSide) sl(pts.B, HF, `h=${fmt(h)}`, 'h')

  const name = kind === 'iso' ? 'равнобедренная' : kind === 'right' ? 'прямоугольная' : 'обычная'
  const angAB = angs.A + angs.B
  const angCD = angs.C + angs.D

  return (
    <div className="viz">
      <div className="viz-title">Какая это трапеция?</div>
      <div className="chips">
        {PRESETS.map((p) => (
          <button key={p.name} className={`chip wide ${p.v.a === a && p.v.b === b && p.v.h === h && p.v.s === s ? 'on' : ''}`} onClick={() => setV(p.v)}>
            {p.name}
          </button>
        ))}
        <button className={`chip wide ${diag ? 'on' : ''}`} aria-pressed={diag} onClick={() => setDiag(!diag)}>
          Диагонали
        </button>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="pk-svg" role="img" aria-label={`${name} трапеция ABCD: основания AD = ${fmt(a)} и BC = ${fmt(b)}, высота ${fmt(h)}, боковые стороны AB = ${fmt(AB)} и CD = ${fmt(CD)}`}>
        {nodes}
        {angleNodes}
        {sideLabels}
        <VertexLabels V={q} view={view} center={c} />
      </svg>
      <div className="pk-controls">
        <Num label="AD =" aria="основание AD" value={a} min={4} max={10} onChange={(x) => set({ a: x })} format={(n) => fmt(n, 0)} />
        <Num label="BC =" aria="основание BC" value={b} min={2} max={a - 1} onChange={(x) => set({ b: x })} format={(n) => fmt(n, 0)} />
        <Num label="h =" aria="высота" value={h} min={2} max={5} onChange={(x) => set({ h: x })} format={(n) => fmt(n, 0)} />
      </div>
      <div className="pk-slider-row">
        <span className="slider-label">Сдвиг верхнего основания</span>
        <Stepper compact aria="сдвиг верхнего основания" value={s} min={-2} max={a - b + 2} step={1} onChange={(x) => set({ s: x })} format={(n) => fmt(n, 0)} />
      </div>
      <input className="slider" type="range" min={-2} max={a - b + 2} step={1} value={s} onChange={(e) => set({ s: Number(e.target.value) })} aria-label="Сдвиг верхнего основания" />
      <div className="readout pk-readout" aria-live="polite">
        {kind === 'iso' && (
          <p>
            Это <span className="pk-tag">равнобедренная</span> трапеция: боковые стороны равны, <Tex tex={`AB=CD=${tn(AB)}`} />. Углы при основании равны: <Tex tex={`\\angle A=\\angle D=${tn(angs.A, 0)}^\\circ`} />.
          </p>
        )}
        {kind === 'right' && (
          <p>
            Это <span className="pk-tag">прямоугольная</span> трапеция: боковая сторона <Tex tex={s === 0 ? 'AB' : 'CD'} /> перпендикулярна основаниям. Она же высота: <Tex tex={`${s === 0 ? 'AB' : 'CD'}=h=${tn(h)}`} />.
          </p>
        )}
        {kind === 'plain' && (
          <p>
            Это <span className="pk-tag">обычная</span> трапеция: боковые стороны разные, <Tex tex={`AB=${tn(AB)}`} /> и <Tex tex={`CD=${tn(CD)}`} />.
          </p>
        )}
        <p>
          Углы при боковой стороне <Tex tex="AB" />: <Tex tex={`\\angle A+\\angle B=${tn(angs.A, 0)}^\\circ+${tn(angs.B, 0)}^\\circ=${tn(angAB, 0)}^\\circ`} />.
        </p>
        <p>
          При стороне <Tex tex="CD" />: <Tex tex={`\\angle C+\\angle D=${tn(angs.C, 0)}^\\circ+${tn(angs.D, 0)}^\\circ=${tn(angCD, 0)}^\\circ`} />.
        </p>
        {diag && (
          <p>
            Диагонали: <Tex tex={`AC=${tn(AC)}`} />, <Tex tex={`BD=${tn(BD)}`} />.{' '}
            {Math.abs(AC - BD) < 1e-9 ? 'Они равны: это признак равнобедренной трапеции.' : 'Они разные: у равнобедренной трапеции диагонали были бы равны.'}
          </p>
        )}
      </div>
    </div>
  )
}
