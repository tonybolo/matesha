import { useState } from 'react'
import { Tex } from '../components/Tex'
import { boundaryTex, substitutionTex, texNum } from './domain'
import { Stepper } from './Stepper'

const MIN = -8
const MAX = 8
const W = 360
const px = (x: number) => 18 + ((x - MIN) / (MAX - MIN)) * (W - 36)
const fmt = (v: number) => String(Math.round(v * 100) / 100).replace('.', ',').replace('-', '−')

const PRESETS: [number, number][] = [
  [-16, 0],
  [4, 0],
  [1, -3],
  [-1, 5],
]

const poly = (a: number, b: number) => `${a === 1 ? '' : a === -1 ? '-' : a}x${b === 0 ? '' : b > 0 ? `+${b}` : `${b}`}`

/** Когда √(ax+b) существует: подкоренное число не может быть отрицательным. Ребёнок подставляет x и видит, что получилось под корнем. */
export function DomainViz() {
  const [[a, b], setV] = useState(PRESETS[0])
  const [x, setX] = useState(2)
  const set = (i: number, v: number) => setV(([p, q]) => (i === 0 ? [v === 0 ? 1 : v, q] : [p, v]))
  const boundary = -b / a
  const inner = a * x + b
  const ok = inner >= 0
  const from = a > 0 ? boundary : MIN
  const to = a > 0 ? MAX : boundary
  const clamp = (v: number) => Math.max(MIN, Math.min(MAX, v))
  // нажатие на числовую прямую ставит x в это место (с точностью до 0,5)
  const pick = (clientX: number, svg: SVGSVGElement) => {
    const r = svg.getBoundingClientRect()
    const v = MIN + ((((clientX - r.left) / r.width) * W - 18) / (W - 36)) * (MAX - MIN)
    setX(clamp(Math.round(v * 2) / 2))
  }
  const labelX = Math.max(30, Math.min(W - 30, px(x)))
  return (
    <div className="viz">
      <div className="viz-title">Когда корень существует?</div>

      <div className="viz-step">
        <span className="viz-num">1</span> Выбери выражение под корнем
      </div>
      <div className="chips">
        {PRESETS.map(([p, q], i) => (
          <button key={i} className={`chip wide ${p === a && q === b ? 'on' : ''}`} onClick={() => setV([p, q])}>
            <Tex tex={`\\sqrt{${poly(p, q)}}`} />
          </button>
        ))}
      </div>
      <div className="steppers">
        <Stepper compact label="число при x" value={a} min={-9} max={9} step={1} onChange={(v) => set(0, v)} format={fmt} />
        <Stepper compact label="свободное число" value={b} min={-9} max={9} step={1} onChange={(v) => set(1, v)} format={fmt} />
      </div>
      <div className="viz-expr" aria-live="polite">
        <Tex tex={`\\sqrt{${poly(a, b)}}`} />
      </div>

      <div className="viz-step">
        <span className="viz-num">2</span> Подставь число x и посмотри, что получится под корнем
      </div>
      <svg
        viewBox={`0 0 ${W} 70`}
        className="numline tappable"
        role="img"
        aria-label="Числовая прямая: где корень существует. Нажми на прямую, чтобы выбрать x"
        onClick={(e) => pick(e.clientX, e.currentTarget)}
      >
        <line x1={14} x2={W - 14} y1={38} y2={38} stroke="currentColor" strokeWidth={2} opacity={0.6} />
        <rect x={px(clamp(from))} y={30} width={Math.max(0, px(clamp(to)) - px(clamp(from)))} height={16} className="good-zone" />
        {Array.from({ length: MAX - MIN + 1 }, (_, i) => MIN + i).map((t) => (
          <g key={t}>
            <line x1={px(t)} x2={px(t)} y1={34} y2={42} stroke="currentColor" opacity={0.5} />
            {t % 2 === 0 && (
              <text x={px(t)} y={62} textAnchor="middle" fontSize={11} fill="currentColor" opacity={0.7}>
                {t < 0 ? `−${-t}` : t}
              </text>
            )}
          </g>
        ))}
        {boundary >= MIN && boundary <= MAX && <circle cx={px(boundary)} cy={38} r={6} fill="var(--accent)" stroke="var(--bg)" strokeWidth={2} />}
        <path d={`M${px(x)} 31 l-6 -12 h12 z`} fill={ok ? 'var(--ok)' : 'var(--bad)'} />
        <text x={labelX} y={13} textAnchor="middle" fontSize={12} fontWeight={700} fill={ok ? 'var(--ok)' : 'var(--bad)'}>
          x = {fmt(x)}
        </text>
      </svg>
      <div className="x-row">
        <span className="slider-label">Число x:</span>
        <Stepper compact aria="x" value={x} min={MIN} max={MAX} step={1} onChange={setX} format={fmt} />
        <span className="muted">(или двигай ползунок, или нажми на прямую)</span>
      </div>
      <input className="slider" type="range" min={MIN} max={MAX} step={0.5} value={x} onChange={(e) => setX(Number(e.target.value))} aria-label="Значение x" />

      <div className={`readout ${ok ? '' : 'bad'}`} aria-live="polite">
        <div>
          Подставим <Tex tex={`x=${texNum(x)}`} /> в <Tex tex={poly(a, b)} />:
        </div>
        <div className="viz-calc">
          <Tex tex={substitutionTex(a, b, x)} />
        </div>
        <div>
          {ok ? (
            <>
              <Tex tex={`${texNum(inner)}\\ge 0`} /> — число не отрицательное, корень существует: <Tex tex={`\\sqrt{${texNum(inner)}}`} />
            </>
          ) : (
            <>
              <Tex tex={`${texNum(inner)}<0`} /> — под корнем отрицательное число, корня нет 💥
            </>
          )}
        </div>
        <div className="muted">
          Зелёная полоса — все x, при которых под корнем не будет отрицательного числа: <Tex tex={boundaryTex(a, b)} />
        </div>
      </div>
    </div>
  )
}
