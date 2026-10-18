import type { FigValue } from '../../content/types'
import { Tex } from '../../components/Tex'
import './DistFig.css'

/** Значение ячейки → TeX: 2.5 → 2{,}5, 1/6 → \frac{1}{6}, 20% → 20\%, p и 2p — как есть. */
function cellTex(v: string | number): string {
  const s = String(v).trim()
  if (/^-?\d+(\.\d+)?$/.test(s)) return s.replace('.', '{,}')
  const fr = s.match(/^(-?)(\d+)\/(\d+)$/)
  if (fr) return `${fr[1]}\\frac{${fr[2]}}{${fr[3]}}`
  const pc = s.match(/^(\d+(?:\.\d+)?)%$/)
  if (pc) return `${pc[1].replace('.', '{,}')}\\%`
  return s
}

const list = (v: FigValue | undefined): (string | number)[] => (Array.isArray(v) ? v : [])
const unknown = (v: string | number) => /[a-z?]/i.test(String(v))

function Table({ xs, ps, name, xh, ph }: { xs: (string | number)[]; ps: (string | number)[]; name: string; xh?: string; ph?: string }) {
  const label = `${xh ?? 'значения ' + name}: ${xs.join('; ')}; ${ph ?? 'вероятности'}: ${ps.join('; ')}`
  return (
    <table className="dfig" aria-label={label}>
      <tbody>
        <tr>
          <th scope="row">{xh ?? <Tex tex={name} />}</th>
          {xs.map((x, i) => (
            <td key={i}>
              <Tex tex={cellTex(x)} />
            </td>
          ))}
        </tr>
        <tr>
          <th scope="row">{ph ?? <Tex tex="P" />}</th>
          {ps.map((p, i) => (
            <td key={i} className={unknown(p) ? 'unk' : ''}>
              <Tex tex={cellTex(p)} />
            </td>
          ))}
        </tr>
      </tbody>
    </table>
  )
}

/** Таблица распределения случайной величины (или таблица частот): xs — значения, ps — вероятности; xs2/ps2 — вторая величина. */
export function DistFig(props: Record<string, FigValue>) {
  const name = typeof props.name === 'string' ? props.name : 'X'
  const xh = typeof props.xh === 'string' ? props.xh : undefined
  const ph = typeof props.ph === 'string' ? props.ph : undefined
  const xs2 = list(props.xs2)
  return (
    <div className="dfig-wrap">
      <Table xs={list(props.xs)} ps={list(props.ps)} name={name} xh={xh} ph={ph} />
      {xs2.length > 0 && <Table xs={xs2} ps={list(props.ps2)} name={typeof props.name2 === 'string' ? props.name2 : 'Y'} />}
    </div>
  )
}
