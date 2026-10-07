import { useMemo, useState } from 'react'
import { Tex } from '../components/Tex'

type Factor = { tex: string; paren?: boolean }
type Example = { expanded: string; num: Factor[]; den: Factor[]; excluded: string; note?: string }

const f = (tex: string, paren = false): Factor => ({ tex, paren })

const EXAMPLES: Example[] = [
  {
    expanded: '\\frac{x^2-9}{x^2+3x}',
    num: [f('x-3', true), f('x+3', true)],
    den: [f('x'), f('x+3', true)],
    excluded: 'x\\ne 0,\\ x\\ne -3',
  },
  {
    expanded: '\\frac{a^2-4a+4}{a^2-4}',
    num: [f('a-2', true), f('a-2', true)],
    den: [f('a-2', true), f('a+2', true)],
    excluded: 'a\\ne 2,\\ a\\ne -2',
  },
  {
    expanded: '\\frac{4a-4b}{a^2-b^2}',
    num: [f('4'), f('a-b', true)],
    den: [f('a-b', true), f('a+b', true)],
    excluded: 'a\\ne b,\\ a\\ne -b',
  },
  {
    expanded: '\\frac{6x^2}{9x}',
    num: [f('2'), f('3'), f('x'), f('x')],
    den: [f('3'), f('3'), f('x')],
    excluded: 'x\\ne 0',
  },
  {
    expanded: '\\frac{3-x}{x^2-9}',
    num: [f('-1'), f('x-3', true)],
    den: [f('x-3', true), f('x+3', true)],
    excluded: 'x\\ne 3,\\ x\\ne -3',
    note: '3−x = −(x−3): выноси минус, чтобы получить одинаковые скобки.',
  },
]

type Tile = { id: string; side: 'n' | 'd'; factor: Factor }

function tilesOf(ex: Example): Tile[] {
  return [
    ...ex.num.map((factor, i) => ({ id: `n${i}`, side: 'n' as const, factor })),
    ...ex.den.map((factor, i) => ({ id: `d${i}`, side: 'd' as const, factor })),
  ]
}

function product(tiles: Tile[]): string {
  if (tiles.length === 0) return '1'
  return tiles
    .map((t, i) => {
      const alone = tiles.length === 1
      if (t.factor.paren) return alone ? t.factor.tex : `(${t.factor.tex})`
      const numeric = /^-?\d+$/.test(t.factor.tex)
      return numeric && i > 0 ? `\\cdot ${t.factor.tex}` : t.factor.tex
    })
    .join('')
}

const key = (t: Tile) => t.factor.tex

export function CancelViz({ preset }: { preset?: string }) {
  const [ei, setEi] = useState(preset === 'second' ? 1 : 0)
  const ex = EXAMPLES[ei]
  const tiles = useMemo(() => tilesOf(ex), [ex])
  const [factored, setFactored] = useState(false)
  const [gone, setGone] = useState<Set<string>>(new Set())
  const [sel, setSel] = useState<string | null>(null)
  const [msg, setMsg] = useState<string | null>(null)

  const reset = (i = ei) => {
    setEi(i)
    setFactored(false)
    setGone(new Set())
    setSel(null)
    setMsg(null)
  }

  const live = tiles.filter((t) => !gone.has(t.id))
  const liveN = live.filter((t) => t.side === 'n')
  const liveD = live.filter((t) => t.side === 'd')
  const canCancel = liveN.some((n) => liveD.some((d) => key(d) === key(n)))
  const finished = factored && !canCancel

  const tap = (t: Tile) => {
    if (gone.has(t.id)) return
    if (sel === null) {
      setSel(t.id)
      setMsg(null)
      return
    }
    if (sel === t.id) {
      setSel(null)
      return
    }
    const other = tiles.find((x) => x.id === sel)!
    if (other.side !== t.side && key(other) === key(t)) {
      setGone(new Set([...gone, other.id, t.id]))
      setMsg('Сократили! Делим числитель и знаменатель на этот множитель.')
    } else if (other.side === t.side) {
      setMsg('Сокращать можно только пару «сверху и снизу».')
    } else {
      setMsg('Эти множители разные — сокращать нельзя.')
    }
    setSel(null)
  }

  const hint = () => {
    const n = liveN.find((a) => liveD.some((d) => key(d) === key(a)))
    if (n) setSel(n.id)
  }

  const row = (side: 'n' | 'd') => (
    <div className="tile-row">
      {tiles
        .filter((t) => t.side === side)
        .map((t, i) => (
          <span key={t.id} className="tile-wrap">
            {i > 0 && <span className="times" aria-hidden>·</span>}
            <button
              className={`tile ${gone.has(t.id) ? 'gone' : ''} ${sel === t.id ? 'sel' : ''}`}
              onClick={() => tap(t)}
              disabled={gone.has(t.id)}
              aria-label={`Множитель ${t.factor.tex}${gone.has(t.id) ? ', сокращён' : ''}`}
            >
              <Tex tex={t.factor.paren ? `(${t.factor.tex})` : t.factor.tex} />
            </button>
          </span>
        ))}
    </div>
  )

  return (
    <div className="viz cancel">
      <div className="viz-title">Сокращалка: нажми на два одинаковых множителя</div>
      {!factored ? (
        <div className="cancel-start">
          <Tex display tex={ex.expanded} />
          <button className="btn primary" onClick={() => setFactored(true)}>
            Разложить на множители
          </button>
        </div>
      ) : (
        <div className="cancel-board">
          {row('n')}
          <div className="vinculum" />
          {row('d')}
        </div>
      )}
      {msg && (
        <p className="viz-msg" aria-live="polite">
          {msg}
        </p>
      )}
      {ex.note && factored && <p className="muted">{ex.note}</p>}
      {factored && (
        <div className="readout">
          Получилось: <Tex tex={`\\frac{${product(liveN)}}{${product(liveD)}}`} />
          {finished && (
            <div>
              ✅ Больше сокращать нечего. Допустимо: <Tex tex={ex.excluded} />
            </div>
          )}
        </div>
      )}
      <div className="viz-actions">
        {factored && !finished && (
          <button className="btn small ghost" onClick={hint}>
            Подсказать пару
          </button>
        )}
        {factored && (
          <button className="btn small ghost" onClick={() => reset()}>
            Заново
          </button>
        )}
        <button className="btn small ghost" onClick={() => reset((ei + 1) % EXAMPLES.length)}>
          Другой пример ({ei + 1}/{EXAMPLES.length})
        </button>
      </div>
    </div>
  )
}
