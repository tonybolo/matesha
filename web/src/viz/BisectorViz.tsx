import { useState, type ReactNode } from 'react'
import { Tex } from '../components/Tex'
import './BisectorViz.css'
import { Arc, Chevs, Dot, Num, Seg, Shape, Ticks, Txt, VertexLabels } from './parDraw'
import { Placer, VERTS, angleAt, bisectorHit, centroid, dist, fixedView, fmt, parallelogram, placeAngle, placeSeg, pushOut, tn, type Pt, type VName, type XY } from './parKit'
import { Stepper } from './Stepper'

const W = 320
const H = 178
const deg = (n: number) => `${fmt(n, 0)}°`
const dirTo = (from: XY, to: XY): XY => [to[0] - from[0], to[1] - from[1]]

type Mode = 'A' | 'D' | 'AD'

const STEPS = ['Биссектриса делит угол пополам', 'Накрест лежащие углы равны', 'Треугольник равнобедренный']

/** Биссектриса угла параллелограмма отсекает равнобедренный треугольник: по шагам, для угла A, угла D и для обоих сразу. */
export function BisectorViz() {
  const [s, setS] = useState({ a: 8, b: 5, ang: 70 })
  const [mode, setMode] = useState<Mode>('A')
  const [step, setStep] = useState(1)
  const { a, b, ang } = s
  const set = (patch: Partial<typeof s>) => setS((p) => ({ ...p, ...patch }))
  const setA = (v: number) => setS((p) => ({ ...p, a: v, b: Math.min(p.b, v - 1) }))

  const q = parallelogram(a, b, ang)
  const view = fixedView(VERTS.map((n) => q[n]), { w: W, h: H, k: 21, padBottom: 30, padTop: 22 })
  const pts = Object.fromEntries(VERTS.map((n) => [n, view.S(q[n])])) as Record<VName, XY>
  const c = centroid(VERTS.map((n) => pts[n]))
  const pl = new Placer()
  for (const n of VERTS) pl.fix(pushOut(pts[n], c, 13), n)

  const hitA = bisectorHit(q, 'A', 'B', 'C') as Pt
  const hitD = bisectorHit(q, 'D', 'B', 'C') as Pt
  const MS = view.S(hitA)
  const KS = view.S(hitD)

  // одиночная биссектриса: из угла X, X' — соседняя по боковой стороне вершина, N — соседняя по основанию
  const X: VName = mode === 'D' ? 'D' : 'A'
  const L: VName = X === 'A' ? 'B' : 'C'
  const N: VName = X === 'A' ? 'D' : 'A'
  const hit = X === 'A' ? hitA : hitD
  const HS = X === 'A' ? MS : KS
  const hName = X === 'A' ? 'M' : 'K'
  const bigAngle = angleAt(q[L], q[X], q[N])
  const half = bigAngle / 2
  const rest = a - b
  const measured = dist(q[L], hit)

  const nodes: ReactNode[] = []
  let key = 0
  const add = (n: ReactNode) => nodes.push(<g key={key++}>{n}</g>)

  add(<Shape pts={VERTS.map((n) => pts[n])} edge="" />)

  if (mode !== 'AD') {
    if (step >= 3) add(<polygon points={[pts[X], pts[L], HS].map((p) => p.join(',')).join(' ')} className="pk-fill alt" />)
    if (step >= 2) {
      add(<Chevs p={pts.B} q={pts.C} n={1} />)
      add(<Chevs p={pts.A} q={pts.D} n={1} />)
    }
  }
  add(<Shape pts={VERTS.map((n) => pts[n])} fill="" />)

  if (mode === 'AD') {
    add(<Seg p={pts.A} q={MS} className="pk-bis" />)
    add(<Seg p={pts.D} q={KS} className="pk-s3" />)
    // отрезки BM и CK рядом со стороной BC (чтобы было видно, перекрываются ли они)
    const dy = 6
    const lo = (p: XY, dyy: number): XY => [p[0], p[1] + dyy]
    add(<Seg p={lo(pts.B, dy)} q={lo(MS, dy)} className="pk-s1" />)
    add(<Seg p={lo(pts.C, dy + 5)} q={lo(KS, dy + 5)} className="pk-s3" />)
    add(<Ticks p={pts.A} q={pts.B} n={1} />)
    add(<Ticks p={pts.D} q={pts.C} n={1} />)
  } else {
    add(<Seg p={pts[X]} q={HS} className="pk-bis" />)
    if (step >= 1) {
      add(<Arc o={pts[X]} u={dirTo(pts[X], pts[L])} v={dirTo(pts[X], HS)} r={24} className="pk-arc c1" />)
      add(<Arc o={pts[X]} u={dirTo(pts[X], HS)} v={dirTo(pts[X], pts[N])} r={24} className="pk-arc c1" />)
    }
    if (step >= 2) add(<Arc o={HS} u={dirTo(HS, pts[X])} v={dirTo(HS, pts[L])} r={20} className="pk-arc c1" />)
    if (step >= 3) {
      add(<Ticks p={pts[X]} q={pts[L]} n={1} />)
      add(<Ticks p={pts[L]} q={HS} n={1} />)
    }
  }

  if (mode === 'AD') {
    add(<Dot at={MS} r={3.2} />)
    add(<Dot at={KS} r={3.2} />)
  } else {
    add(<Dot at={HS} r={3.2} />)
  }

  // подписи
  const labels: ReactNode[] = []
  const lab = (at: XY, text: string, cls = 'pk-m') =>
    labels.push(
      <Txt key={labels.length} at={at} className={cls}>
        {text}
      </Txt>,
    )
  const pointLabel = (p: XY, name: string) => {
    const at = pl.place([pushOut(p, c, 13), pushOut(p, c, 20)], name)
    labels.push(
      <Txt key={'p' + name} at={at} className="pk-pt">
        {name}
      </Txt>,
    )
  }
  if (mode === 'AD') {
    pl.dot(MS)
    pl.dot(KS)
    pointLabel(MS, 'M')
    pointLabel(KS, 'K')
    lab(placeSeg(pl, pts.B, MS, c, fmt(b)), fmt(b))
    lab(placeSeg(pl, pts.C, KS, c, fmt(b)), fmt(b))
    lab(placeSeg(pl, pts.A, pts.B, c, fmt(b)), fmt(b))
    lab(placeSeg(pl, pts.D, pts.C, c, fmt(b)), fmt(b))
  } else {
    pl.dot(HS)
    pointLabel(HS, hName)
    if (step >= 1) {
      const u1 = dirTo(pts[X], pts[L])
      const v1 = dirTo(pts[X], HS)
      const v2 = dirTo(pts[X], pts[N])
      lab(placeAngle(pl, pts[X], u1, v1, 24, deg(half)), deg(half), 'pk-m in')
      lab(placeAngle(pl, pts[X], v1, v2, 24, deg(half)), deg(half), 'pk-m in')
    }
    if (step >= 2) lab(placeAngle(pl, HS, dirTo(HS, pts[X]), dirTo(HS, pts[L]), 20, deg(half)), deg(half), 'pk-m in')
    if (step >= 3) {
      lab(placeSeg(pl, pts[X], pts[L], c, fmt(b)), fmt(b))
      lab(placeSeg(pl, pts[L], HS, c, fmt(b)), fmt(b))
      lab(placeSeg(pl, HS, X === 'A' ? pts.C : pts.B, c, fmt(rest)), fmt(rest))
    }
  }

  // подпись для экранных программ
  const aria =
    mode === 'AD'
      ? `Параллелограмм ABCD с биссектрисами углов A и D, BM = AB = ${fmt(b)}, CK = CD = ${fmt(b)}`
      : `Параллелограмм ABCD, AB = ${fmt(b)}, AD = ${fmt(a)}, угол A равен ${deg(ang)}. Биссектриса угла ${X} встречает сторону BC в точке ${hName}`

  const two = b + b
  const mk = Math.abs(a - two)
  const sideNear = X === 'A' ? 'AB' : 'CD'
  const triName = X === 'A' ? 'ABM' : 'DCK'
  const eqSeg = X === 'A' ? 'BM' : 'CK'
  const otherSeg = X === 'A' ? 'MC' : 'KB'
  const angXL = X === 'A' ? 'BAM' : 'CDK'
  const angXN = X === 'A' ? 'MAD' : 'KDA'
  const angH = X === 'A' ? 'AMB' : 'DKC'

  return (
    <div className="viz">
      <div className="viz-title">Биссектриса отрезает равнобедренный треугольник</div>
      <div className="chips">
        {(
          [
            ['A', 'Угол A'],
            ['D', 'Угол D'],
            ['AD', 'Оба угла'],
          ] as [Mode, string][]
        ).map(([m, t]) => (
          <button key={m} className={`chip wide ${mode === m ? 'on' : ''}`} onClick={() => setMode(m)}>
            {t}
          </button>
        ))}
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="pk-svg" role="img" aria-label={aria}>
        {nodes}
        {labels}
        <VertexLabels V={q} view={view} center={c} />
      </svg>
      {mode !== 'AD' && (
        <div className="bv-steps">
          <span className="slider-label">Шаг</span>
          <div className="chips small">
            {STEPS.map((t, i) => (
              <button key={t} className={`chip ${step === i + 1 ? 'on' : ''}`} onClick={() => setStep(i + 1)} aria-label={`Шаг ${i + 1}: ${t}`}>
                {i + 1}
              </button>
            ))}
          </div>
          <button className="btn small primary" onClick={() => setStep(step >= 3 ? 1 : step + 1)}>
            {step >= 3 ? 'Сначала ↺' : 'Дальше ▸'}
          </button>
        </div>
      )}
      <div className="pk-controls">
        <Num label="AB =" aria="сторона AB" value={b} min={2} max={Math.min(6, a - 1)} onChange={(v) => set({ b: v })} format={(n) => fmt(n, 0)} />
        <Num label="AD =" aria="сторона AD" value={a} min={4} max={8} onChange={setA} format={(n) => fmt(n, 0)} />
      </div>
      <div className="pk-slider-row">
        <span className="slider-label">Угол A</span>
        <Stepper compact aria="угол A" value={ang} min={40} max={140} step={5} onChange={(v) => set({ ang: v })} format={deg} />
      </div>
      <input className="slider" type="range" min={40} max={140} step={5} value={ang} onChange={(e) => set({ ang: Number(e.target.value) })} aria-label="Угол A" />
      <div className="readout pk-readout" aria-live="polite">
        {mode === 'AD' ? (
          <>
            <p>
              Биссектриса угла <Tex tex="A" /> даёт <Tex tex={`BM=AB=${tn(b)}`} />, биссектриса угла <Tex tex="D" /> даёт <Tex tex={`CK=CD=${tn(b)}`} />.
            </p>
            <p>
              <Tex tex={`BC=${tn(a)}`} />, а <Tex tex={`BM+CK=${tn(two)}`} />.{' '}
              {two < a ? (
                <>
                  Отрезки не доходят друг до друга: <Tex tex={`MK=${tn(a)}-${tn(two)}=${tn(mk)}`} />.
                </>
              ) : two > a ? (
                <>
                  Отрезки налезают друг на друга: <Tex tex={`MK=${tn(two)}-${tn(a)}=${tn(mk)}`} />.
                </>
              ) : (
                <>Точки M и K совпали: биссектрисы встретились на стороне BC.</>
              )}
            </p>
          </>
        ) : (
          <>
            <p>
              <strong>
                Шаг {step}. {STEPS[step - 1]}.
              </strong>
            </p>
            {step === 1 && (
              <p>
                Биссектриса <Tex tex={`${X}${hName}`} /> делит угол <Tex tex={X} /> = {deg(bigAngle)} пополам: <Tex tex={`\\angle ${angXL}=\\angle ${angXN}=${tn(half)}^\\circ`} />.
              </p>
            )}
            {step === 2 && (
              <p>
                <Tex tex="AD\parallel BC" />, <Tex tex={`${X}${hName}`} /> — секущая, поэтому накрест лежащие углы равны: <Tex tex={`\\angle ${angH}=\\angle ${angXN}=${tn(half)}^\\circ`} />.
              </p>
            )}
            {step === 3 && (
              <>
                <p>
                  В треугольнике <Tex tex={triName} /> два угла равны ({deg(half)} и {deg(half)}), значит, он равнобедренный. Меряем по рисунку: <Tex tex={`${eqSeg}=${tn(measured)}`} /> и{' '}
                  <Tex tex={`${sideNear}=${tn(dist(q[X], q[L]))}`} />. Равны!
                </p>
                <p>
                  Тогда <Tex tex={`${otherSeg}=BC-${eqSeg}=${tn(a)}-${tn(b)}=${tn(rest)}`} />.
                </p>
              </>
            )}
            <p className="muted">
              Меняй стороны и угол: <Tex tex={eqSeg} /> всегда остаётся равным <Tex tex={sideNear} />.
            </p>
          </>
        )}
      </div>
    </div>
  )
}
