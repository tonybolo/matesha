import type { FigValue } from '../../content/types'
import { GeoFigure } from '../parDraw'
import { P, describeFig, parallelogram, type Quad } from '../parKit'

const num = (v: FigValue | undefined, d: number): number => (typeof v === 'number' && Number.isFinite(v) ? v : d)
const list = (v: FigValue | undefined): string[] => (Array.isArray(v) ? v.map(String) : typeof v === 'string' && v ? [v] : [])

/** Обычный выпуклый четырёхугольник: ни параллельных, ни равных сторон, чтобы рисунок не подсказывал признак. */
const GENERIC: Quad = { A: P(0, 0), B: P(0.5, 3.1), C: P(5.3, 3.7), D: P(6.3, 0.4) }

/**
 * Рисунок к заданиям про параллелограмм: a = AD, b = AB, ang = ∠A в градусах.
 * Дополнительно: marks, diag, ht, bis, legend; quad — обычный четырёхугольник (для признаков).
 */
export function ParFig(props: Record<string, FigValue>) {
  const generic = props.quad === true
  const V = generic ? GENERIC : parallelogram(num(props.a, 7), num(props.b, 4), num(props.ang, 60))
  const diag = props.diag === true ? true : typeof props.diag === 'string' && props.diag ? props.diag : undefined
  const spec = {
    V,
    marks: list(props.marks),
    diag,
    ht: list(props.ht),
    bis: list(props.bis),
    arcs: list(props.arcs),
    legend: typeof props.legend === 'string' ? props.legend : undefined,
  }
  return <GeoFigure spec={{ ...spec, label: describeFig(spec, generic ? 'четырёхугольник ABCD' : 'параллелограмм ABCD') }} />
}
