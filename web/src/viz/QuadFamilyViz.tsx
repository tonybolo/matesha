import { useState, type ReactNode } from 'react'
import { Tex } from '../components/Tex'
import { QuadFig } from './fig/QuadFig'
import { Stepper } from './Stepper'
import './QuadFamilyViz.css'

type Pt = [number, number]
type Kind = 'quad' | 'trap' | 'iso' | 'rtrap' | 'par' | 'rect' | 'rhomb' | 'square'
type TreeKind = 'quad' | 'trap' | 'par' | 'rect' | 'rhomb' | 'square'

/** Название фигуры (именительный падеж), род. */
const NAME: Record<Kind, string> = {
  quad: 'четырёхугольник',
  trap: 'трапеция',
  iso: 'равнобедренная трапеция',
  rtrap: 'прямоугольная трапеция',
  par: 'параллелограмм',
  rect: 'прямоугольник',
  rhomb: 'ромб',
  square: 'квадрат',
}
const FEM: Kind[] = ['trap', 'iso', 'rtrap']

// ---------------------------------------------------------------------------------------------
// Определение вида фигуры по координатам вершин (векторы и допуск на ошибки округления)
// ---------------------------------------------------------------------------------------------

/** Самое точное название четырёхугольника по координатам вершин. */
function classify(P: Pt[]): Kind {
  const s: Pt[] = P.map((p, i) => {
    const q = P[(i + 1) % 4]
    return [q[0] - p[0], q[1] - p[1]]
  })
  const len = (a: Pt) => Math.hypot(a[0], a[1])
  const parallel = (a: Pt, b: Pt) => Math.abs(a[0] * b[1] - a[1] * b[0]) < 1e-9 * len(a) * len(b)
  const perp = (a: Pt, b: Pt) => Math.abs(a[0] * b[0] + a[1] * b[1]) < 1e-9 * len(a) * len(b)
  const same = (a: number, b: number) => Math.abs(a - b) < 1e-9 * Math.max(a, b)
  const p02 = parallel(s[0], s[2])
  const p13 = parallel(s[1], s[3])
  const right = [0, 1, 2, 3].some((i) => perp(s[i], s[(i + 1) % 4]))
  if (p02 && p13) {
    const eq = same(len(s[0]), len(s[1]))
    return right ? (eq ? 'square' : 'rect') : eq ? 'rhomb' : 'par'
  }
  if (p02 || p13) {
    const legs = p02 ? [1, 3] : [0, 2]
    if (same(len(s[legs[0]]), len(s[legs[1]]))) return 'iso'
    return right ? 'rtrap' : 'trap'
  }
  return 'quad'
}

const angleAt = (P: Pt[], i: number) => {
  const v = P[i]
  const a = P[(i + 3) % 4]
  const b = P[(i + 1) % 4]
  const ux = a[0] - v[0]
  const uy = a[1] - v[1]
  const wx = b[0] - v[0]
  const wy = b[1] - v[1]
  return (Math.acos(Math.max(-1, Math.min(1, (ux * wx + uy * wy) / (Math.hypot(ux, uy) * Math.hypot(wx, wy))))) * 180) / Math.PI
}

const r1 = (x: number) => String(Math.round(x * 10) / 10).replace('.', '{,}')

// ---------------------------------------------------------------------------------------------
// 1. «Угадай фигуру» + семейное дерево
// ---------------------------------------------------------------------------------------------

type Toggles = { t: boolean; p: boolean; e: boolean; r: boolean }

const PARENTS: Record<TreeKind, TreeKind[]> = { quad: [], trap: ['quad'], par: ['quad'], rect: ['par'], rhomb: ['par'], square: ['rect', 'rhomb'] }
const KIDS: Record<TreeKind, TreeKind[]> = { quad: ['trap', 'par'], trap: [], par: ['rect', 'rhomb'], rect: ['square'], rhomb: ['square'], square: [] }
const DEFN: Record<TreeKind, string> = {
  quad: 'фигура из четырёх вершин и четырёх сторон: никакие три вершины не лежат на одной прямой, стороны не пересекаются',
  trap: 'четырёхугольник, у которого две стороны параллельны, а две другие не параллельны',
  par: 'четырёхугольник, у которого противоположные стороны попарно параллельны',
  rect: 'параллелограмм, у которого все углы прямые',
  rhomb: 'параллелограмм, у которого все стороны равны',
  square: 'прямоугольник, у которого все стороны равны',
}
/** Какие переключатели соответствуют фигуре. */
const TOGGLES_OF: Record<TreeKind, Toggles> = {
  quad: { t: false, p: false, e: false, r: false },
  trap: { t: true, p: false, e: false, r: false },
  par: { t: false, p: true, e: false, r: false },
  rect: { t: false, p: true, e: false, r: true },
  rhomb: { t: false, p: true, e: true, r: false },
  square: { t: false, p: true, e: true, r: true },
}

/** Координаты фигуры для рисунка (y вверх). */
const SHAPE: Record<TreeKind, Pt[]> = {
  quad: [[0, 0], [7, 0.5], [5.5, 6], [1.5, 4]],
  trap: [[0, 0], [1, 4], [5, 4], [9, 0]],
  par: [[0, 0], [6, 0], [8, 4], [2, 4]],
  rect: [[0, 0], [8, 0], [8, 4.5], [0, 4.5]],
  rhomb: [[0, 2], [4, 0], [8, 2], [4, 4]],
  square: [[0, 0], [5, 0], [5, 5], [0, 5]],
}

const ancestors = (k: TreeKind): TreeKind[] => {
  const out: TreeKind[] = []
  const walk = (x: TreeKind) => {
    for (const p of PARENTS[x]) {
      if (!out.includes(p)) out.push(p)
      walk(p)
    }
  }
  walk(k)
  return out
}

/** Что получилось из переключателей: фигура либо null («так не бывает»). Противоречие: у трапеции параллельна ровно одна пара сторон, а всё остальное делает параллельными обе. */
function figureOf(g: Toggles): TreeKind | null {
  const par = g.p || g.e || g.r // равные стороны или прямые углы сами делают противоположные стороны параллельными
  if (g.t && par) return null
  if (g.t) return 'trap'
  if (!par) return 'quad'
  if (g.e && g.r) return 'square'
  if (g.r) return 'rect'
  if (g.e) return 'rhomb'
  return 'par'
}

const NODES: Record<TreeKind, { x: number; row: number; w: number }> = {
  quad: { x: 44, row: 0, w: 38 },
  trap: { x: 20, row: 1, w: 27 },
  par: { x: 68, row: 1, w: 34 },
  rect: { x: 50, row: 2, w: 32 },
  rhomb: { x: 86, row: 2, w: 26 },
  square: { x: 68, row: 3, w: 27 },
}
const EDGES: [TreeKind, TreeKind][] = [
  ['quad', 'trap'],
  ['quad', 'par'],
  ['par', 'rect'],
  ['par', 'rhomb'],
  ['rect', 'square'],
  ['rhomb', 'square'],
]
const NODE_H = 70
const ROW = 86
const TREE_H = 3 * ROW + NODE_H

function Mini({ kind }: { kind: TreeKind }) {
  const P = SHAPE[kind]
  const xs = P.map((p) => p[0])
  const ys = P.map((p) => p[1])
  const x0 = Math.min(...xs)
  const y0 = Math.min(...ys)
  const s = Math.min(40 / (Math.max(...xs) - x0), 26 / (Math.max(...ys) - y0))
  const pts = P.map((p) => `${(2 + (p[0] - x0) * s).toFixed(1)},${(28 - (p[1] - y0) * s).toFixed(1)}`).join(' ')
  return (
    <svg viewBox="0 0 44 30" width={44} height={30} aria-hidden>
      <polygon points={pts} className="qf-mini" />
    </svg>
  )
}

function describe(g: Toggles): ReactNode {
  const fig = figureOf(g)
  const forced = (g.e || g.r) && !g.p
  const note = forced ? (
    <div className="muted">
      Заметь: «обе пары параллельны» включилось само — у четырёхугольника с равными сторонами (или с прямыми углами) противоположные стороны всегда параллельны.
    </div>
  ) : null
  if (fig === null) {
    return (
      <>
        <div>
          <strong>Так фигуры не бывает.</strong> У трапеции параллельна <strong>только одна</strong> пара сторон, а{' '}
          {g.p ? 'вторая пара тоже параллельна' : 'равные стороны (или прямые углы) делают параллельными обе пары'} — получился бы параллелограмм.
        </div>
        <div className="muted">Выключи одно из двух свойств.</div>
      </>
    )
  }
  const lead: Record<TreeKind, string> = {
    quad: 'Пока про фигуру известно только то, что у неё четыре угла. Включи свойства — и имя станет точнее.',
    trap: 'Параллельна только одна пара сторон.',
    par: 'Обе пары противоположных сторон параллельны.',
    rect: 'Параллелограмм, у которого все углы прямые.',
    rhomb: 'Параллелограмм, у которого все стороны равны.',
    square: 'Все углы прямые и все стороны равны: и прямоугольник, и ромб сразу.',
  }
  return (
    <>
      <div>
        {lead[fig]} Это <strong>{fig === 'quad' ? 'просто четырёхугольник' : NAME[fig]}</strong>.
      </div>
      {note}
    </>
  )
}

function Detail({ kind }: { kind: TreeKind }) {
  const parents = PARENTS[kind]
  const anc = ancestors(kind)
  const kids = KIDS[kind]
  const fem = FEM.includes(kind)
  const word = fem ? 'всякая' : 'всякий'
  return (
    <>
      <div>
        <strong>{NAME[kind][0].toUpperCase() + NAME[kind].slice(1)}</strong> — {DEFN[kind]}.
      </div>
      <div>
        {parents.length === 0
          ? 'Родителей нет: это самая «общая» фигура семьи.'
          : `${parents.length > 1 ? 'Родители' : 'Родитель'}: ${parents.map((p) => NAME[p]).join(' и ')}.`}
        {anc.length > 0 && ` Значит, ${word} ${NAME[kind]} — это ${anc.map((p) => NAME[p]).join(', ')}.`}
      </div>
      {kids.length > 0 && (
        <div className="muted">
          Дети: {kids.map((k) => NAME[k]).join(' и ')}. Наоборот не всегда: не каждый {NAME[kind]} — {NAME[kids[0]]}.
        </div>
      )}
      {kind === 'trap' && <div className="muted">Бывают особые трапеции: равнобедренная (равны боковые стороны) и прямоугольная (есть прямой угол).</div>}
    </>
  )
}

const PRESET_TOGGLES = (preset?: string): Toggles => (preset && preset in TOGGLES_OF ? TOGGLES_OF[preset as TreeKind] : TOGGLES_OF.quad)

/** Игра «Угадай фигуру»: включай свойства и смотри, как называется фигура; внизу семейное дерево, на фигуры можно нажимать. */
export function QuadFamilyViz({ preset }: { preset?: string }) {
  const [g, setG] = useState<Toggles>(() => PRESET_TOGGLES(preset))
  const fig = figureOf(g)
  const forced = g.e || g.r
  const anc = fig ? ancestors(fig) : []
  const flip = (k: keyof Toggles) => setG((cur) => ({ ...cur, [k]: !cur[k] }))

  const marks: Record<string, number[]> = {}
  if (fig === 'trap') marks.par1 = [1, 3]
  if (fig === 'par' || fig === 'rect' || fig === 'rhomb' || fig === 'square') {
    marks.par1 = [0, 2]
    marks.par2 = [1, 3]
  }
  if (fig === 'rhomb' || fig === 'square') marks.eq1 = [0, 1, 2, 3]
  if (fig === 'rect' || fig === 'square') marks.rt = [0, 1, 2, 3]
  const flat = fig ? SHAPE[fig].flatMap((p) => p) : []

  const toggles: { k: keyof Toggles; label: string }[] = [
    { k: 't', label: 'параллельна только одна пара сторон' },
    { k: 'p', label: 'обе пары противоположных сторон параллельны' },
    { k: 'e', label: 'все стороны равны' },
    { k: 'r', label: 'все углы прямые' },
  ]
  const edgeOn = (a: TreeKind, b: TreeKind) => fig !== null && (fig === b || anc.includes(b)) && (fig === a || anc.includes(a))

  return (
    <div className="viz qf">
      <div className="viz-title">Угадай фигуру</div>

      <div className="viz-step">
        <span className="viz-num">1</span> Включай свойства
      </div>
      <div className="qf-toggles">
        {toggles.map(({ k, label }) => {
          const auto = k === 'p' && forced && !g.p
          const on = k === 'p' ? g.p || forced : g[k]
          return (
            <button key={k} className={`chip wide qf-toggle ${on ? 'on' : ''} ${auto ? 'auto' : ''}`} aria-pressed={on} onClick={() => flip(k)} disabled={k === 'p' && forced}>
              <span className="qf-check" aria-hidden>
                {on ? '☑' : '☐'}
              </span>
              <span>{label}</span>
            </button>
          )
        })}
      </div>

      <div className="qf-fig">
        {fig ? (
          <QuadFig pts={flat} {...marks} view={[-1, -1, 10, 7]} />
        ) : (
          <div className="qf-none" role="img" aria-label="Такой фигуры нет">
            <span aria-hidden>🚫</span>
            <span>такой фигуры нет</span>
          </div>
        )}
      </div>
      <div className={`readout ${fig ? '' : 'bad'}`} aria-live="polite">
        {describe(g)}
      </div>

      <div className="viz-step">
        <span className="viz-num">2</span> Семейное дерево: нажми на фигуру
      </div>
      <div className="qf-tree" style={{ height: TREE_H }}>
        <svg className="qf-edges" viewBox={`0 0 100 ${TREE_H}`} preserveAspectRatio="none" aria-hidden>
          {EDGES.map(([a, b]) => (
            <line
              key={a + b}
              className={`qf-edge ${edgeOn(a, b) ? 'on' : ''}`}
              x1={NODES[a].x}
              y1={NODES[a].row * ROW + NODE_H}
              x2={NODES[b].x}
              y2={NODES[b].row * ROW}
              vectorEffect="non-scaling-stroke"
            />
          ))}
        </svg>
        {(Object.keys(NODES) as TreeKind[]).map((k) => {
          const n = NODES[k]
          const cls = fig === k ? 'on' : anc.includes(k) ? 'anc' : ''
          return (
            <button
              key={k}
              className={`qf-node ${cls}`}
              style={{ left: `${n.x}%`, top: n.row * ROW, width: `${n.w}%`, height: NODE_H }}
              aria-pressed={fig === k}
              onClick={() => setG(TOGGLES_OF[k])}
            >
              <Mini kind={k} />
              <span className="qf-label">{NAME[k]}</span>
            </button>
          )
        })}
      </div>
      <div className="readout" aria-live="polite">
        {fig ? <Detail kind={fig} /> : <div>Выбери фигуру в дереве или включи подходящие свойства: тогда здесь появится её определение и родители.</div>}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------------------------
// 2. Лаборатория параллелограмма: угол и сторона меняют имя фигуры
// ---------------------------------------------------------------------------------------------

const AB = 5

function parPts(ang: number, b: number): Pt[] {
  const t = (ang * Math.PI) / 180
  const D: Pt = [b * Math.cos(t), b * Math.sin(t)]
  return [[0, 0], [AB, 0], [AB + D[0], D[1]], D]
}

const LAB_CHIPS: { kind: Kind; ang: number; b: number }[] = [
  { kind: 'par', ang: 70, b: 3 },
  { kind: 'rect', ang: 90, b: 3 },
  { kind: 'rhomb', ang: 70, b: 5 },
  { kind: 'square', ang: 90, b: 5 },
]
const START: Record<string, [number, number]> = { par: [70, 3], rect: [90, 3], rhomb: [70, 5], square: [90, 5] }

/** Параллелограмм ABCD: меняем угол A и сторону AD. Имя фигуры считается по координатам вершин. */
export function ParLabViz({ preset }: { preset?: string }) {
  const [[ang, b], setAB] = useState<[number, number]>(() => START[preset ?? 'par'] ?? START.par)
  const P = parPts(ang, b)
  const kind = classify(P)
  const right = kind === 'rect' || kind === 'square'
  const equal = kind === 'rhomb' || kind === 'square'
  const a1 = ang
  const a2 = 180 - ang
  const why: Record<string, string> = {
    par: 'Обе пары противоположных сторон параллельны, а углы не прямые и соседние стороны разные.',
    rect: 'Параллелограмм, у которого все углы прямые, а соседние стороны разные.',
    rhomb: 'Параллелограмм, у которого все стороны равны, а углы не прямые.',
    square: 'Все углы прямые и все стороны равны: это одновременно прямоугольник и ромб.',
  }
  return (
    <div className="viz qf">
      <div className="viz-title">Лаборатория параллелограмма</div>
      <div className="viz-step">
        <span className="viz-num">1</span> Меняй угол и сторону
      </div>
      <div className="steppers">
        <Stepper compact label="угол A" value={ang} min={50} max={130} step={10} onChange={(v) => setAB([v, b])} format={(v) => `${v}°`} />
        <Stepper compact label="сторона AD" value={b} min={2} max={7} step={1} onChange={(v) => setAB([ang, v])} format={(v) => String(v)} />
      </div>
      <div className="chips">
        {LAB_CHIPS.map((c) => (
          <button key={c.kind} className={`chip wide ${kind === c.kind ? 'on' : ''}`} onClick={() => setAB([c.ang, c.b])}>
            {NAME[c.kind]}
          </button>
        ))}
      </div>
      <div className="qf-fig">
        <QuadFig
          pts={P.flatMap((p) => p)}
          par1={[0, 2]}
          par2={[1, 3]}
          eq1={equal ? [0, 1, 2, 3] : [0, 2]}
          eq2={equal ? [] : [1, 3]}
          rt={right ? [0, 1, 2, 3] : []}
          angs={[`${a1}°`, `${a2}°`, `${a1}°`, `${a2}°`]}
          view={[-5, -1, 10, 8]}
        />
      </div>
      <div className="readout" aria-live="polite">
        <div>
          Сейчас это <strong>{NAME[kind]}</strong>. {why[kind]}
        </div>
        <div className="viz-calc">
          <Tex tex={`AB\\parallel DC,\\ BC\\parallel AD`} />
        </div>
        <div className="viz-calc">
          <Tex tex={equal ? `AB=BC=CD=DA=${AB}` : `AB=DC=${AB},\\ BC=AD=${b}`} />
        </div>
        <div className="viz-calc">
          <Tex tex={`\\angle A=\\angle C=${a1}^\\circ,\\ \\angle B=\\angle D=${a2}^\\circ`} />
        </div>
        <div className="muted">
          Соседние углы вместе дают <Tex tex={`${a1}^\\circ+${a2}^\\circ=180^\\circ`} />, противоположные равны.
        </div>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------------------------
// 3. Лаборатория трапеции: верхнее основание и сдвиг; когда боковые стороны тоже параллельны, трапеция «превращается» в параллелограмм
// ---------------------------------------------------------------------------------------------

const BASE = 8
const HGT = 5

function trapPts(top: number, shift: number): Pt[] {
  return [[0, 0], [shift, HGT], [shift + top, HGT], [BASE, 0]]
}

const TRAP_CHIPS: { label: string; kinds: Kind[]; top: number; shift: number }[] = [
  { label: 'обычная', kinds: ['trap'], top: 4, shift: 1 },
  { label: 'равнобедренная', kinds: ['iso'], top: 4, shift: 2 },
  { label: 'прямоугольная', kinds: ['rtrap'], top: 4, shift: 0 },
  { label: 'основания равны', kinds: ['par', 'rect', 'rhomb', 'square'], top: 8, shift: 3 },
]

/** Трапеция ABCD с основаниями AD и BC. Двигаем верхнее основание: имя фигуры считается по координатам. */
export function TrapLabViz() {
  const [[top, shift], setTS] = useState<[number, number]>([4, 1])
  const P = trapPts(top, shift)
  const kind = classify(P)
  const isTrap = kind === 'trap' || kind === 'iso' || kind === 'rtrap'
  const ang = [0, 1, 2, 3].map((i) => Math.round(angleAt(P, i)))
  // углы при боковых сторонах вместе дают 180°: подгоняем округление
  const aA = ang[0]
  const aB = 180 - aA
  const aD = ang[3]
  const aC = 180 - aD
  const legAB = Math.hypot(P[1][0] - P[0][0], P[1][1] - P[0][1])
  const legCD = Math.hypot(P[2][0] - P[3][0], P[2][1] - P[3][1])
  const marks: Record<string, number[]> = { par1: [1, 3] }
  if (!isTrap) marks.par2 = [0, 2]
  if (kind === 'iso') marks.eq1 = [0, 2]
  const rt = [0, 1, 2, 3].filter((i) => Math.abs(angleAt(P, i) - 90) < 1e-6)
  const lead: Record<Kind, string> = {
    trap: 'Основания параллельны, боковые стороны нет — это трапеция.',
    iso: 'Боковые стороны равны — это равнобедренная трапеция.',
    rtrap: 'Есть прямой угол (даже два) — это прямоугольная трапеция.',
    par: 'Боковые стороны тоже стали параллельными! Параллельны обе пары сторон — это уже параллелограмм, а не трапеция.',
    rect: 'Боковые стороны параллельны и все углы прямые — это прямоугольник (параллелограмм), а не трапеция.',
    rhomb: 'Параллельны обе пары сторон — это параллелограмм.',
    square: 'Параллельны обе пары сторон — это параллелограмм.',
    quad: '',
  }
  return (
    <div className="viz qf">
      <div className="viz-title">Лаборатория трапеции</div>
      <div className="viz-step">
        <span className="viz-num">1</span> Двигай верхнее основание
      </div>
      <div className="steppers">
        <Stepper compact label="основание BC" value={top} min={2} max={8} step={1} onChange={(v) => setTS([v, shift])} />
        <Stepper compact label="сдвиг вправо" value={shift} min={0} max={6} step={1} onChange={(v) => setTS([top, v])} />
      </div>
      <div className="chips">
        {TRAP_CHIPS.map((c) => (
          <button key={c.label} className={`chip wide ${c.kinds.includes(kind) ? 'on' : ''}`} onClick={() => setTS([c.top, c.shift])}>
            {c.label}
          </button>
        ))}
      </div>
      <div className="qf-fig">
        <QuadFig pts={P.flatMap((p) => p)} {...marks} rt={rt} angs={isTrap ? [`${aA}°`, `${aB}°`, `${aC}°`, `${aD}°`] : []} view={[-1.5, -1, 15.5, 6]} />
      </div>
      <div className="readout" aria-live="polite">
        <div>
          Сейчас это <strong>{NAME[kind]}</strong>. {lead[kind]}
        </div>
        <div className="viz-calc">
          <Tex tex={isTrap ? `AD\\parallel BC,\\ AB\\nparallel CD` : `AD\\parallel BC,\\ AB\\parallel CD`} />
        </div>
        {isTrap && (
          <>
            <div className="viz-calc">
              <Tex tex={`AB\\approx ${r1(legAB)},\\ CD\\approx ${r1(legCD)}`} /> — боковые стороны {kind === 'iso' ? 'равны' : 'разной длины'}
            </div>
            <div className="muted">
              Углы при боковой стороне вместе дают <Tex tex={`${aA}^\\circ+${aB}^\\circ=180^\\circ`} /> и <Tex tex={`${aD}^\\circ+${aC}^\\circ=180^\\circ`} />: основания параллельны.
            </div>
          </>
        )}
        {!isTrap && <div className="muted">Сделай верхнее основание меньше нижнего (AD = 8), и боковые стороны снова разойдутся.</div>}
      </div>
    </div>
  )
}
