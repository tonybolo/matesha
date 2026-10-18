import { useState, type MouseEvent } from 'react'
import { Tex } from '../components/Tex'
import { Stepper } from './Stepper'
import './OppositesViz.css'

const MIN = -8
const MAX = 8
const STEP = 0.5
const W = 340
const PAD = 18
const px = (v: number) => PAD + ((v - MIN) / (MAX - MIN)) * (W - 2 * PAD)
const clamp = (v: number) => Math.max(MIN, Math.min(MAX, v))
/** −2,5 для подписей; -2{,}5 и \left(-2{,}5\right) для формул. */
const fmt = (v: number) => (v < 0 ? '−' : '') + String(Math.abs(v)).replace('.', ',')
const tn = (v: number) => String(v).replace('.', '{,}')
const tw = (v: number) => (v < 0 ? `\\left(${tn(v)}\\right)` : tn(v))
const frTex = (v: number) => {
  // число шагом 0,5 — дробью: 2,5 = 5/2, −4 = −4/1
  const n = Math.round(v * 2)
  return n % 2 === 0 ? `\\frac{${n / 2}}{1}` : `${n < 0 ? '-' : ''}\\frac{${Math.abs(n)}}{2}`
}
const stepsWord = (n: number) => {
  if (!Number.isInteger(n)) return 'шага'
  const k = Math.abs(n)
  if (k % 10 === 1 && k % 100 !== 11) return 'шаг'
  if ([2, 3, 4].includes(k % 10) && ![12, 13, 14].includes(k % 100)) return 'шага'
  return 'шагов'
}
const steps = (n: number) => `${fmt(n)} ${stepsWord(n)}`

/** Нажатие на прямую ставит число в это место (с точностью до 0,5). */
function tapValue(e: MouseEvent<SVGSVGElement>): number {
  const r = e.currentTarget.getBoundingClientRect()
  const x = ((e.clientX - r.left) / r.width) * W
  return clamp(Math.round((MIN + ((x - PAD) / (W - 2 * PAD)) * (MAX - MIN)) / STEP) * STEP)
}

type Mark = { v: number; cls: string; label?: string }

/** Ось от −8 до 8: деления, подписи чётных чисел; выбранные точки подписаны жирно и не налезают друг на друга. */
function Axis({ y, marks }: { y: number; marks: Mark[] }) {
  const ticks = Array.from({ length: MAX - MIN + 1 }, (_, i) => MIN + i)
  const sorted = [...marks].sort((p, q) => p.v - q.v)
  const rows: number[] = []
  const lastX: number[] = []
  for (const m of sorted) {
    let row = 0
    while (lastX[row] !== undefined && px(m.v) - lastX[row] < 30) row++
    lastX[row] = px(m.v)
    rows.push(row)
  }
  const free = (t: number) => sorted.every((m) => Math.abs(px(m.v) - px(t)) >= 26)
  return (
    <>
      <line x1={PAD - 10} x2={W - PAD + 10} y1={y} y2={y} stroke="currentColor" strokeWidth={2} opacity={0.65} />
      {ticks.map((t) => (
        <line key={t} x1={px(t)} x2={px(t)} y1={y - (t === 0 ? 8 : 4)} y2={y + (t === 0 ? 8 : 4)} stroke="currentColor" opacity={t === 0 ? 0.9 : 0.5} strokeWidth={t === 0 ? 2 : 1} />
      ))}
      {ticks
        .filter((t) => t % 2 === 0 && free(t))
        .map((t) => (
          <text key={t} x={px(t)} y={y + 21} textAnchor="middle" className="ov-label">
            {fmt(t)}
          </text>
        ))}
      {sorted.map((m, i) => (
        <text key={`${m.cls}-${i}`} x={Math.max(14, Math.min(W - 14, px(m.v)))} y={y + 21 + 15 * rows[i]} textAnchor="middle" className={`ov-label strong ${m.cls}`}>
          {m.label ?? fmt(m.v)}
        </text>
      ))}
    </>
  )
}

function Chips<T>({ items, on, pick, tex }: { items: T[]; on: (t: T) => boolean; pick: (t: T) => void; tex: (t: T) => string }) {
  return (
    <div className="chips">
      {items.map((it, i) => (
        <button key={i} className={`chip wide ${on(it) ? 'on' : ''}`} onClick={() => pick(it)}>
          <Tex tex={tex(it)} />
        </button>
      ))}
    </div>
  )
}

// ---------- шаг 1: где живёт число ----------

function LineMode() {
  const [a, setA] = useState(-4)
  const where = a === 0 ? 'ноль' : a > 0 ? 'положительное' : 'отрицательное'
  return (
    <div className="viz">
      <div className="viz-title">Где стоит число на прямой</div>
      <Chips items={[-4, 2.5, -0.5, 6]} on={(v) => v === a} pick={setA} tex={(v) => (v === -0.5 ? '-\\frac{1}{2}' : tn(v))} />
      <div className="steppers">
        <Stepper label="число" value={a} min={MIN} max={MAX} step={STEP} onChange={setA} />
      </div>
      <svg viewBox={`0 0 ${W} 104`} className="numline tappable" role="img" aria-label={`Числовая прямая, отмечено число ${fmt(a)}. Нажми на прямую, чтобы выбрать другое`} onClick={(e) => setA(tapValue(e))}>
        <rect x={px(MIN)} y={8} width={px(0) - px(MIN)} height={58} className="ov-zone neg" />
        <rect x={px(0)} y={8} width={px(MAX) - px(0)} height={58} className="ov-zone pos" />
        <text x={px(MIN) + 2} y={22} className="ov-zone-label">
          минус: холодно, долг
        </text>
        <text x={px(MAX) - 2} y={22} textAnchor="end" className="ov-zone-label">
          плюс: тепло
        </text>
        {a !== 0 && <line x1={px(0)} x2={px(a)} y1={50} y2={50} className={`ov-walk ${a > 0 ? 'pos' : 'neg'}`} />}
        {a !== 0 && (
          <text x={(px(0) + px(a)) / 2} y={42} textAnchor="middle" className="ov-label strong">
            {steps(Math.abs(a))} {a > 0 ? 'вправо' : 'влево'}
          </text>
        )}
        <Axis y={66} marks={[{ v: a, cls: 'a' }]} />
        <circle cx={px(a)} cy={66} r={7} className="ov-pt a" />
      </svg>
      <div className="readout" aria-live="polite">
        <div>
          <strong>{fmt(a)}</strong> —{' '}
          {a === 0
            ? 'ноль: граница, ни положительное, ни отрицательное число. 0° — вода замерзает; 0 ₽ — ни денег, ни долга.'
            : a > 0
              ? `${where} число: от нуля ${steps(a)} вправо. Как +${fmt(a)}° на градуснике или ${fmt(a)} ₽ в кошельке.`
              : `${where} число: от нуля ${steps(-a)} влево. Как ${fmt(a)}° на градуснике (мороз) или долг ${fmt(-a)} ₽.`}
        </div>
        <div className="viz-calc">
          <Tex tex={`${tn(a)}=${frTex(a)}`} />
        </div>
        <div className="muted">Его можно записать дробью — значит, это рациональное число.</div>
      </div>
    </div>
  )
}

// ---------- шаг 2: зеркало, противоположные числа, модуль ----------

function MirrorMode() {
  const [a, setA] = useState(-5)
  const d = Math.abs(a)
  const y = 70
  const brace = (v: number, cls: string) => (v === 0 ? null : <path d={`M${px(0)} ${y - 22} V${y - 28} H${px(v)} V${y - 22}`} className={`ov-brace ${cls}`} />)
  return (
    <div className="viz">
      <div className="viz-title">Зеркало в нуле: противоположные числа</div>
      <Chips items={[-5, 3, 2.5, 0]} on={(v) => v === a} pick={setA} tex={tn} />
      <div className="steppers">
        <Stepper label="число" value={a} min={MIN} max={MAX} step={STEP} onChange={setA} />
        <button className="btn small" onClick={() => setA(-a)} disabled={a === 0}>
          🪞 Отразить
        </button>
      </div>
      <svg viewBox={`0 0 ${W} 110`} className="numline tappable" role="img" aria-label={`Число ${fmt(a)} и противоположное ему ${fmt(-a)}: до нуля ${steps(d)}`} onClick={(e) => setA(tapValue(e))}>
        <line x1={px(0)} x2={px(0)} y1={20} y2={y + 6} className="ov-mirror" />
        <text x={px(0)} y={14} textAnchor="middle" className="ov-label muted-text">
          зеркало
        </text>
        {brace(a, 'a')}
        {brace(-a, 'b')}
        {a !== 0 && (
          <>
            <text x={(px(0) + px(a)) / 2} y={y - 33} textAnchor="middle" className="ov-label strong a">
              {fmt(d)}
            </text>
            <text x={(px(0) + px(-a)) / 2} y={y - 33} textAnchor="middle" className="ov-label strong b">
              {fmt(d)}
            </text>
          </>
        )}
        <Axis y={y} marks={a === 0 ? [{ v: 0, cls: 'a' }] : [{ v: a, cls: 'a' }, { v: -a, cls: 'b' }]} />
        {a !== 0 && <circle cx={px(-a)} cy={y} r={7} className="ov-pt b" />}
        <circle cx={px(a)} cy={y} r={7} className="ov-pt a" />
      </svg>
      <div className="readout" aria-live="polite">
        {a === 0 ? (
          <>
            <div>Ноль — сам себе противоположный: отражение нуля — снова ноль.</div>
            <div className="viz-calc">
              <Tex tex="-0=0,\qquad \left|0\right|=0" />
            </div>
          </>
        ) : (
          <>
            <div>
              Числа {fmt(a)} и {fmt(-a)} противоположные: они по разные стороны от нуля, и до нуля от каждого {steps(d)}.
            </div>
            <div className="viz-calc">
              <Tex tex={`-\\left(${tn(a)}\\right)=${tn(-a)}`} />
            </div>
            <div className="viz-calc">
              <Tex tex={`\\left|${tn(a)}\\right|=\\left|${tn(-a)}\\right|=${tn(d)}`} />
            </div>
            <div className="muted">Модуль — это расстояние до нуля, поэтому у противоположных чисел модули одинаковые.</div>
          </>
        )}
      </div>
    </div>
  )
}

// ---------- шаг 2: правее — больше ----------

function CompareMode() {
  const [[a, b], setAB] = useState<[number, number]>([-2, -5])
  const rel = a > b ? '>' : a < b ? '<' : '='
  const hi = a > b ? a : b
  const lo = a > b ? b : a
  const y = 64
  let why: string
  if (a === b) why = 'Это одна и та же точка — числа равны.'
  else if (hi < 0) why = `Оба числа отрицательные. Модуль у ${fmt(lo)} больше (${fmt(-lo)} > ${fmt(-hi)}), но само число меньше: оно дальше от нуля влево. Мороз ${fmt(lo)}° холоднее, чем ${fmt(hi)}°.`
  else if (hi === 0) why = 'Ноль больше любого отрицательного числа.'
  else if (lo === 0) why = 'Любое положительное число больше нуля.'
  else if (lo < 0) why = 'Любое положительное число больше любого отрицательного.'
  else why = 'Оба числа положительные: больше то, которое дальше от нуля.'
  return (
    <div className="viz">
      <div className="viz-title">Правее — больше</div>
      <Chips<[number, number]>
        items={[
          [-2, -5],
          [-0.5, -3],
          [0, -4],
          [2, -6],
        ]}
        on={([p, q]) => p === a && q === b}
        pick={(v) => setAB(v)}
        tex={([p, q]) => `${tn(p)}\\ \\text{и}\\ {${tn(q)}}`}
      />
      <div className="steppers">
        <Stepper label="a" value={a} min={MIN} max={MAX} step={STEP} onChange={(v) => setAB([v, b])} />
        <Stepper label="b" value={b} min={MIN} max={MAX} step={STEP} onChange={(v) => setAB([a, v])} />
      </div>
      <svg viewBox={`0 0 ${W} 100`} className="numline" role="img" aria-label={`Числа a = ${fmt(a)} и b = ${fmt(b)}: ${a === b ? 'равны' : `больше ${fmt(hi)}`}`}>
        {a !== b && (
          <text x={Math.max(30, Math.min(W - 30, px(hi)))} y={y - 22} textAnchor="middle" className="ov-label strong ok">
            больше ▾
          </text>
        )}
        <text x={px(MIN)} y={16} className="ov-label muted-text">
          ◂ меньше
        </text>
        <text x={px(MAX)} y={16} textAnchor="end" className="ov-label muted-text">
          больше ▸
        </text>
        <Axis
          y={y}
          marks={
            a === b
              ? [{ v: a, cls: 'a', label: `a = b = ${fmt(a)}` }]
              : [
                  { v: a, cls: 'a', label: `a = ${fmt(a)}` },
                  { v: b, cls: 'b', label: `b = ${fmt(b)}` },
                ]
          }
        />
        <circle cx={px(b)} cy={y} r={7} className="ov-pt b" />
        <circle cx={px(a)} cy={y} r={a === b ? 5 : 7} className="ov-pt a" />
      </svg>
      <div className="readout" aria-live="polite">
        <div className="viz-calc">
          <Tex tex={`${tn(a)}${rel}${tn(b)}`} />
        </div>
        <div>{a === b ? 'Числа равны.' : `${fmt(hi)} правее, чем ${fmt(lo)}, значит, ${fmt(hi)} больше.`}</div>
        <div className="muted">{why}</div>
      </div>
    </div>
  )
}

// ---------- ⭐ шаг 8: расстояние между точками ----------

function DistanceMode() {
  const [[a, b], setAB] = useState<[number, number]>([-2, 3])
  const d = Math.abs(a - b)
  const lo = Math.min(a, b)
  const hi = Math.max(a, b)
  const y = 66
  const units = Array.from({ length: Math.floor(d) + 1 }, (_, i) => lo + i)
  return (
    <div className="viz">
      <div className="viz-title">Расстояние между точками — модуль разности</div>
      <Chips<[number, number]>
        items={[
          [-2, 3],
          [-6, -1],
          [1, 7],
          [-4, 4],
        ]}
        on={([p, q]) => p === a && q === b}
        pick={(v) => setAB(v)}
        tex={([p, q]) => `${tn(p)}\\ \\text{и}\\ {${tn(q)}}`}
      />
      <div className="steppers">
        <Stepper label="a" value={a} min={MIN} max={MAX} step={STEP} onChange={(v) => setAB([v, b])} />
        <Stepper label="b" value={b} min={MIN} max={MAX} step={STEP} onChange={(v) => setAB([a, v])} />
      </div>
      <svg viewBox={`0 0 ${W} 102`} className="numline" role="img" aria-label={`Точки ${fmt(a)} и ${fmt(b)}, расстояние между ними ${steps(d)}`}>
        {d > 0 && <line x1={px(lo)} x2={px(hi)} y1={y} y2={y} className="ov-seg" />}
        {units.map((u) => (
          <circle key={u} cx={px(u)} cy={y - 14} r={2.5} className="ov-dot" />
        ))}
        {d > 0 && (
          <text x={(px(lo) + px(hi)) / 2} y={y - 24} textAnchor="middle" className="ov-label strong ok">
            {steps(d)}
          </text>
        )}
        <Axis
          y={y}
          marks={
            a === b
              ? [{ v: a, cls: 'a', label: `a = b` }]
              : [
                  { v: a, cls: 'a', label: `a = ${fmt(a)}` },
                  { v: b, cls: 'b', label: `b = ${fmt(b)}` },
                ]
          }
        />
        <circle cx={px(b)} cy={y} r={7} className="ov-pt b" />
        <circle cx={px(a)} cy={y} r={a === b ? 5 : 7} className="ov-pt a" />
      </svg>
      <div className="readout" aria-live="polite">
        <div className="viz-calc">
          <Tex tex={`|a-b|=\\left|${tn(a)}-${tw(b)}\\right|=\\left|${tn(a - b)}\\right|=${tn(d)}`} />
        </div>
        <div className="viz-calc">
          <Tex tex={`|b-a|=\\left|${tn(b)}-${tw(a)}\\right|=\\left|${tn(b - a)}\\right|=${tn(d)}`} />
        </div>
        <div>
          {d === 0
            ? 'Точки совпали — расстояние равно нулю.'
            : `Между точками ${fmt(a)} и ${fmt(b)} — ${steps(d)}. Порядок вычитания не важен: модуль убирает минус.`}
        </div>
      </div>
    </div>
  )
}

/** Числовая прямая для темы «Рациональные числа». preset: line — где стоит число; (по умолчанию) — зеркало и модуль; compare — правее больше; distance — расстояние |a − b|. */
export function OppositesViz({ preset }: { preset?: string }) {
  if (preset === 'line') return <LineMode />
  if (preset === 'compare') return <CompareMode />
  if (preset === 'distance') return <DistanceMode />
  return <MirrorMode />
}
