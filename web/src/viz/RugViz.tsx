import { useState } from 'react'
import { Tex } from '../components/Tex'

const CELL = 28
const OFF = 24
const fmt = (v: number) => v.toFixed(2).replace('.', ',')

/** Корень как сторона квадрата: ползунок площади, сторона рисуется в масштабе поверх сетки из плиток. */
export function RugViz() {
  const [n, setN] = useState(25)
  const side = Math.sqrt(n)
  const whole = Number.isInteger(side)
  const lo = Math.floor(side)
  return (
    <div className="viz">
      <div className="viz-title">Коврик из плиток: какая у него сторона?</div>
      <div className="chips">
        {[4, 9, 25, 50, 72, 100].map((v) => (
          <button key={v} className={`chip ${v === n ? 'on' : ''}`} onClick={() => setN(v)}>
            {v}
          </button>
        ))}
      </div>
      <svg viewBox="0 0 330 330" className="rug" role="img" aria-label={`Квадрат площадью ${n}`}>
        {Array.from({ length: 11 }, (_, i) => (
          <g key={i}>
            <line x1={OFF + i * CELL} x2={OFF + i * CELL} y1={OFF} y2={OFF + 10 * CELL} className="grid" />
            <line y1={OFF + i * CELL} y2={OFF + i * CELL} x1={OFF} x2={OFF + 10 * CELL} className="grid" />
            <text x={OFF + i * CELL} y={14} textAnchor="middle" fontSize={10} fill="currentColor" opacity={0.6}>
              {i}
            </text>
          </g>
        ))}
        <rect x={OFF} y={OFF} width={side * CELL} height={side * CELL} className={`rug-fill ${whole ? 'whole' : 'frac'}`} />
        {!whole && lo > 0 && <rect x={OFF} y={OFF} width={lo * CELL} height={lo * CELL} className="rug-core" />}
        <text x={OFF + (side * CELL) / 2} y={OFF + (side * CELL) / 2} textAnchor="middle" dominantBaseline="middle" fontSize={18} fontWeight={700} fill="currentColor">
          {n} плиток
        </text>
      </svg>
      <div className="slider-label">Площадь коврика: {n} плиток</div>
      <input className="slider" type="range" min={1} max={100} step={1} value={n} onChange={(e) => setN(Number(e.target.value))} aria-label="Площадь коврика в плитках" />
      <div className="readout" aria-live="polite">
        {whole ? (
          <>
            Сторона ровно <strong>{side}</strong> плиток: <Tex tex={`\\sqrt{${n}}=${side}`} />. Число целое.
          </>
        ) : (
          <>
            Сторона не укладывается ровно: она между {lo} и {lo + 1}, примерно <strong>{fmt(side)}</strong>. Это <Tex tex={`\\sqrt{${n}}`} />: число{' '}
            <strong>иррациональное</strong> (бесконечная дробь без повторов).
          </>
        )}
      </div>
    </div>
  )
}
