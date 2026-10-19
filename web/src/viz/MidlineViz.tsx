import { useState, type ReactNode } from 'react'
import { Tex } from '../components/Tex'
import './MidlineViz.css'
import { Chevs, Dot, Num, Seg, Shape, Txt, VertexLabels } from './parDraw'
import { Placer, VERTS, centroid, fixedView, fmt, intersect, mid, mul, pushOut, sub, tn, trapezoid, type Pt, type VName, type XY } from './parKit'

const W = 320
const H = 156
const HEIGHT = 5
const deg = (n: number) => fmt(n, 0)

/** Средняя линия трапеции: полусумма оснований, достраивание до параллелограмма, диагональ режет линию на половинки оснований. */
export function MidlineViz() {
  const [v, setV] = useState({ a: 10, b: 4 })
  const [doubled, setDoubled] = useState(false)
  const [diag, setDiag] = useState(false)
  const { a, b } = v
  const setA = (x: number) => setV((p) => ({ a: x, b: Math.min(p.b, x - 1) }))
  const m = (a + b) / 2

  const s = (a - b) / 3
  const q = trapezoid(a, b, HEIGHT, s)
  const M = mid(q.A, q.B)
  const N = mid(q.C, q.D)
  // вторая такая же трапеция, повёрнутая на 180° вокруг N: вместе получается параллелограмм
  const rot = (p: Pt): Pt => sub(mul(N, 2), p)
  const ghost = { A: rot(q.A), B: rot(q.B), C: rot(q.C), D: rot(q.D) }
  const M2 = rot(M)
  const O = intersect(M, N, q.A, q.C)?.p as Pt
  const all = doubled ? [...VERTS.map((n) => q[n]), ...VERTS.map((n) => ghost[n])] : VERTS.map((n) => q[n])
  const view = fixedView(all, { w: W, h: H, k: doubled ? 12 : 21, padBottom: doubled ? 44 : 32, padTop: 24 })
  const S = (p: Pt): XY => view.S(p)
  const pts = Object.fromEntries(VERTS.map((n) => [n, S(q[n])])) as Record<VName, XY>
  const c = centroid(VERTS.map((n) => pts[n]))
  const pl = new Placer()
  for (const n of VERTS) pl.fix(pushOut(pts[n], c, 13), n)
  const MS = S(M)
  const NS = S(N)
  pl.dot(MS)
  pl.dot(NS)

  const nodes: ReactNode[] = []
  let key = 0
  const add = (n: ReactNode) => nodes.push(<g key={key++}>{n}</g>)
  if (doubled) {
    const gp = VERTS.map((n) => S(ghost[n]))
    add(<Shape pts={gp} fill="pk-fill ghost" edge="pk-edge ghost" />)
  }
  add(<Shape pts={VERTS.map((n) => pts[n])} edge="" />)
  if (diag) add(<Seg p={pts.A} q={pts.C} className="pk-diag" />)
  add(<Shape pts={VERTS.map((n) => pts[n])} fill="" />)
  add(<Chevs p={pts.A} q={pts.D} n={1} />)
  add(<Chevs p={pts.B} q={pts.C} n={1} />)
  add(<Seg p={MS} q={NS} className="pk-mid" />)
  if (doubled) add(<Seg p={NS} q={S(M2)} className="pk-mid mv-ghost" />)
  add(<Dot at={MS} r={3.2} />)
  add(<Dot at={NS} r={3.2} />)
  if (diag) add(<Dot at={S(O)} r={3.2} />)
  if (doubled) {
    // размер a + b под нижней стороной составной фигуры
    const y = view.Y(q.A) + 24
    const x1 = view.X(q.A)
    const x2 = view.X(ghost.B)
    add(
      <>
        <line x1={x1} y1={y} x2={x2} y2={y} className="mv-dim" />
        <line x1={x1} y1={y - 4} x2={x1} y2={y + 4} className="mv-dim" />
        <line x1={x2} y1={y - 4} x2={x2} y2={y + 4} className="mv-dim" />
      </>,
    )
  }

  const labels: ReactNode[] = []
  const lab = (at: XY, text: string, cls = 'pk-m', k = text) =>
    labels.push(
      <Txt key={k + labels.length} at={at} className={cls}>
        {text}
      </Txt>,
    )
  // подписи оснований
  const baseLabelBottom = pl.place([[(pts.A[0] + pts.D[0]) / 2, pts.A[1] + 13]], fmt(a))
  lab(baseLabelBottom, fmt(a), 'pk-m', 'a')
  lab(pl.place([[(pts.B[0] + pts.C[0]) / 2, pts.B[1] - 12]], fmt(b)), fmt(b), 'pk-m', 'b')
  // средняя линия
  const mx = (MS[0] + NS[0]) / 2
  if (diag) {
    const OS = S(O)
    lab(pl.place([[(MS[0] + OS[0]) / 2, MS[1] - 12]], fmt(b / 2)), fmt(b / 2), 'pk-m in', 'mp')
    lab(pl.place([[(OS[0] + NS[0]) / 2, MS[1] - 12]], fmt(a / 2)), fmt(a / 2), 'pk-m in', 'pn')
    labels.push(
      <Txt key="P" at={pl.place([[OS[0] + 11, OS[1] + 12], [OS[0], OS[1] + 14]], 'P')} className="pk-pt in">
        P
      </Txt>,
    )
  } else {
    lab(pl.place([[mx, MS[1] - 12], [mx, MS[1] + 13]], `m=${fmt(m)}`), `m=${fmt(m)}`, 'pk-m in', 'm')
  }
  for (const [name, at] of [['M', MS], ['N', NS]] as [string, XY][]) {
    const where = pl.place([pushOut(at, c, 13), pushOut(at, c, 20)], name)
    labels.push(
      <Txt key={name} at={where} className="pk-pt">
        {name}
      </Txt>,
    )
  }
  if (doubled) {
    const y = view.Y(q.A) + 24
    lab([(view.X(q.A) + view.X(ghost.B)) / 2, y + 14], `a + b = ${fmt(a + b)}`, 'pk-m flat', 'sum')
  }

  return (
    <div className="viz">
      <div className="viz-title">Средняя линия: ровно посередине между основаниями</div>
      <div className="chips">
        <button className={`chip wide ${doubled ? 'on' : ''}`} aria-pressed={doubled} onClick={() => setDoubled(!doubled)}>
          {doubled ? 'Убрать вторую' : 'Достроить'}
        </button>
        <button className={`chip wide ${diag ? 'on' : ''}`} aria-pressed={diag} onClick={() => setDiag(!diag)}>
          Диагональ AC
        </button>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="pk-svg" role="img" aria-label={`Трапеция ABCD с основаниями AD = ${fmt(a)} и BC = ${fmt(b)}. Средняя линия MN = ${fmt(m)}${doubled ? `. Достроена вторая такая же трапеция: получился параллелограмм с основанием ${fmt(a + b)}` : ''}${diag ? `. Диагональ AC делит среднюю линию на ${fmt(b / 2)} и ${fmt(a / 2)}` : ''}`}>
        {nodes}
        {labels}
        <VertexLabels V={q} view={view} center={c} />
      </svg>
      <div className="pk-controls">
        <Num label="AD =" aria="основание AD" value={a} min={4} max={10} onChange={setA} format={deg} />
        <Num label="BC =" aria="основание BC" value={b} min={2} max={a - 1} onChange={(x) => setV((p) => ({ ...p, b: x }))} format={deg} />
      </div>
      <div className="readout pk-readout" aria-live="polite">
        <p>
          Основания <Tex tex={`a=${tn(a)}`} /> и <Tex tex={`b=${tn(b)}`} />. Средняя линия: <Tex tex={`m=\\dfrac{${tn(a)}+${tn(b)}}{2}=${tn(m)}`} />.
        </p>
        <p>
          Она длиннее меньшего основания на <Tex tex={`${tn(m - b)}`} /> и короче большего на <Tex tex={`${tn(a - m)}`} />: ровно посередине.
        </p>
        {doubled && (
          <p>
            Достроили такую же трапецию: получился параллелограмм с основанием <Tex tex={`a+b=${tn(a + b)}`} />. Средняя линия — его половина: <Tex tex={`${tn(a + b)}:2=${tn(m)}`} />.
          </p>
        )}
        {diag && (
          <p>
            Диагональ режет среднюю линию на куски <Tex tex={`\\dfrac{b}{2}=${tn(b / 2)}`} /> и <Tex tex={`\\dfrac{a}{2}=${tn(a / 2)}`} />. Вместе: <Tex tex={`${tn(b / 2)}+${tn(a / 2)}=${tn(m)}`} />.
          </p>
        )}
      </div>
    </div>
  )
}

