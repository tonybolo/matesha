import { useState } from 'react'
import { Tex } from '../components/Tex'
import { Stepper } from './Stepper'
import './DistributionViz.css'

// ---------- точные дроби ----------
type Q = { n: number; d: number }
const gcd = (a: number, b: number): number => (b === 0 ? Math.abs(a) : gcd(b, a % b))
function q(n: number, d = 1): Q {
  if (d < 0) {
    n = -n
    d = -d
  }
  const g = gcd(n, d) || 1
  return { n: n / g, d: d / g }
}
const add = (a: Q, b: Q) => q(a.n * b.d + b.n * a.d, a.d * b.d)
const sub = (a: Q, b: Q) => q(a.n * b.d - b.n * a.d, a.d * b.d)
const mul = (a: Q, b: Q) => q(a.n * b.n, a.d * b.d)
const sumQ = (xs: Q[]) => xs.reduce(add, q(0))
const val = (x: Q) => x.n / x.d
const eq = (a: Q, b: Q) => a.n === b.n && a.d === b.d
function terminating(d: number): boolean {
  while (d % 2 === 0) d /= 2
  while (d % 5 === 0) d /= 5
  return d === 1
}
const decTex = (v: number) => String(Number(v.toFixed(6))).replace('.', '{,}')
/** Вероятность или число в TeX: 0{,}3; \frac{1}{6} (frac — дроби, а не десятичные). */
function tq(x: Q, frac = false): string {
  if (x.d === 1) return String(x.n)
  if (terminating(x.d) && !frac) return decTex(val(x))
  return `${x.n < 0 ? '-' : ''}\\frac{${Math.abs(x.n)}}{${x.d}}`
}
/** Итог: 2{,}5 или \frac{35}{12}\approx 2{,}92. */
function tqFull(x: Q): string {
  if (x.d === 1 || terminating(x.d)) return tq(x)
  return `${tq(x, true)}\\approx ${decTex(Math.round(val(x) * 100) / 100)}`
}
/** Короткая подпись для SVG: 0,3 или 1/6. */
function sq(x: Q, frac = false): string {
  if (x.d === 1) return String(x.n).replace('-', '−')
  if (terminating(x.d) && !frac) return String(Number(val(x).toFixed(6))).replace('.', ',').replace('-', '−')
  return `${x.n < 0 ? '−' : ''}${Math.abs(x.n)}/${x.d}`
}
const par = (s: string, neg: boolean) => (neg ? `(${s})` : s)
const fmt = (v: number) => String(Math.round(v * 100) / 100).replace('.', ',').replace('-', '−')

// ---------- столбики распределения ----------
const W = 340
const PADX = 26

function Bars({ xs, ps, min, max, step, sel, onPick, cls = '', missing, mean, sd, frac, label, height = 170, cat = false, axisLabels = false }: {
  xs: number[]
  ps: Q[]
  min: number
  max: number
  step: number
  sel?: number
  onPick?: (i: number) => void
  cls?: string
  missing?: number
  mean?: number
  sd?: number
  frac?: boolean
  label: string
  height?: number
  /** Столбики через равные промежутки (как категории), а не по числовой оси. */
  cat?: boolean
  /** Подписи чисел на оси вместо подписей под столбиками и без вероятностей над ними. */
  axisLabels?: boolean
}) {
  const unit = (W - 2 * PADX) / (max - min)
  const x = (v: number) => PADX + (v - min) * unit
  const pos = (i: number) => (cat ? PADX + ((i + 0.5) / xs.length) * (W - 2 * PADX) : x(xs[i]))
  const bw = cat ? Math.min(46, ((W - 2 * PADX) / xs.length) * 0.6) : Math.max(9, Math.min(34, unit * 0.8))
  const base = height - (mean === undefined ? 24 : 52)
  const top = 22
  const maxP = Math.max(0.5, ...ps.map(val))
  const ticks: number[] = []
  if (!cat) for (let t = Math.ceil(min / step) * step; t <= max + 1e-9; t += step) ticks.push(t)
  return (
    <svg viewBox={`0 0 ${W} ${height}`} className="dst-svg" role="img" aria-label={label}>
      {sd !== undefined && mean !== undefined && sd > 0 && <rect x={x(Math.max(min, mean - sd))} y={base - 4} width={x(Math.min(max, mean + sd)) - x(Math.max(min, mean - sd))} height={8} className="dst-band" />}
      <line x1={PADX - 10} x2={W - PADX + 10} y1={base} y2={base} className="axis" />
      {ticks.map((t) => (
        <g key={t}>
          <line x1={x(t)} x2={x(t)} y1={base} y2={base + 4} className="axis" />
          {axisLabels && (
            <text x={x(t)} y={base + 16} className="dst-x">
              {fmt(t)}
            </text>
          )}
        </g>
      ))}
      {xs.map((v, i) => {
        const h = missing === i && val(ps[i]) === 0 ? 0 : (val(ps[i]) / maxP) * (base - top - 14)
        const cx = pos(i)
        return (
          <g key={i} className={onPick ? 'dst-pick' : undefined} onClick={onPick ? () => onPick(i) : undefined}>
            {onPick && <rect x={cx - Math.max(bw, 36) / 2} y={0} width={Math.max(bw, 36)} height={base + 16} className={`dst-hit ${sel === i ? 'on' : ''}`} />}
            {missing === i && <rect x={cx - bw / 2} y={top + 14} width={bw} height={base - top - 14} className="dst-ghost" />}
            <rect x={cx - bw / 2} y={base - h} width={bw} height={h} className={`dst-bar ${cls} ${sel === i ? 'sel' : ''}`} />
            {!axisLabels && (
              <>
                <text x={cx} y={Math.max(top + 10, base - h - 6)} className="dst-p">
                  {missing === i ? (val(ps[i]) === 0 ? 'p = ?' : `p = ${sq(ps[i], frac)}`) : sq(ps[i], frac)}
                </text>
                <text x={cx} y={base + 16} className="dst-x">
                  {fmt(v)}
                </text>
              </>
            )}
          </g>
        )
      })}
      {mean !== undefined && (
        <>
          <path d={`M${x(mean)} ${base + 20} l-10 20 h20 z`} className="dst-fulcrum" />
          <text x={Math.max(56, Math.min(W - 56, x(mean)))} y={base + 50} className="dst-elabel">
            E = {fmt(mean)}
          </text>
        </>
      )}
    </svg>
  )
}

/** Таблица распределения в TeX. */
function tableTex(name: string, xs: number[], ps: (Q | null)[], frac = false) {
  return `\\begin{array}{c|${'c'.repeat(xs.length)}} ${name} & ${xs.join(' & ')} \\cr \\hline P & ${ps.map((p) => (p ? tq(p, frac) : 'p')).join(' & ')} \\end{array}`
}

const six = (): Q[] => Array.from({ length: 6 }, () => q(1, 6))

type Preset = { title: string; xs: number[]; ps: Q[]; frac?: boolean; edit?: boolean; missing?: number; note: string }

// ---------- шаг 5: таблица распределения, сумма вероятностей ----------
const TABLE: Preset[] = [
  { title: 'Монета', xs: [0, 1], ps: [q(1, 2), q(1, 2)], frac: true, note: 'X — число орлов при одном броске монеты.' },
  { title: 'Кубик', xs: [1, 2, 3, 4, 5, 6], ps: six(), frac: true, note: 'X — число очков на кубике.' },
  { title: 'Своя игра', xs: [0, 10, 50], ps: [q(6, 10), q(3, 10), q(1, 10)], edit: true, note: 'X — выигрыш в очках. Нажми на столбик и меняй его вероятность.' },
  { title: 'Найди p', xs: [1, 2, 3, 4], ps: [q(2, 10), q(4, 10), q(1, 10), q(0)], edit: true, missing: 3, note: 'Вероятность значения 4 неизвестна. Нажми на пунктирный столбик и подбери её.' },
]

function TableMode() {
  const [pi, setPi] = useState(0)
  const pr = TABLE[pi]
  const [tenths, setTenths] = useState<number[]>(() => pr.ps.map((p) => Math.round(val(p) * 10)))
  const [sel, setSel] = useState(pr.missing ?? 0)
  const ps = pr.edit ? tenths.map((t) => q(t, 10)) : pr.ps
  const total = sumQ(ps)
  const one = eq(total, q(1))
  const pick = (i: number) => {
    setPi(i)
    setTenths(TABLE[i].ps.map((p) => Math.round(val(p) * 10)))
    setSel(TABLE[i].missing ?? 0)
  }
  const s = Math.min(sel, pr.xs.length - 1)
  const others = pr.missing !== undefined ? sumQ(ps.filter((_, i) => i !== pr.missing)) : q(0)
  const unknownP = pr.missing !== undefined && val(ps[pr.missing]) === 0
  const sumTex =
    pr.frac && pr.xs.length === 6
      ? `6\\cdot\\frac{1}{6}=1`
      : unknownP
        ? `${ps.map((p, i) => (i === pr.missing ? 'p' : tq(p))).join('+')}=${tq(others)}+p`
        : `${ps.map((p) => tq(p, pr.frac)).join('+')}=${tq(total)}`
  return (
    <div className="viz">
      <div className="viz-title">Таблица распределения: значения и их вероятности</div>
      <div className="chips">
        {TABLE.map((p, i) => (
          <button key={p.title} className={`chip wide ${i === pi ? 'on' : ''}`} onClick={() => pick(i)}>
            {p.title}
          </button>
        ))}
      </div>
      <p className="dst-note">{pr.note}</p>
      <Bars
        xs={pr.xs}
        ps={ps}
        min={0}
        max={1}
        step={1}
        cat
        sel={pr.edit ? s : undefined}
        onPick={pr.edit ? setSel : undefined}
        missing={pr.missing}
        frac={pr.frac}
        label={`Столбики вероятностей: ${pr.xs.map((x, i) => `${x} — ${sq(ps[i], pr.frac)}`).join(', ')}`}
      />
      {pr.edit && (
        <div className="steppers">
          <Stepper compact label={`вероятность значения ${pr.xs[s]}`} value={tenths[s] / 10} min={0} max={1} step={0.1} onChange={(v) => setTenths((t) => t.map((x, i) => (i === s ? Math.round(v * 10) : x)))} />
        </div>
      )}
      <div className={`readout ${one || unknownP ? '' : 'bad'}`} aria-live="polite">
        <div className="dst-table">
          <Tex tex={tableTex('X', pr.xs, ps.map((p, i) => (i === pr.missing && val(p) === 0 ? null : p)), pr.frac)} display />
        </div>
        <div>
          Сумма вероятностей: <Tex tex={sumTex} />{' '}
          {unknownP
            ? '— а должна быть ровно 1.'
            : one
            ? pr.missing !== undefined
              ? '✓'
              : '✓ — это настоящая таблица распределения: какое-то значение выпадает обязательно.'
            : val(total) < 1
              ? `— не хватает ${sq(sub(q(1), total))} до 1. Таблицы распределения так не бывает.`
              : `— больше 1 на ${sq(sub(total, q(1)))}. Так не бывает.`}
        </div>
        {pr.missing !== undefined && (
          <div>
            {one ? (
              <strong>
                Верно: <Tex tex={`p=1-(${ps.filter((_, i) => i !== pr.missing).map((p) => tq(p)).join('+')})=1-${tq(others)}=${tq(ps[pr.missing])}`} /> 🎉
              </strong>
            ) : (
              <>Подбери p кнопками «−» и «+», чтобы сумма стала ровно 1. Известные вероятности вместе дают {sq(others)}.</>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// ---------- шаг 7: E — точка равновесия, D — разброс ----------
const VAR: Preset[] = [
  { title: 'Игра А: всегда 5', xs: [5], ps: [q(1)], note: 'Всегда 5 очков — случайности нет.' },
  { title: 'Игра Б: 0 или 10', xs: [0, 10], ps: [q(1, 2), q(1, 2)], note: 'Монета: 0 или 10 очков.' },
  { title: 'Кубик', xs: [1, 2, 3, 4, 5, 6], ps: six(), frac: true, note: 'Очки на кубике.' },
  { title: 'Своя', xs: [0, 2, 4, 6], ps: [q(1, 10), q(2, 10), q(3, 10), q(4, 10)], edit: true, note: 'Нажми на столбик и меняй вероятность.' },
]

function VarMode() {
  const [pi, setPi] = useState(0)
  const pr = VAR[pi]
  const [tenths, setTenths] = useState<number[]>(() => VAR[3].ps.map((p) => Math.round(val(p) * 10)))
  const [sel, setSel] = useState(0)
  const ps = pr.edit ? tenths.map((t) => q(t, 10)) : pr.ps
  const total = sumQ(ps)
  const ok = eq(total, q(1))
  const E = sumQ(pr.xs.map((x, i) => mul(q(x), ps[i])))
  const devs = pr.xs.map((x) => sub(q(x), E))
  const parts = devs.map((d, i) => mul(mul(d, d), ps[i]))
  const D = sumQ(parts)
  const sd = Math.sqrt(val(D))
  const s = Math.min(sel, pr.xs.length - 1)
  const frac = pr.frac
  const eTex = pr.xs.length === 6 && frac ? `E(X)=\\frac{1+2+3+4+5+6}{6}=3{,}5` : `E(X)=${pr.xs.map((x, i) => `${par(String(x), x < 0)}\\cdot ${tq(ps[i], frac)}`).join('+')}=${tqFull(E)}`
  return (
    <div className="viz">
      <div className="viz-title">E — точка равновесия, D — разброс вокруг неё</div>
      <div className="chips">
        {VAR.map((p, i) => (
          <button key={p.title} className={`chip wide ${i === pi ? 'on' : ''}`} onClick={() => setPi(i)}>
            {p.title}
          </button>
        ))}
      </div>
      <p className="dst-note">{pr.note}</p>
      <Bars
        xs={pr.xs}
        ps={ps}
        min={pr.xs.length === 6 ? 0 : -1}
        max={pr.xs.length === 6 ? 7 : 11}
        step={1}
        sel={pr.edit ? s : undefined}
        onPick={pr.edit ? setSel : undefined}
        mean={ok ? val(E) : undefined}
        sd={ok ? sd : undefined}
        frac={frac}
        label={`Столбики вероятностей ${pr.xs.map((x, i) => `${x} — ${sq(ps[i], frac)}`).join(', ')}; опора в точке E = ${fmt(val(E))}`}
        height={196}
      />
      {pr.edit && (
        <div className="steppers">
          <Stepper compact label={`вероятность значения ${pr.xs[s]}`} value={tenths[s] / 10} min={0} max={1} step={0.1} onChange={(v) => setTenths((t) => t.map((x, i) => (i === s ? Math.round(v * 10) : x)))} />
        </div>
      )}
      <div className={`readout ${ok ? '' : 'bad'}`} aria-live="polite">
        {!ok ? (
          <div>
            Сумма вероятностей сейчас <Tex tex={tq(total)} />, а должна быть ровно 1. Поправь столбики — тогда посчитаем E и D.
          </div>
        ) : (
          <>
            <div>
              <Tex tex={eTex} /> — сюда ставим опору (зелёная полоса — от <Tex tex={`E-\\sigma`} /> до <Tex tex={`E+\\sigma`} />).
            </div>
            <ul className="dst-rows">
              {pr.xs.map((x, i) => (
                <li key={i}>
                  <Tex tex={`x=${x}:\\ (${x}-${par(tq(E), val(E) < 0)})^2\\cdot ${tq(ps[i], frac)}=${par(tq(devs[i]), val(devs[i]) < 0)}^2\\cdot ${tq(ps[i], frac)}${terminating(parts[i].d) ? '=' : ''}${terminating(parts[i].d) ? tq(parts[i]) : `\\approx ${decTex(Math.round(val(parts[i]) * 100) / 100)}`}`} />
                </li>
              ))}
            </ul>
            <div>
              <Tex tex={`D(X)=${tqFull(D)}`} />, <Tex tex={`\\sigma(X)=\\sqrt{D(X)}\\approx ${decTex(Math.round(sd * 100) / 100)}`} />.{' '}
              {val(D) === 0 ? 'Разброса нет: величина всегда равна одному числу.' : 'Чем дальше столбики от опоры, тем больше дисперсия.'}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

// ---------- шаг 8: Y = aX + b ----------
const LIN_X = [1, 2, 3]
const LIN_P = [q(1, 4), q(1, 2), q(1, 4)]
const LIN_PRESETS: [number, number][] = [
  [1, 3],
  [2, 0],
  [-1, 0],
  [2, 3],
  [-2, 5],
]
const linTex = (a: number, b: number, v = 'X') => `${a === 1 ? '' : a === -1 ? '-' : a}${v}${b === 0 ? '' : b > 0 ? `+${b}` : `-${-b}`}`

function LinMode() {
  const [[a, b], setAB] = useState<[number, number]>(LIN_PRESETS[3])
  const ys = LIN_X.map((x) => a * x + b)
  const EX = sumQ(LIN_X.map((x, i) => mul(q(x), LIN_P[i])))
  const DX = sumQ(LIN_X.map((x, i) => mul(mul(sub(q(x), EX), sub(q(x), EX)), LIN_P[i])))
  // по формулам
  const EYf = add(mul(q(a), EX), q(b))
  const DYf = mul(q(a * a), DX)
  // прямо по таблице Y
  const EYt = sumQ(ys.map((y, i) => mul(q(y), LIN_P[i])))
  const DYt = sumQ(ys.map((y, i) => mul(mul(sub(q(y), EYt), sub(q(y), EYt)), LIN_P[i])))
  const okE = eq(EYf, EYt)
  const okD = eq(DYf, DYt)
  const setA = (v: number) => setAB(([pa, pb]) => [v === 0 ? (pa > 0 ? -1 : 1) : v, pb])
  const Y = linTex(a, b)
  return (
    <div className="viz">
      <div className="viz-title">Сдвигаем и растягиваем: Y = aX + b</div>
      <div className="chips">
        {LIN_PRESETS.map(([pa, pb]) => (
          <button key={`${pa},${pb}`} className={`chip wide ${pa === a && pb === b ? 'on' : ''}`} onClick={() => setAB([pa, pb])}>
            <Tex tex={`Y=${linTex(pa, pb)}`} />
          </button>
        ))}
      </div>
      <div className="steppers">
        <Stepper compact label="a (растянуть)" value={a} min={-3} max={3} step={1} onChange={setA} format={fmt} />
        <Stepper compact label="b (сдвинуть)" value={b} min={-6} max={6} step={1} onChange={(v) => setAB(([pa]) => [pa, v])} format={fmt} />
      </div>
      <p className="dst-row-title">
        <Tex tex="X" />: значения <Tex tex="1;\ 2;\ 3" />, вероятности <Tex tex="\frac{1}{4};\ \frac{1}{2};\ \frac{1}{4}" />
      </p>
      <Bars xs={LIN_X} ps={LIN_P} min={-15} max={15} step={5} cls="dst-x0" mean={val(EX)} frac label="Таблица X: значения 1, 2, 3" height={150} axisLabels />
      <p className="dst-row-title">
        <Tex tex={`Y=${Y}`} />: значения <Tex tex={ys.join(';\\ ')} />, вероятности те же
      </p>
      <Bars xs={ys} ps={LIN_P} min={-15} max={15} step={5} cls="dst-y" mean={val(EYt)} frac label={`Таблица Y: значения ${ys.join(', ')}`} height={150} axisLabels />
      <div className="readout" aria-live="polite">
        <div>
          <Tex tex={`E(Y)=${a}\\cdot E(X)${b >= 0 ? '+' : '-'}${Math.abs(b)}=${a}\\cdot ${tq(EX)}${b >= 0 ? '+' : '-'}${Math.abs(b)}=${tq(EYf)}`} />; по таблице <Tex tex="Y" /> тоже <Tex tex={tq(EYt)} /> {okE ? '✓' : '✗'}
        </div>
        <div>
          <Tex tex={`D(Y)=${a < 0 ? `(${a})` : a}^2\\cdot D(X)=${a * a}\\cdot ${tq(DX)}=${tq(DYf)}`} />; по таблице тоже <Tex tex={tq(DYt)} /> {okD ? '✓' : '✗'}
        </div>
        <div>
          {b !== 0 ? `Сдвиг на ${fmt(b)} передвинул всё вместе с опорой, а разброс не изменил. ` : ''}
          {Math.abs(a) !== 1 ? `Множитель ${fmt(a)} растянул отклонения в ${Math.abs(a)} раза, поэтому D выросла в ${a * a} раз${a * a % 10 >= 2 && a * a % 10 <= 4 ? 'а' : ''}.` : a === -1 ? 'Множитель −1 отразил таблицу зеркально: разброс тот же.' : ''}
        </div>
      </div>
    </div>
  )
}

/** Таблица распределения случайной величины. preset="var" — E как точка равновесия и дисперсия; preset="lin" — Y = aX + b. */
export function DistributionViz({ preset }: { preset?: string }) {
  if (preset === 'var') return <VarMode />
  if (preset === 'lin') return <LinMode />
  return <TableMode />
}
