import { useState } from 'react'
import { Stepper } from './Stepper'
import './BalanceViz.css'

type Scale = { min: number; max: number; step: number }
const S10: Scale = { min: 0, max: 10, step: 1 }

const W = 340
const PAD = 26
const R = 10
const fmt = (v: number) => String(Math.round(v * 100) / 100).replace('.', ',').replace('-', '−')
const exact = (v: number) => Math.abs(v * 100 - Math.round(v * 100)) < 1e-6
const nice = (v: number) => (exact(v) ? fmt(v) : `≈ ${fmt(v)}`)
const sum = (a: number[]) => a.reduce((s, v) => s + v, 0)
const px = (v: number, s: Scale) => PAD + ((v - s.min) / (s.max - s.min)) * (W - 2 * PAD)
const weightsWord = (n: number) => (n % 10 === 1 && n % 100 !== 11 ? 'грузик' : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14) ? 'грузика' : 'грузиков')

/** Уровень каждого кружка в стопке: самый нижний, где он не задевает уже поставленные (как точки на диаграмме). */
function levelsOf(xsPx: number[]): number[] {
  const order = xsPx.map((x, i) => ({ x, i })).sort((a, b) => a.x - b.x || a.i - b.i)
  const levels = Array<number>(xsPx.length).fill(0)
  const placed: { x: number; k: number }[] = []
  for (const { x, i } of order) {
    let k = 0
    while (placed.some((p) => p.k === k && Math.abs(p.x - x) < 2 * R - 1)) k++
    levels[i] = k
    placed.push({ x, k })
  }
  return levels
}

/** «2 + 1 + 1 = 4» для расстояний до опоры. */
function distList(d: number[]): string {
  if (d.length === 0) return 'нет грузиков'
  return d.length === 1 ? nice(d[0]) : `${d.map(fmt).join(' + ')} = ${nice(sum(d))}`
}

function Balance({ xs, f, angle, scale, sel, onPick, caption, room, tilt }: {
  xs: number[]
  f: number
  angle: number
  scale: Scale
  sel?: number
  onPick?: (i: number) => void
  caption: string
  /** Сколько грузиков стопкой помещается без увеличения картинки. */
  room: number
  /** Нужен запас сверху на наклон. */
  tilt: boolean
}) {
  const levels = levelsOf(xs.map((x) => px(x, scale)))
  const top = Math.max(room, ...levels.map((k) => k + 1))
  const RY = (tilt ? 30 : 8) + top * (2 * R + 1) + 9
  const H = RY + 66
  const fx = px(f, scale)
  const ticks: number[] = []
  for (let t = scale.min; t <= scale.max + 1e-9; t += scale.step) ticks.push(t)
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="bal-svg" role="img" aria-label={`Линейка с грузиками в точках ${xs.join(', ')}; опора в точке ${fmt(f)}`}>
      <line x1={6} x2={W - 6} y1={RY + 42} y2={RY + 42} className="bal-ground" />
      <g className="bal-tilt" style={{ transform: `rotate(${angle}deg)`, transformOrigin: `${fx}px ${RY + 9}px` }}>
        <rect x={PAD - 14} y={RY - 9} width={W - 2 * PAD + 28} height={18} rx={4} className="bal-ruler" />
        {ticks.map((t) => (
          <g key={t}>
            <line x1={px(t, scale)} x2={px(t, scale)} y1={RY - 9} y2={RY - 5} className="bal-tick" />
            <text x={px(t, scale)} y={RY + 5} className="bal-num">
              {t}
            </text>
          </g>
        ))}
        {xs.map((x, i) => {
          const cy = RY - 9 - R - 1 - levels[i] * (2 * R + 1)
          return (
            <g key={i} className={onPick ? 'bal-pick' : undefined} onClick={onPick ? () => onPick(i) : undefined}>
              <circle cx={px(x, scale)} cy={cy} r={R} className={`bal-w w${i % 6} ${sel === i ? 'sel' : ''}`} />
              <text x={px(x, scale)} y={cy + 4} className="bal-wnum">
                {i + 1}
              </text>
            </g>
          )
        })}
      </g>
      <path d={`M${fx} ${RY + 10} l-15 32 h30 z`} className="bal-fulcrum" />
      <text x={Math.max(48, Math.min(W - 48, fx))} y={RY + 60} className="bal-flabel">
        {caption}
      </text>
    </svg>
  )
}

const PRESETS: number[][] = [
  [2, 3, 3, 5, 7],
  [1, 2, 6],
  [0, 1, 2, 9],
  [4, 6],
  [1, 1, 1, 9],
]

/** Одна линейка: грузики двигаются кнопками, опора стоит в среднем сама или её ставит ребёнок. */
function Single() {
  const [xs, setXs] = useState<number[]>(PRESETS[0])
  const [sel, setSel] = useState(0)
  const [hand, setHand] = useState(false)
  const [f, setF] = useState(3)
  const n = xs.length
  const S = sum(xs)
  const mean = S / n
  const at = hand ? f : mean
  const imb = S - n * at // сумма (x − опора): плюс — перевес справа
  const balanced = Math.abs(imb) < 1e-9
  const angle = hand ? Math.max(-8, Math.min(8, imb * 2.5)) : 0
  const left = xs.filter((x) => x < at - 1e-9).map((x) => at - x)
  const right = xs.filter((x) => x > at + 1e-9).map((x) => x - at)
  const onTop = n - left.length - right.length
  const s = Math.min(sel, n - 1)

  const move = (v: number) => setXs((p) => p.map((x, i) => (i === s ? v : x)))
  const add = () => {
    setXs((p) => [...p, 5])
    setSel(n)
  }
  const remove = () => {
    setXs((p) => p.filter((_, i) => i !== s))
    setSel(Math.max(0, s - 1))
  }
  const toHand = () => {
    setHand(true)
    setF(Math.max(0, Math.min(10, Math.round(mean) - 1)))
  }

  return (
    <div className="viz">
      <div className="viz-title">Линейка с грузиками: где поставить опору?</div>
      <div className="chips">
        {PRESETS.map((p, i) => (
          <button key={i} className={`chip wide ${p.join() === xs.join() ? 'on' : ''}`} onClick={() => setXs(p)}>
            {p.join(', ')}
          </button>
        ))}
      </div>
      <Balance xs={xs} f={at} angle={angle} scale={S10} sel={s} onPick={setSel} caption={hand ? `опора: ${fmt(f)}` : `среднее: ${nice(mean)}`} room={3} tilt />
      <div className="viz-step">
        <span className="viz-num">1</span> Выбери грузик и двигай его
      </div>
      <div className="chips bal-chips" role="group" aria-label="Грузики">
        {xs.map((x, i) => (
          <button key={i} className={`chip ${i === s ? 'on' : ''}`} onClick={() => setSel(i)} aria-label={`Грузик ${i + 1} в точке ${x}`}>
            <span className={`bal-dot w${i % 6}`} aria-hidden />
            {x}
          </button>
        ))}
      </div>
      <div className="steppers">
        <Stepper compact label={`грузик ${s + 1}`} value={xs[s]} min={0} max={10} step={1} onChange={move} format={fmt} />
        <button className="btn small" onClick={add} disabled={n >= 6}>
          + грузик
        </button>
        <button className="btn small ghost" onClick={remove} disabled={n <= 2}>
          − грузик
        </button>
      </div>
      <div className="viz-step">
        <span className="viz-num">2</span> Кто ставит опору?
      </div>
      <div className="chips">
        <button className={`chip wide ${!hand ? 'on' : ''}`} onClick={() => setHand(false)}>
          Опора встаёт в среднее сама
        </button>
        <button className={`chip wide ${hand ? 'on' : ''}`} onClick={toHand}>
          Поставлю опору сам
        </button>
      </div>
      {hand && (
        <div className="steppers">
          <Stepper compact label="опора" value={f} min={0} max={10} step={0.5} onChange={setF} format={fmt} />
          <button className="btn small" onClick={() => setF(mean)} disabled={balanced}>
            Поставить в среднее
          </button>
        </div>
      )}
      <div className={`readout ${hand && !balanced ? 'bad' : ''}`} aria-live="polite">
        <p className="bal-line">
          Грузики: {xs.join(', ')}. Сумма {S}, {weightsWord(n)} {n}, среднее {S} : {n} = {nice(mean)}.
        </p>
        {!hand ? (
          left.length === 0 && right.length === 0 ? (
            <p className="bal-line">Все грузики в одной точке — опора прямо под ними, линейка в равновесии ⚖️</p>
          ) : (
            <p className="bal-line">
              Опора под средним. Слева расстояния до опоры: {distList(left)}, справа: {distList(right)} — поровну, поэтому линейка в равновесии ⚖️
              {onTop > 0 && ` Ещё ${onTop} ${weightsWord(onTop)} стоит прямо над опорой.`}
            </p>
          )
        ) : (
          <>
            <p className="bal-line">
              Опора в точке {fmt(f)}. Слева расстояния до опоры: {distList(left)}, справа: {distList(right)}.
            </p>
            <p className="bal-line">
              <strong>
                {balanced
                  ? 'Поровну — равновесие ⚖️ Опора стоит ровно в среднем.'
                  : imb > 0
                    ? `Справа перевес ${nice(imb)} — линейка падает вправо. Сдвинь опору вправо, к среднему ${nice(mean)}.`
                    : `Слева перевес ${nice(-imb)} — линейка падает влево. Сдвинь опору влево, к среднему ${nice(mean)}.`}
              </strong>
            </p>
          </>
        )}
      </div>
    </div>
  )
}

type Person = { name: string; xs: number[] }
const PAIRS: { title: string; unit: string; scale: Scale; a: Person; b: Person }[] = [
  { title: 'Петя и Вася', unit: '', scale: S10, a: { name: 'Петя', xs: [5, 5, 5, 5] }, b: { name: 'Вася', xs: [1, 3, 7, 9] } },
  { title: 'Два города', unit: '°', scale: { min: 0, max: 30, step: 5 }, a: { name: 'Тихий', xs: [14, 15, 16] }, b: { name: 'Ветреный', xs: [5, 15, 25] } },
  { title: 'Аня и Боря', unit: '', scale: { min: 0, max: 6, step: 1 }, a: { name: 'Аня', xs: [4, 4, 4, 4] }, b: { name: 'Боря', xs: [5, 5, 3, 3] } },
]

/** Два набора с одинаковым средним: обе линейки в равновесии, а грузики разбросаны по-разному. */
function Two() {
  const [pi, setPi] = useState(0)
  const { scale, unit, a, b } = PAIRS[pi]
  const stat = (p: Person) => {
    const m = sum(p.xs) / p.xs.length
    const dev = p.xs.map((x) => Math.abs(x - m))
    return { m, dev, range: Math.max(...p.xs) - Math.min(...p.xs), spread: sum(dev.map((d) => d * d)) / p.xs.length }
  }
  const A = stat(a)
  const B = stat(b)
  const same = Math.abs(A.m - B.m) < 1e-9
  const wider = Math.abs(A.spread - B.spread) < 1e-9 ? null : A.spread > B.spread ? a.name : b.name
  return (
    <div className="viz">
      <div className="viz-title">Одинаковое среднее — разный разброс</div>
      <div className="chips">
        {PAIRS.map((p, i) => (
          <button key={p.title} className={`chip wide ${i === pi ? 'on' : ''}`} onClick={() => setPi(i)}>
            {p.title}
          </button>
        ))}
      </div>
      {[a, b].map((p, k) => (
        <div key={p.name}>
          <p className="bal-name">
            {p.name}: {p.xs.map((x) => `${x}${unit}`).join(', ')}
          </p>
          <Balance xs={p.xs} f={(k === 0 ? A : B).m} angle={0} scale={scale} caption={`среднее: ${nice((k === 0 ? A : B).m)}${unit}`} room={1} tilt={false} />
        </div>
      ))}
      <div className="readout" aria-live="polite">
        <p className="bal-line">
          Среднее: {a.name} — {nice(A.m)}
          {unit}, {b.name} — {nice(B.m)}
          {unit}
          {same ? ' — одинаковое, обе линейки в равновесии.' : '.'}
        </p>
        <p className="bal-line">
          Насколько числа отходят от среднего: {a.name} — {A.dev.map(fmt).join(', ')}
          {A.spread === 0 ? ' (разброса нет)' : ''}; {b.name} — {B.dev.map(fmt).join(', ')}
          {B.spread === 0 ? ' (разброса нет)' : ''}.
        </p>
        <p className="bal-line">
          Размах (наибольшее минус наименьшее): {a.name} — {fmt(A.range)}
          {unit}, {b.name} — {fmt(B.range)}
          {unit}.
        </p>
        <p className="bal-line">
          <strong>{wider ? `${same ? 'Среднее одинаковое, а разброс' : 'Разброс'} больше у набора «${wider}».` : 'Разброс у наборов одинаковый.'}</strong>
        </p>
      </div>
    </div>
  )
}

/** Среднее арифметическое — точка равновесия линейки с одинаковыми грузиками. preset="two" — два набора с одним средним. */
export function BalanceViz({ preset }: { preset?: string }) {
  return preset === 'two' ? <Two /> : <Single />
}
