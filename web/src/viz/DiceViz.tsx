import { useMemo, useState } from 'react'
import { Tex } from '../components/Tex'
import './DiceViz.css'

const MAX_ROLLS = 10000
const W = 340
const fmt = (v: number, digits = 2) => String(Math.round(v * 10 ** digits) / 10 ** digits).replace('.', ',').replace('-', '−')
const timesWord = (n: number) => (n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14) ? 'раза' : 'раз')

/** Псевдослучайный бросок номер i в серии seed: одно и то же число при каждом запуске (перемешивание битов, как в murmur3). */
function rollAt(seed: number, i: number): number {
  let h = (Math.imul(seed, 0x9e3779b1) ^ Math.imul(i + 1, 0x85ebca6b)) >>> 0
  h = Math.imul(h ^ (h >>> 16), 0x7feb352d) >>> 0
  h = Math.imul(h ^ (h >>> 15), 0x846ca68b) >>> 0
  h = (h ^ (h >>> 16)) >>> 0
  return 1 + Math.floor((h / 4294967296) * 6)
}

const PIPS: Record<number, [number, number][]> = {
  1: [[2, 2]],
  2: [[1, 1], [3, 3]],
  3: [[1, 1], [2, 2], [3, 3]],
  4: [[1, 1], [3, 1], [1, 3], [3, 3]],
  5: [[1, 1], [3, 1], [2, 2], [1, 3], [3, 3]],
  6: [[1, 1], [3, 1], [1, 2], [3, 2], [1, 3], [3, 3]],
}

function Die({ v, x, size, fresh }: { v: number; x: number; size: number; fresh: boolean }) {
  const c = size / 4
  return (
    <g transform={`translate(${x} 4)`}>
      <rect width={size} height={size} rx={6} className={`dice-face ${fresh ? 'fresh' : ''}`} />
      {PIPS[v].map(([i, j], k) => (
        <circle key={k} cx={i * c} cy={j * c} r={size / 11} className="dice-pip" />
      ))}
    </g>
  )
}

/** Кубик: бросаем 1, 10, 100, 1000 раз и смотрим, как среднее выпавших очков подбирается к E(X) = 3,5. */
export function DiceViz() {
  const [seed, setSeed] = useState(1)
  const [n, setN] = useState(0)
  const { rolls, counts, sum, path } = useMemo(() => {
    const rolls = Array.from({ length: n }, (_, i) => rollAt(seed, i))
    const counts = [0, 0, 0, 0, 0, 0]
    const path: { k: number; m: number }[] = []
    let s = 0
    let next = 1
    rolls.forEach((r, i) => {
      counts[r - 1]++
      s += r
      const k = i + 1
      if (k === next || k === n) {
        path.push({ k, m: s / k })
        next = k < 20 ? k + 1 : Math.ceil(k * 1.04)
      }
    })
    return { rolls, counts, sum: s, path }
  }, [seed, n])
  const mean = n ? sum / n : 0
  const add = (k: number) => setN((v) => Math.min(MAX_ROLLS, v + k))

  // график среднего: по горизонтали — число бросков (1, 10, 100, 1000, 10 000 через равные шаги), по вертикали — от 1 до 6
  const GH = 158
  const gx = (k: number) => 30 + (Math.log10(k) / 4) * (W - 60)
  const gy = (m: number) => 12 + ((6 - m) / 5) * (GH - 48)
  const last = rolls.slice(-8)
  const maxC = Math.max(1, ...counts)

  return (
    <div className="viz">
      <div className="viz-title">Бросаем кубик много раз: куда идёт среднее?</div>
      <div className="viz-actions dice-actions">
        <button className="btn small primary" onClick={() => add(1)} disabled={n >= MAX_ROLLS}>
          🎲 Бросить
        </button>
        <button className="btn small" onClick={() => add(10)} disabled={n >= MAX_ROLLS}>
          +10
        </button>
        <button className="btn small" onClick={() => add(100)} disabled={n >= MAX_ROLLS}>
          +100
        </button>
        <button className="btn small" onClick={() => add(1000)} disabled={n >= MAX_ROLLS}>
          +1000
        </button>
        <button className="btn small ghost" onClick={() => setN(0)} disabled={n === 0}>
          ↺ Сначала
        </button>
        <button
          className="btn small ghost"
          onClick={() => {
            setSeed((v) => v + 1)
            setN(0)
          }}
        >
          Другая серия
        </button>
      </div>

      <svg viewBox={`0 0 ${W} 44`} className="dice-svg" role="img" aria-label={last.length ? `Последние броски: ${last.join(', ')}` : 'Бросков пока нет'}>
        {last.length === 0 ? (
          <text x={W / 2} y={28} className="dice-empty">
            Бросков пока нет — нажми «Бросить»
          </text>
        ) : (
          last.map((v, i) => <Die key={n - last.length + i} v={v} x={6 + i * 41} size={36} fresh={i === last.length - 1} />)
        )}
      </svg>

      <svg viewBox={`0 0 ${W} 112`} className="dice-svg" role="img" aria-label={`Сколько раз выпало: ${counts.map((c, i) => `${i + 1} — ${c}`).join(', ')}`}>
        {counts.map((c, i) => {
          const h = (c / maxC) * 66
          const x = 22 + i * 52
          return (
            <g key={i}>
              <rect x={x} y={84 - h} width={36} height={h} className="dice-bar" />
              <text x={x + 18} y={Math.max(14, 80 - h)} className="dice-count">
                {c}
              </text>
              <text x={x + 18} y={102} className="dice-face-label">
                {i + 1}
              </text>
            </g>
          )
        })}
        <line x1={14} x2={W - 14} y1={84} y2={84} className="axis" />
      </svg>

      <svg viewBox={`0 0 ${W} ${GH}`} className="dice-svg" role="img" aria-label={`Среднее после ${n} бросков: ${fmt(mean)}; ожидание 3,5`}>
        {[1, 2, 3, 4, 5, 6].map((m) => (
          <g key={m}>
            <line x1={30} x2={W - 14} y1={gy(m)} y2={gy(m)} className="grid" />
            <text x={24} y={gy(m) + 4} className="dice-tick" textAnchor="end">
              {m}
            </text>
          </g>
        ))}
        {[1, 10, 100, 1000, 10000].map((k) => (
          <g key={k}>
            <line x1={gx(k)} x2={gx(k)} y1={gy(6)} y2={gy(1)} className="grid" />
            <text x={gx(k)} y={GH - 20} className="dice-tick" textAnchor="middle">
              {k === 10000 ? '10 000' : k}
            </text>
          </g>
        ))}
        <text x={(gx(1) + gx(10000)) / 2} y={GH - 4} className="dice-tick" textAnchor="middle">
          число бросков (каждое деление — в 10 раз больше)
        </text>
        <line x1={30} x2={W - 14} y1={gy(3.5)} y2={gy(3.5)} className="dice-e" />
        <text x={W - 16} y={gy(3.5) - 5} className="dice-elabel" textAnchor="end">
          E = 3,5
        </text>
        {path.length > 1 && <polyline points={path.map((p) => `${gx(p.k).toFixed(1)},${gy(p.m).toFixed(1)}`).join(' ')} className="dice-line" />}
        {n > 0 && <circle cx={gx(n)} cy={gy(mean)} r={5} className="dice-now" />}
      </svg>

      <div className="readout" aria-live="polite">
        {n === 0 ? (
          <>Нажми «Бросить» или «+100». Будем следить за средним числом очков.</>
        ) : (
          <>
            <div>
              Бросков: <strong>{n}</strong>. Сумма очков: {sum}. Среднее: <Tex tex={`${sum}:${n}${Math.abs(mean * 100 - Math.round(mean * 100)) < 1e-9 ? '=' : '\\approx '}${fmt(mean, 2).replace(',', '{,}')}`} />.
            </div>
            <div>
              {n === 1
                ? `Выпало ${rolls[0]}. Один бросок может быть каким угодно — пока рано делать выводы.`
                : `До E(X) = 3,5 сейчас ${fmt(Math.abs(mean - 3.5))}. ${n < 100 ? 'Пока среднее сильно скачет: бросков мало.' : 'Чем больше бросков, тем ближе среднее к 3,5 — это закон больших чисел.'}`}
            </div>
            <div className="muted">
              Каждое число ждём примерно в каждом шестом броске — около {fmt(n / 6, 0)} {timesWord(Math.round(n / 6))}. Вышло: {counts.map((c, i) => `«${i + 1}» — ${c}`).join(', ')}.
            </div>
          </>
        )}
      </div>
    </div>
  )
}
