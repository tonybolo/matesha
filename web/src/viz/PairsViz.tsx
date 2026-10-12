import { useMemo, useState } from 'react'
import { Tex } from '../components/Tex'

const NUMBERS = [72, 50, 180, 200, 1296]

function primeFactors(n: number): number[] {
  const out: number[] = []
  let m = n
  for (let p = 2; p * p <= m; p++) while (m % p === 0) (out.push(p), (m /= p))
  if (m > 1) out.push(m)
  return out
}

type Tile = { id: number; p: number; out: boolean }

/** Пары одинаковых множителей выходят из-под корня по одному. */
export function PairsViz() {
  const [n, setN] = useState(72)
  const base = useMemo(() => primeFactors(n).map((p, id) => ({ id, p, out: false })), [n])
  const [tiles, setTiles] = useState<Tile[]>(base)
  const [exited, setExited] = useState<number[]>([])
  const [sel, setSel] = useState<number | null>(null)
  const [msg, setMsg] = useState<string | null>(null)

  const reset = (m = n) => {
    setN(m)
    setTiles(primeFactors(m).map((p, id) => ({ id, p, out: false })))
    setExited([])
    setSel(null)
    setMsg(null)
  }

  const tap = (t: Tile) => {
    if (t.out) return
    if (sel === null) return setSel(t.id)
    if (sel === t.id) return setSel(null)
    const other = tiles.find((x) => x.id === sel)!
    if (other.p === t.p) {
      setTiles(tiles.map((x) => (x.id === sel || x.id === t.id ? { ...x, out: true } : x)))
      setExited([...exited, t.p])
      setMsg(`Пара ${t.p} и ${t.p} вышла из-под корня одним числом ${t.p}.`)
    } else setMsg('Нужны два одинаковых множителя.')
    setSel(null)
  }

  const inside = tiles.filter((t) => !t.out)
  const outside = exited.reduce((a, b) => a * b, 1)
  const rest = inside.reduce((a, t) => a * t.p, 1)
  const canPair = inside.some((t, i) => inside.some((u, j) => i !== j && u.p === t.p))
  const result = rest === 1 ? `${outside}` : outside === 1 ? `\\sqrt{${rest}}` : `${outside}\\sqrt{${rest}}`

  return (
    <div className="viz">
      <div className="viz-title">Пары выходят из-под корня</div>
      <div className="chips">
        {NUMBERS.map((v) => (
          <button key={v} className={`chip wide ${v === n ? 'on' : ''}`} onClick={() => reset(v)}>
            <Tex tex={`\\sqrt{${v}}`} />
          </button>
        ))}
      </div>
      <p className="muted">
        Разложили <Tex tex={`${n}`} /> на простые множители. Нажми на два одинаковых: они выйдут из-под корня.
      </p>
      <div className="house" aria-label="Под корнем">
        <span className="roof" aria-hidden>
          √
        </span>
        <div className="tile-row">
          {tiles.map((t) =>
            t.out ? null : (
              <button key={t.id} className={`tile ${sel === t.id ? 'sel' : ''}`} onClick={() => tap(t)} aria-label={`Множитель ${t.p}`}>
                {t.p}
              </button>
            ),
          )}
          {inside.length === 0 && <span className="muted">пусто (под корнем 1)</span>}
        </div>
      </div>
      <div className="outside" aria-label="Вышли из-под корня">
        Вышли: {exited.length === 0 ? <span className="muted">пока никого</span> : exited.map((p, i) => <span key={i} className="tile static c2">{p}</span>)}
      </div>
      {msg && (
        <p className="viz-msg" aria-live="polite">
          {msg}
        </p>
      )}
      <div className="readout">
        Получилось: <Tex tex={`\\sqrt{${n}}=${result}`} />
        {!canPair && <div>✅ Пар больше нет, дальше упрощать нельзя.</div>}
      </div>
      <div className="viz-actions">
        <button className="btn small ghost" onClick={() => reset()}>
          Заново
        </button>
      </div>
    </div>
  )
}
