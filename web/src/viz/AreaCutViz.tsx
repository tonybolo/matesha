import { useState, type ReactNode } from 'react'
import { Tex } from '../components/Tex'
import './AreaCutViz.css'
import { Chevs, Num, RightMark, Seg, Shape, Txt, VertexLabels } from './parDraw'
import { P, Placer, VERTS, centroid, dist, fixedView, fmt, mid, mul, pushOut, sub, tn, trapezoid, type Pt, type Quad, type VName, type XY } from './parKit'
import { Stepper } from './Stepper'

const W = 320
const num = (n: number) => fmt(n, 0)

/** Площадь: параллелограмм перекраивается в прямоугольник, две трапеции складываются в параллелограмм (режим задаёт preset). */
export function AreaCutViz({ preset }: { preset?: string }) {
  return preset === 'trapezoid' ? <TrapPanel /> : <ParPanel />
}

// ---------------------------------------------------------------------------
// Параллелограмм → прямоугольник
// ---------------------------------------------------------------------------

function ParPanel() {
  const [v, setV] = useState({ a: 6, h: 4, s: 2 })
  const [moved, setMoved] = useState(false)
  const { a, h, s } = v
  const set = (patch: Partial<typeof v>) =>
    setV((p) => {
      const n = { ...p, ...patch }
      n.s = Math.min(n.s, n.a)
      return n
    })
  const H = 150
  const q: Quad = { A: P(0, 0), B: P(s, h), C: P(s + a, h), D: P(a, 0) }
  const foot = P(s, 0)
  const view = fixedView([...VERTS.map((n) => q[n]), foot], { w: W, h: H, k: 16, padBottom: 34, padTop: 22 })
  const k = view.k
  const pts = Object.fromEntries(VERTS.map((n) => [n, view.S(q[n])])) as Record<VName, XY>
  const HS = view.S(foot)
  const c = centroid(VERTS.map((n) => pts[n]))
  const AB = dist(q.A, q.B)
  const area = a * h

  // клетки единичного размера на прямоугольнике
  const cells: ReactNode[] = []
  for (let i = 0; i <= a; i++) cells.push(<line key={'v' + i} x1={HS[0] + i * k} y1={HS[1]} x2={HS[0] + i * k} y2={HS[1] - h * k} className="ac-grid" />)
  for (let j = 0; j <= h; j++) cells.push(<line key={'h' + j} x1={HS[0]} y1={HS[1] - j * k} x2={HS[0] + a * k} y2={HS[1] - j * k} className="ac-grid" />)

  const pl = new Placer()
  for (const n of VERTS) pl.fix(pushOut(pts[n], c, 13), n)
  const lab: ReactNode[] = []
  const put = (p: XY, qq: XY, text: string, key: string) => {
    const mx = (p[0] + qq[0]) / 2
    const my = (p[1] + qq[1]) / 2
    const at = pl.place([[mx, my + 13], [mx, my - 12]], text)
    lab.push(
      <Txt key={key} at={at} className="pk-m">
        {text}
      </Txt>,
    )
  }
  put(pts.A, pts.D, `a=${num(a)}`, 'a')
  if (s > 0) {
    const at: XY = [HS[0] - 12, (HS[1] + pts.B[1]) / 2]
    lab.push(
      <Txt key="h" at={at} className="pk-m">
        {`h=${num(h)}`}
      </Txt>,
    )
  } else {
    lab.push(
      <Txt key="h" at={[pts.A[0] - 14, (pts.A[1] + pts.B[1]) / 2]} className="pk-m">
        {`h=${num(h)}`}
      </Txt>,
    )
  }

  return (
    <div className="viz">
      <div className="viz-title">Перекраиваем параллелограмм в прямоугольник</div>
      <div className="chips">
        <button className={`btn small ${moved ? '' : 'primary'}`} onClick={() => setMoved(!moved)}>
          {moved ? 'Вернуть' : 'Перекроить'}
        </button>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="pk-svg" role="img" aria-label={`Параллелограмм ABCD с основанием AD = ${num(a)} и высотой BH = ${num(h)}. ${moved ? `Треугольник ABH перенесён вправо, получился прямоугольник ${num(a)} на ${num(h)}, площадь ${num(area)}` : 'Левый треугольник ABH можно отрезать и приставить справа'}`}>
        {/* что останется на месте: трапеция HDCB */}
        <Shape pts={[HS, pts.D, pts.C, pts.B]} />
        {/* контур исходного параллелограмма (виден, когда треугольник уехал) */}
        <polygon points={VERTS.map((n) => pts[n].join(',')).join(' ')} className="ac-orig" style={{ opacity: moved ? 1 : 0 }} />
        {/* левый треугольник ABH: уезжает вправо на a */}
        <g className="ac-move" style={{ transform: `translateX(${moved ? a * k : 0}px)` }}>
          {s > 0 && <polygon points={[pts.A, HS, pts.B].map((p) => p.join(',')).join(' ')} className="pk-fill alt" />}
          {s > 0 && <polygon points={[pts.A, HS, pts.B].map((p) => p.join(',')).join(' ')} className="pk-edge" />}
        </g>
        <g style={{ opacity: moved ? 1 : 0 }} className="ac-fade">
          {cells}
        </g>
        <Seg p={pts.B} q={HS} className="pk-height" />
        {s > 0 && <RightMark o={HS} u={[0, -1]} v={[1, 0]} s={8} />}
        <Shape pts={[HS, pts.D, pts.C, pts.B]} fill="" />
        <Chevs p={pts.B} q={pts.C} n={1} />
        <Chevs p={pts.A} q={pts.D} n={1} />
        {lab}
        <VertexLabels V={q} view={view} center={c} />
      </svg>
      <div className="pk-controls">
        <Num label="a =" aria="основание a" value={a} min={3} max={8} onChange={(x) => set({ a: x })} format={num} />
        <Num label="h =" aria="высота h" value={h} min={2} max={5} onChange={(x) => set({ h: x })} format={num} />
      </div>
      <div className="pk-slider-row">
        <span className="slider-label">Наклон</span>
        <Stepper compact aria="наклон" value={s} min={0} max={a} step={1} onChange={(x) => set({ s: x })} format={num} />
      </div>
      <input className="slider" type="range" min={0} max={a} step={1} value={s} onChange={(e) => set({ s: Number(e.target.value) })} aria-label="Наклон" />
      <div className="readout pk-readout" aria-live="polite">
        {!moved ? (
          <>
            <p>
              Основание <Tex tex={`a=${tn(a)}`} />, высота <Tex tex={`h=${tn(h)}`} /> (<Tex tex="BH\perp AD" />). Боковая сторона <Tex tex={`AB=${tn(AB)}`} /> — не высота, в формулу она не идёт.
            </p>
            <p className="muted">{s === 0 ? 'Наклона нет: это уже прямоугольник, резать нечего.' : 'Нажми «Перекроить»: левый треугольник переедет вправо.'}</p>
          </>
        ) : (
          <>
            <p>
              Получился прямоугольник <Tex tex={`${tn(a)}\\times ${tn(h)}`} />: в нём <Tex tex={`${tn(a)}\\cdot ${tn(h)}=${tn(area)}`} /> клеток.
            </p>
            <p>
              Значит, <Tex tex={`S=a\\cdot h=${tn(a)}\\cdot ${tn(h)}=${tn(area)}`} />.
            </p>
            <p className="muted">Меняй наклон: боковая сторона другая, а высота и площадь те же.</p>
          </>
        )}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Две трапеции → параллелограмм
// ---------------------------------------------------------------------------

function TrapPanel() {
  const [v, setV] = useState({ a: 8, b: 4, h: 3 })
  const [doubled, setDoubled] = useState(false)
  const { a, b, h } = v
  const set = (patch: Partial<typeof v>) =>
    setV((p) => {
      const n = { ...p, ...patch }
      n.b = Math.min(n.b, n.a - 1)
      return n
    })
  const H = 150
  const s = (a - b) / 2
  const q = trapezoid(a, b, h, s)
  const N = mid(q.C, q.D)
  const rot = (p: Pt): Pt => sub(mul(N, 2), p)
  const ghost: Quad = { A: rot(q.A), B: rot(q.B), C: rot(q.C), D: rot(q.D) }
  const all = [...VERTS.map((n) => q[n]), ...VERTS.map((n) => ghost[n])]
  const view = fixedView(doubled ? all : VERTS.map((n) => q[n]), { w: W, h: H, k: doubled ? 13 : 21, padBottom: doubled ? 46 : 34, padTop: 22 })
  const pts = Object.fromEntries(VERTS.map((n) => [n, view.S(q[n])])) as Record<VName, XY>
  const gp = VERTS.map((n) => view.S(ghost[n]))
  const c = centroid(VERTS.map((n) => pts[n]))
  const HF = view.S(P(s, 0))
  const m = (a + b) / 2
  const S1 = m * h

  const pl = new Placer()
  for (const n of VERTS) pl.fix(pushOut(pts[n], c, 13), n)
  const lab: ReactNode[] = []
  const put = (at: XY, text: string, key: string, cls = 'pk-m') =>
    lab.push(
      <Txt key={key} at={at} className={cls}>
        {text}
      </Txt>,
    )
  put(pl.place([[(pts.A[0] + pts.D[0]) / 2, pts.A[1] + 13]], `a=${num(a)}`), `a=${num(a)}`, 'a')
  put(pl.place([[(pts.B[0] + pts.C[0]) / 2, pts.B[1] - 12]], `b=${num(b)}`), `b=${num(b)}`, 'b')
  put(pl.place([[HF[0] - 13, (HF[1] + pts.B[1]) / 2]], `h=${num(h)}`), `h=${num(h)}`, 'h', 'pk-m in')
  const dimY = pts.A[1] + 26
  const x2 = view.X(ghost.B)

  return (
    <div className="viz">
      <div className="viz-title">Две трапеции складываются в параллелограмм</div>
      <div className="chips">
        <button className={`btn small ${doubled ? '' : 'primary'}`} onClick={() => setDoubled(!doubled)}>
          {doubled ? 'Убрать вторую' : 'Достроить'}
        </button>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="pk-svg" role="img" aria-label={`Трапеция ABCD с основаниями AD = ${num(a)} и BC = ${num(b)} и высотой ${num(h)}. ${doubled ? `Достроена такая же трапеция: получился параллелограмм с основанием ${num(a + b)} и высотой ${num(h)}, площадь ${num((a + b) * h)}` : 'Площадь трапеции — половина такого параллелограмма'}`}>
        <g className="ac-fade" style={{ opacity: doubled ? 1 : 0 }}>
          <Shape pts={gp} fill="pk-fill ghost" edge="pk-edge ghost" />
          <line x1={view.X(q.A)} y1={dimY} x2={x2} y2={dimY} className="ac-dim" />
          <line x1={view.X(q.A)} y1={dimY - 4} x2={view.X(q.A)} y2={dimY + 4} className="ac-dim" />
          <line x1={x2} y1={dimY - 4} x2={x2} y2={dimY + 4} className="ac-dim" />
          <Txt at={[(view.X(q.A) + x2) / 2, dimY + 13]} className="pk-m flat">{`a + b = ${num(a + b)}`}</Txt>
        </g>
        <Shape pts={VERTS.map((n) => pts[n])} />
        <Seg p={pts.B} q={HF} className="pk-height" />
        <RightMark o={HF} u={[0, -1]} v={[1, 0]} s={8} />
        <Chevs p={pts.B} q={pts.C} n={1} />
        <Chevs p={pts.A} q={pts.D} n={1} />
        {lab}
        <VertexLabels V={q} view={view} center={c} />
      </svg>
      <div className="pk-controls">
        <Num label="a =" aria="основание a" value={a} min={4} max={10} onChange={(x) => set({ a: x })} format={num} />
        <Num label="b =" aria="основание b" value={b} min={2} max={a - 1} onChange={(x) => set({ b: x })} format={num} />
        <Num label="h =" aria="высота h" value={h} min={2} max={5} onChange={(x) => set({ h: x })} format={num} />
      </div>
      <div className="readout pk-readout" aria-live="polite">
        {!doubled ? (
          <>
            <p>
              Основания <Tex tex={`a=${tn(a)}`} /> и <Tex tex={`b=${tn(b)}`} />, высота <Tex tex={`h=${tn(h)}`} />. Средняя линия <Tex tex={`m=${tn(m)}`} />.
            </p>
            <p className="muted">Нажми «Достроить»: приставим к трапеции такую же, но перевёрнутую.</p>
          </>
        ) : (
          <>
            <p>
              Две трапеции — параллелограмм с основанием <Tex tex={`a+b=${tn(a + b)}`} /> и высотой <Tex tex={`h=${tn(h)}`} />. Его площадь <Tex tex={`${tn(a + b)}\\cdot ${tn(h)}=${tn((a + b) * h)}`} />.
            </p>
            <p>
              Одна трапеция — половина: <Tex tex={`S=\\dfrac{a+b}{2}\\cdot h=${tn((a + b) * h)}:2=${tn(S1)}`} />.
            </p>
          </>
        )}
      </div>
    </div>
  )
}
