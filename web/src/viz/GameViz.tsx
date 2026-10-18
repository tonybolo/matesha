import { useMemo, useState } from 'react'
import { Tex } from '../components/Tex'
import { Stepper } from './Stepper'
import './GameViz.css'

const N = 100
const CELL = 22
const GAP = 3
const OFF = 20
const fmt = (v: number) => String(Math.round(v * 100) / 100).replace('.', ',').replace('-', '−')
const signed = (v: number) => (v > 0 ? `+${fmt(v)}` : fmt(v))
const ticketsWord = (n: number) => (n % 10 === 1 && n % 100 !== 11 ? 'билет' : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14) ? 'билета' : 'билетов')

/** Перемешивание битов (как в murmur3): одинаковый результат при каждом запуске. */
function hash(a: number, b: number): number {
  let h = (Math.imul(a + 0x632be5ab, 0x9e3779b1) ^ Math.imul(b + 1, 0x85ebca6b)) >>> 0
  h = Math.imul(h ^ (h >>> 16), 0x7feb352d) >>> 0
  h = Math.imul(h ^ (h >>> 15), 0x846ca68b) >>> 0
  return (h ^ (h >>> 16)) >>> 0
}

// где на «листе» лежат выигрышные билеты: постоянная перестановка 0..99
const PLACE = Array.from({ length: N }, (_, i) => i).sort((a, b) => hash(3, a) - hash(3, b))

type Lottery = { title: string; big: number; nb: number; small: number; ns: number; price: number }
const LOTTERIES: Lottery[] = [
  { title: '1 × 500 и 5 × 100', big: 500, nb: 1, small: 100, ns: 5, price: 15 },
  { title: '2 × 200 и 10 × 30', big: 200, nb: 2, small: 30, ns: 10, price: 7 },
  { title: '20 × 50', big: 500, nb: 0, small: 50, ns: 20, price: 10 },
]

/** Лотерея из 100 билетов: средний выигрыш на билет — это E(X), справедливая цена билета. */
export function GameViz() {
  const [li, setLi] = useState(0)
  const [nb, setNb] = useState(LOTTERIES[0].nb)
  const [ns, setNs] = useState(LOTTERIES[0].ns)
  const [price, setPrice] = useState(LOTTERIES[0].price)
  const [bought, setBought] = useState(0)
  const L = LOTTERIES[li]
  const prizeAt = (pos: number) => {
    const k = PLACE.indexOf(pos)
    return k < nb ? L.big : k < nb + ns ? L.small : 0
  }
  const fund = nb * L.big + ns * L.small
  const E = fund / N
  const diff = price - E
  const { won, last } = useMemo(() => {
    let w = 0
    let lastPos = -1
    for (let j = 0; j < bought; j++) {
      lastPos = hash(7, j) % N
      const k = PLACE.indexOf(lastPos)
      w += k < nb ? L.big : k < nb + ns ? L.small : 0
    }
    return { won: w, last: lastPos }
  }, [bought, nb, ns, L])
  const spent = bought * price
  const choose = (i: number) => {
    setLi(i)
    setNb(LOTTERIES[i].nb)
    setNs(LOTTERIES[i].ns)
    setPrice(LOTTERIES[i].price)
    setBought(0)
  }
  const fundParts = [nb ? `${nb}\\cdot ${L.big}` : '', ns ? `${ns}\\cdot ${L.small}` : ''].filter(Boolean).join('+') || '0'

  return (
    <div className="viz">
      <div className="viz-title">Лотерея из 100 билетов: какая цена честная?</div>
      <div className="chips">
        {LOTTERIES.map((l, i) => (
          <button key={l.title} className={`chip wide ${i === li ? 'on' : ''}`} onClick={() => choose(i)}>
            {l.title}
          </button>
        ))}
      </div>
      <svg viewBox={`0 0 ${2 * OFF + 10 * CELL + 9 * GAP} ${10 * CELL + 9 * GAP + 8}`} className="game-svg" role="img" aria-label={`100 билетов: ${nb} по ${L.big} руб., ${ns} по ${L.small} руб., остальные пустые`}>
        {Array.from({ length: N }, (_, pos) => {
          const p = prizeAt(pos)
          const x = OFF + (pos % 10) * (CELL + GAP)
          const y = 4 + Math.floor(pos / 10) * (CELL + GAP)
          return <rect key={pos} x={x} y={y} width={CELL} height={CELL} rx={4} className={`game-t ${p === L.big && nb ? 'big' : p ? 'small' : ''} ${pos === last ? 'last' : ''}`} />
        })}
      </svg>
      <div className="game-legend">
        {nb > 0 && (
          <span>
            <i className="game-key big" /> {L.big} руб. × {nb}
          </span>
        )}
        {ns > 0 && (
          <span>
            <i className="game-key small" /> {L.small} руб. × {ns}
          </span>
        )}
        <span>
          <i className="game-key" /> пусто × {N - nb - ns}
        </span>
      </div>
      <div className="steppers">
        <Stepper compact label={`призов по ${L.big}`} value={nb} min={0} max={5} step={1} onChange={(v) => { setNb(v); setBought(0) }} />
        <Stepper compact label={`призов по ${L.small}`} value={ns} min={0} max={30} step={1} onChange={(v) => { setNs(v); setBought(0) }} />
        <Stepper compact label="цена билета, руб." value={price} min={0} max={40} step={1} onChange={setPrice} />
      </div>
      <div className="viz-actions">
        <button className="btn small primary" onClick={() => setBought((b) => b + 1)}>
          Купить билет
        </button>
        <button className="btn small" onClick={() => setBought((b) => b + 10)}>
          +10 билетов
        </button>
        <button className="btn small" onClick={() => setBought((b) => b + 100)}>
          +100
        </button>
        <button className="btn small ghost" onClick={() => setBought(0)} disabled={bought === 0}>
          ↺ Сначала
        </button>
      </div>
      <div className={`readout ${Math.abs(diff) < 1e-9 ? '' : diff > 0 ? 'bad' : ''}`} aria-live="polite">
        <div>
          Все призы: <Tex tex={`${fundParts}=${fund}`} /> руб. на {N} билетов. В среднем на один билет приходится <Tex tex={`${fund}:${N}=${fmt(E).replace(',', '{,}')}`} /> руб. — это <Tex tex="E(X)" />, справедливая цена.
        </div>
        <div>
          <strong>
            {Math.abs(diff) < 1e-9
              ? `Билет стоит ${fmt(price)} руб. = E(X): игра справедливая, в среднем никто не в выигрыше и не в проигрыше.`
              : diff > 0
                ? `Билет стоит ${fmt(price)} руб. — дороже E(X) на ${fmt(diff)} руб.: игрок в среднем теряет ${fmt(diff)} руб. с каждого билета, выигрывает устроитель.`
                : `Билет стоит ${fmt(price)} руб. — дешевле E(X) на ${fmt(-diff)} руб.: в среднем игрок получает на ${fmt(-diff)} руб. больше, чем платит. Устроитель в убытке.`}
          </strong>
        </div>
        <div>
          {bought === 0
            ? 'Купи билеты и посмотри, что получится на деле.'
            : `Куплено ${bought} ${ticketsWord(bought)}: потрачено ${fmt(spent)} руб., выиграно ${fmt(won)} руб. Итог ${signed(won - spent)} руб., в среднем ${signed((won - spent) / bought)} руб. за билет (ожидание: ${signed(E - price)}).${bought < 100 ? ' Билетов пока мало, итог может сильно отличаться от ожидания.' : ''}`}
        </div>
      </div>
    </div>
  )
}
