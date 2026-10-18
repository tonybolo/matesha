import { useState } from 'react'
import { Tex } from '../components/Tex'
import { Stepper } from './Stepper'
import './JumpsViz.css'

const MIN = -12
const MAX = 12
const LIM = 10
const W = 340
const H = 122
const PAD = 16
const Y = 76
const px = (x: number) => PAD + ((x - MIN) / (MAX - MIN)) * (W - 2 * PAD)
const fmt = (v: number) => (v < 0 ? `−${-v}` : String(v))
const tex = (v: number, wrap = false) => (v < 0 && wrap ? `\\left(${v}\\right)` : String(v))
const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v))

type Op = '+' | '-'
const ADD: [number, number][] = [
  [-3, 5],
  [2, -6],
  [-4, -3],
  [5, -5],
]
const SUB: [number, number][] = [
  [3, 5],
  [3, -5],
  [-2, -6],
  [-4, 3],
]

/** Кошелёк: 3 ₽, долг 3 ₽, 0 ₽. */
const money = (v: number) => (v > 0 ? `${v} ₽` : v < 0 ? `долг ${-v} ₽` : '0 ₽')

/** Правило знаков для x + y — словами, с числами из картинки. */
function rule(x: number, y: number): string {
  if (y === 0) return 'Прибавить ноль — число не меняется.'
  if (x === 0) return `Старт в нуле — приземляемся прямо в ${fmt(y)}.`
  if (x > 0 && y > 0) return `Оба числа положительные: ${x} + ${y} = ${x + y}.`
  if (x < 0 && y < 0) return `Знаки одинаковые (оба минус): складываем модули ${-x} + ${-y} = ${-x - y}, знак общий — минус.`
  if (Math.abs(x) === Math.abs(y)) return `Числа ${fmt(x)} и ${fmt(y)} противоположные — их сумма равна нулю.`
  const big = Math.abs(x) > Math.abs(y) ? x : y
  const hi = Math.max(Math.abs(x), Math.abs(y))
  const lo = Math.min(Math.abs(x), Math.abs(y))
  return `Знаки разные: из большего модуля вычитаем меньший: ${hi} − ${lo} = ${hi - lo}. Модуль больше у ${fmt(big)}, поэтому знак «${big > 0 ? '+' : '−'}».`
}

/** Сложение и вычитание прыжками по прямой. preset="sub" — с переключателем «+ / −»: вычитание заменяется прибавлением противоположного. */
export function JumpsViz({ preset }: { preset?: string }) {
  const sub = preset === 'sub'
  const presets = sub ? SUB : ADD
  const [[a, b], setAB] = useState<[number, number]>(presets[0])
  const [op, setOp] = useState<Op>(sub ? '-' : '+')
  const sgn = op === '+' ? 1 : -1
  const jump = sgn * b
  const res = a + jump
  // числа на кнопках до 10 по модулю, ответ остаётся на прямой (от −12 до 12)
  const range = (o: Op, start: number): [number, number] =>
    o === '+' ? [Math.max(-LIM, MIN - start), Math.min(LIM, MAX - start)] : [Math.max(-LIM, start - MAX), Math.min(LIM, start - MIN)]
  const [bMin, bMax] = range(op, a)
  const aMin = Math.max(-LIM, MIN - jump)
  const aMax = Math.min(LIM, MAX - jump)
  const switchOp = (o: Op) => {
    const [lo, hi] = range(o, a)
    setOp(o)
    setAB([a, clamp(b, lo, hi)])
  }

  // дуга прыжка
  const x1 = px(a)
  const x2 = px(res)
  const h = Math.min(50, 14 + 3.4 * Math.abs(jump))
  const top = Y - 6 - h
  const cy = Y - 6 - 2 * h
  const mid = (x1 + x2) / 2
  const dir = jump > 0 ? 'right' : 'left'
  const ang = Math.atan2(Y - 6 - cy, x2 - mid)
  const head = (len: number, spread: number) =>
    [
      [x2, Y - 6],
      [x2 - len * Math.cos(ang - spread), Y - 6 - len * Math.sin(ang - spread)],
      [x2 - len * Math.cos(ang + spread), Y - 6 - len * Math.sin(ang + spread)],
    ]
      .map((p) => p.map((v) => v.toFixed(1)).join(','))
      .join(' ')

  // подписи под прямой: старт и финиш жирным, обычные чётные — если не мешают
  const specials = res === a ? [a] : [a, res]
  const rowOf = (v: number) => (v === res && res !== a && Math.abs(res - a) < 2 ? 1 : 0)
  const ticks = Array.from({ length: MAX - MIN + 1 }, (_, i) => MIN + i)

  const calc = op === '+' ? `${tex(a)}+${tex(b, true)}=${res}` : `${tex(a)}-${tex(b, true)}=${tex(a)}+${tex(-b, true)}=${res}`
  const jumpText =
    op === '+'
      ? b > 0
        ? `Прибавляем положительное число ${b} — прыгаем на ${b} вправо.`
        : b < 0
          ? `Прибавляем отрицательное число ${fmt(b)} — прыгаем на ${-b} влево.`
          : 'Прибавляем 0 — стоим на месте.'
      : b !== 0
        ? `Вычесть ${fmt(b)} — то же, что прибавить противоположное число ${fmt(-b)}: прыгаем на ${Math.abs(b)} ${-b > 0 ? 'вправо' : 'влево'}.`
        : 'Вычесть 0 — стоим на месте.'
  const action =
    op === '+'
      ? b > 0
        ? `получил ${b} ₽`
        : b < 0
          ? `потратил ${-b} ₽`
          : 'ничего не изменилось'
      : b > 0
        ? `вычитаем ${b}: потратил ${b} ₽`
        : b < 0
          ? `вычитаем долг: у тебя забрали долг ${-b} ₽`
          : 'ничего не изменилось'

  return (
    <div className="viz">
      <div className="viz-title">{sub ? 'Вычитание — это прыжок к противоположному числу' : 'Сложение — прыжки по прямой'}</div>
      {sub && (
        <div className="chips jv-ops" role="group" aria-label="Действие">
          <button className={`chip wide ${op === '+' ? 'on' : ''}`} aria-pressed={op === '+'} onClick={() => switchOp('+')}>
            сложение «+»
          </button>
          <button className={`chip wide ${op === '-' ? 'on' : ''}`} aria-pressed={op === '-'} onClick={() => switchOp('-')}>
            вычитание «−»
          </button>
        </div>
      )}
      <div className="chips">
        {presets.map(([p, q], i) => {
          const o: Op = sub ? '-' : '+'
          return (
            <button
              key={i}
              className={`chip wide ${p === a && q === b && op === o ? 'on' : ''}`}
              onClick={() => {
                setOp(o)
                setAB([p, q])
              }}
            >
              <Tex tex={`${tex(p)}${o}${tex(q, true)}`} />
            </button>
          )
        })}
      </div>
      <div className="steppers">
        <Stepper label="старт" value={a} min={aMin} max={aMax} step={1} onChange={(v) => setAB([v, b])} />
        <Stepper label={op === '+' ? 'прибавляем' : 'вычитаем'} value={b} min={bMin} max={bMax} step={1} onChange={(v) => setAB([a, v])} />
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="numline" role="img" aria-label={`Числовая прямая: старт в ${fmt(a)}, прыжок на ${Math.abs(jump)} ${jump >= 0 ? 'вправо' : 'влево'}, приземление в ${fmt(res)}`}>
        <rect x={px(MIN)} y={8} width={px(0) - px(MIN)} height={Y - 4} className="jv-zone neg" />
        <rect x={px(0)} y={8} width={px(MAX) - px(0)} height={Y - 4} className="jv-zone pos" />
        <text x={px(MIN) + 2} y={22} className="jv-zone-label">
          минус
        </text>
        <text x={px(MAX) - 2} y={22} textAnchor="end" className="jv-zone-label">
          плюс
        </text>
        <line x1={PAD - 8} x2={W - PAD + 8} y1={Y} y2={Y} stroke="currentColor" strokeWidth={2} opacity={0.65} />
        {ticks.map((t) => (
          <line key={t} x1={px(t)} x2={px(t)} y1={Y - (t === 0 ? 8 : 4)} y2={Y + (t === 0 ? 8 : 4)} stroke="currentColor" opacity={t === 0 ? 0.9 : 0.5} strokeWidth={t === 0 ? 2 : 1} />
        ))}
        {ticks
          .filter((t) => t % 2 === 0 && specials.every((s) => s === t || Math.abs(s - t) >= 2))
          .filter((t) => !specials.includes(t))
          .map((t) => (
            <text key={t} x={px(t)} y={Y + 21} textAnchor="middle" className="jv-label">
              {fmt(t)}
            </text>
          ))}
        {specials.map((s) => (
          <text key={s} x={px(s)} y={Y + 21 + 15 * rowOf(s)} textAnchor="middle" className={`jv-label special ${s === res ? 'land' : ''}`}>
            {fmt(s)}
          </text>
        ))}
        {jump !== 0 && (
          <>
            <path d={`M${x1.toFixed(1)} ${Y - 6} Q${mid.toFixed(1)} ${cy.toFixed(1)} ${x2.toFixed(1)} ${Y - 6}`} className={`jv-arc ${dir}`} />
            <polygon points={head(10, 0.45)} className={`jv-head ${dir}`} />
            <text x={mid} y={top - 6} textAnchor="middle" className={`jv-jump ${dir}`}>
              {jump > 0 ? `+${jump}` : fmt(jump)}
            </text>
          </>
        )}
        <circle cx={x1} cy={Y} r={6} className="jv-start" />
        <circle cx={x2} cy={Y} r={jump === 0 ? 4 : 7} className="jv-land" />
      </svg>
      <div className="readout" aria-live="polite">
        <div className="viz-calc">
          <Tex tex={calc} />
        </div>
        <div>
          Стоим в {fmt(a)}. {jumpText} Приземлились в {fmt(res)}.
        </div>
        <div className="muted">{rule(a, jump)}</div>
        <div className="jv-wallet">
          💰 Кошелёк: сначала {money(a)}, {action} — теперь {money(res)}.
        </div>
      </div>
    </div>
  )
}
