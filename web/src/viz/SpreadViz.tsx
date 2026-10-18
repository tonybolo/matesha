import { useState } from 'react'
import { Tex } from '../components/Tex'
import { Stepper } from './Stepper'
import './SpreadViz.css'

const W = 340
const PAD = 30
const ROW = 24
const px = (v: number) => PAD + (v / 10) * (W - 2 * PAD)
const fmt = (v: number) => String(Math.round(v * 100) / 100).replace('.', ',').replace('-', '−')

// ---------- точные дроби: среднее, отклонения и квадраты — рациональные числа ----------
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
const val = (x: Q) => x.n / x.d
function terminating(d: number): boolean {
  while (d % 2 === 0) d /= 2
  while (d % 5 === 0) d /= 5
  return d === 1
}
const decTex = (v: number) => String(Number(v.toFixed(6))).replace('.', '{,}')
/** Короткая запись для списков: 2{,}5, -4, \approx 0{,}33. */
function qTex(x: Q): string {
  if (x.d === 1) return String(x.n)
  if (terminating(x.d)) return decTex(val(x))
  return `\\approx ${decTex(Math.round(val(x) * 100) / 100)}`
}
/** Итог: десятичная, если она конечная, иначе дробь и приближение: \frac{13}{3}\approx 4{,}33. */
function qTexFull(x: Q): string {
  if (x.d === 1 || terminating(x.d)) return qTex(x)
  return `${x.n < 0 ? '-' : ''}\\frac{${Math.abs(x.n)}}{${x.d}}${qTex(x)}`
}
/** Корень из дроби: точный, если числитель и знаменатель — квадраты. */
function sqrtTex(x: Q): string {
  const a = Math.round(Math.sqrt(x.n))
  const b = Math.round(Math.sqrt(x.d))
  if (a * a === x.n && b * b === x.d) return `=${qTex(q(a, b))}`
  return `\\approx ${decTex(Math.round(Math.sqrt(val(x)) * 100) / 100)}`
}

const PRESETS: number[][] = [
  [1, 3, 7, 9],
  [5, 5, 5, 5],
  [4, 5, 5, 6],
  [2, 4, 4, 6],
  [0, 10],
]

/** Набор точек: отклонения от среднего (стрелки), квадраты отклонений (площади) и дисперсия — средняя площадь. preset="sigma" — ещё и σ. */
export function SpreadViz({ preset }: { preset?: string }) {
  const sigma = preset === 'sigma'
  const [xs, setXs] = useState<number[]>(PRESETS[0])
  const [sel, setSel] = useState(0)
  const n = xs.length
  const s = Math.min(sel, n - 1)
  const S = xs.reduce((a, b) => a + b, 0)
  const mean = q(S, n)
  const m = val(mean)
  const devs = xs.map((x) => q(n * x - S, n))
  const sqs = xs.map((x) => q((n * x - S) ** 2, n * n))
  const D = q(xs.reduce((a, x) => a + (n * x - S) ** 2, 0), n * n * n)
  const sd = Math.sqrt(val(D))

  // строки с точками и стрелками отклонений
  const AY = 10 + n * ROW + 6
  const H1 = AY + 44
  // квадраты: сторона = |отклонение|, масштаб подбирается, чтобы всё влезло в 340 px
  const sides = devs.map((d) => Math.abs(val(d)))
  const totalUnits = sides.reduce((a, b) => a + b, 0) + sd
  const k = Math.min(22, (W - 16 - 10 * (n + 1) - 24) / Math.max(totalUnits, 0.001), 110 / Math.max(...sides, sd, 0.001))
  const H2 = Math.max(...sides, sd) * k + 40
  const base = H2 - 18
  const left = (i: number) => 8 + sides.slice(0, i).reduce((acc, a) => acc + a * k + 10, 0)
  const squares = sides.map((a, i) => ({ x: left(i), side: a * k, i }))
  const dx = left(n) + 18

  const move = (v: number) => setXs((p) => p.map((x, i) => (i === s ? v : x)))

  return (
    <div className="viz">
      <div className="viz-title">{sigma ? 'Дисперсия — средняя площадь, σ — сторона этого квадрата' : 'Отклонения, их квадраты и дисперсия'}</div>
      <div className="chips">
        {PRESETS.map((p, i) => (
          <button key={i} className={`chip wide ${p.join() === xs.join() ? 'on' : ''}`} onClick={() => setXs(p)}>
            {p.join(', ')}
          </button>
        ))}
      </div>

      <svg viewBox={`0 0 ${W} ${H1}`} className="spr-svg" role="img" aria-label={`Точки ${xs.join(', ')}, среднее ${fmt(m)}, стрелки — отклонения от среднего`}>
        {sigma && sd > 0 && <rect x={px(Math.max(0, m - sd))} y={4} width={px(Math.min(10, m + sd)) - px(Math.max(0, m - sd))} height={AY - 4} className="spr-band" />}
        {xs.map((x, i) => {
          const y = 10 + ROW / 2 + i * ROW
          const d = val(devs[i])
          const x0 = px(m)
          const x1 = px(x)
          const dir = d > 0 ? 1 : -1
          return (
            <g key={i} className="spr-row" onClick={() => setSel(i)}>
              <rect x={0} y={y - ROW / 2} width={W} height={ROW} className={`spr-hit ${i === s ? 'on' : ''}`} />
              {Math.abs(x1 - x0) > 9 && (
                <>
                  <line x1={x0} x2={x1 - dir * 9} y1={y} y2={y} className={`spr-arrow c${i % 6}`} />
                  <path d={`M${x1 - dir * 8} ${y - 5} L${x1 - dir * 1} ${y} L${x1 - dir * 8} ${y + 5} z`} className={`spr-head c${i % 6}`} />
                </>
              )}
              <circle cx={x1} cy={y} r={7} className={`spr-dot c${i % 6} ${i === s ? 'sel' : ''}`} />
              <text x={d >= 0 ? x1 + 12 : x1 - 12} y={y + 4} textAnchor={d >= 0 ? 'start' : 'end'} className="spr-dev">
                {d === 0 ? '0' : `${d > 0 ? '+' : '−'}${fmt(Math.abs(d))}`}
              </text>
            </g>
          )
        })}
        <line x1={px(m)} x2={px(m)} y1={4} y2={AY} className="spr-mean" />
        <line x1={PAD - 6} x2={W - PAD + 6} y1={AY} y2={AY} className="axis" />
        {Array.from({ length: 11 }, (_, t) => (
          <g key={t}>
            <line x1={px(t)} x2={px(t)} y1={AY - 4} y2={AY + 4} className="axis" />
            <text x={px(t)} y={AY + 17} className="spr-num">
              {t}
            </text>
          </g>
        ))}
        <text x={Math.max(50, Math.min(W - 50, px(m)))} y={AY + 36} className="spr-mlabel">
          среднее {fmt(m)}
        </text>
      </svg>

      <svg viewBox={`0 0 ${W} ${H2}`} className="spr-svg" role="img" aria-label={`Квадраты отклонений: площади ${sqs.map((x) => fmt(val(x))).join(', ')}; средняя площадь — дисперсия ${fmt(val(D))}`}>
        {squares.map(({ x, side, i }) => (
          <g key={i}>
            {side > 0 ? <rect x={x} y={base - side} width={side} height={side} className={`spr-sq c${i % 6}`} /> : <circle cx={x + 2} cy={base - 2} r={2.5} className={`spr-dot c${i % 6}`} />}
            <text x={x + Math.max(side, 4) / 2} y={side >= 26 ? base - side / 2 + 4 : base - side - 5} className="spr-area">
              {fmt(val(sqs[i]))}
            </text>
          </g>
        ))}
        <rect x={dx} y={base - sd * k} width={sd * k} height={sd * k} className="spr-dsq" />
        <text x={dx + Math.max(sd * k, 4) / 2} y={sd * k >= 30 ? base - (sd * k) / 2 + 4 : base - sd * k - 5} className="spr-dlabel">
          D = {fmt(val(D))}
        </text>
        {sigma && sd > 0 && (
          <text x={dx + (sd * k) / 2} y={base + 14} className="spr-slabel">
            σ ≈ {fmt(sd)}
          </text>
        )}
        <line x1={4} x2={W - 4} y1={base} y2={base} className="spr-base" />
      </svg>

      <div className="viz-step">Выбери точку и двигай её (или нажми на её строку)</div>
      <div className="chips spr-chips" role="group" aria-label="Точки">
        {xs.map((x, i) => (
          <button key={i} className={`chip ${i === s ? 'on' : ''}`} onClick={() => setSel(i)} aria-label={`Точка ${i + 1}: ${x}`}>
            <span className={`spr-chipdot c${i % 6}`} aria-hidden />
            {x}
          </button>
        ))}
      </div>
      <div className="steppers">
        <Stepper compact label={`точка ${s + 1}`} value={xs[s]} min={0} max={10} step={1} onChange={move} format={fmt} />
        <button
          className="btn small"
          onClick={() => {
            setXs((p) => [...p, 5])
            setSel(n)
          }}
          disabled={n >= 6}
        >
          + точка
        </button>
        <button
          className="btn small ghost"
          onClick={() => {
            setXs((p) => p.filter((_, i) => i !== s))
            setSel(Math.max(0, s - 1))
          }}
          disabled={n <= 2}
        >
          − точка
        </button>
      </div>

      <div className="readout spr-readout" aria-live="polite">
        <div>
          <span className="spr-k">1. Среднее:</span> <Tex tex={`\\bar{x}=(${xs.join('+')}):${n}=${qTexFull(mean)}`} />
        </div>
        <div>
          <span className="spr-k">2. Отклонения:</span> <Tex tex={devs.map(qTex).join(';\\ ')} /> <span className="muted">(сумма 0)</span>
        </div>
        <div>
          <span className="spr-k">3. Квадраты:</span> <Tex tex={sqs.map(qTex).join(';\\ ')} />
        </div>
        <div>
          <span className="spr-k">4. Дисперсия:</span> <Tex tex={`D=(${sqs.map(qTex).join('+')}):${n}=${qTexFull(D)}`} />
        </div>
        {sigma && (
          <div>
            <span className="spr-k">σ:</span> <Tex tex={`\\sigma=\\sqrt{D}${sqrtTex(D)}`} />
            {sd > 0 ? ` — типичное расстояние до среднего; полоса на картинке от ${fmt(Math.max(0, m - sd))} до ${fmt(Math.min(10, m + sd))}.` : ' — все точки в одном месте, разброса нет.'}
          </div>
        )}
        <p className="spr-note">
          {val(D) === 0
            ? 'Все точки совпали со средним: отклонения нулевые, дисперсия 0.'
            : `Чем дальше точки от среднего, тем больше квадраты и тем больше дисперсия. Сейчас D = ${fmt(val(D))}${terminating(D.d) ? '' : ' (примерно)'}.`}
        </p>
      </div>
    </div>
  )
}
