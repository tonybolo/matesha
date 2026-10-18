import type { FigValue } from '../../content/types'
import { GeoFigure } from '../parDraw'
import { describeFig, trapezoid } from '../parKit'

const num = (v: FigValue | undefined, d: number): number => (typeof v === 'number' && Number.isFinite(v) ? v : d)
const list = (v: FigValue | undefined): string[] => (Array.isArray(v) ? v.map(String) : typeof v === 'string' && v ? [v] : [])

/**
 * Рисунок к заданиям про трапецию: основания AD = a и BC = b, высота h, s — сдвиг вершины B вправо от A.
 * Дополнительно: marks, diag, ht, arcs, ticks (равные боковые стороны), right (прямые углы A и B),
 * mid (средняя линия MN), midx (точки P и Q на диагоналях), legend.
 */
export function TrapFig(props: Record<string, FigValue>) {
  const V = trapezoid(num(props.a, 10), num(props.b, 4), num(props.h, 4), num(props.s, 3))
  const diag = props.diag === true ? true : typeof props.diag === 'string' && props.diag ? props.diag : undefined
  const spec = {
    V,
    marks: list(props.marks),
    diag,
    ht: list(props.ht),
    arcs: list(props.arcs),
    ticks: props.ticks === true,
    right: props.right === true,
    mid: props.mid === true,
    midx: props.midx === true,
    legend: typeof props.legend === 'string' ? props.legend : undefined,
  }
  return <GeoFigure spec={{ ...spec, label: describeFig(spec, 'трапеция ABCD с основаниями AD и BC') }} />
}
