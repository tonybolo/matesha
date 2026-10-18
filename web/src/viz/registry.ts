import type { ComponentType } from 'react'
import type { FigValue } from '../content/types'

export type VizComponent = ComponentType<{ preset?: string }>
export type FigComponent = ComponentType<Record<string, FigValue>>

const lowerFirst = (s: string) => s.charAt(0).toLowerCase() + s.slice(1)

/** Находит в модулях экспорты с именем XxxSuffix и складывает их под id «xxx». */
function collect(modules: Record<string, Record<string, unknown>>, suffix: string): Record<string, ComponentType<never>> {
  const out: Record<string, ComponentType<never>> = {}
  for (const mod of Object.values(modules)) {
    for (const [name, value] of Object.entries(mod)) {
      if (typeof value === 'function' && name.endsWith(suffix) && name.length > suffix.length) {
        out[lowerFirst(name.slice(0, -suffix.length))] = value as ComponentType<never>
      }
    }
  }
  return out
}

/** Картинки уроков: любой файл viz/*Viz.tsx с экспортом QuadFamilyViz становится картинкой quadFamily. */
export const vizRegistry = collect(import.meta.glob('./*Viz.tsx', { eager: true }) as Record<string, Record<string, unknown>>, 'Viz') as Record<string, VizComponent>
// старое имя из уроков алгебры
vizRegistry.commonDenominator = vizRegistry.commonDenom

/** Рисунки к заданиям: файл viz/fig/*Fig.tsx с экспортом ParallelogramFig становится рисунком parallelogram. */
export const figRegistry = collect(import.meta.glob('./fig/*Fig.tsx', { eager: true }) as Record<string, Record<string, unknown>>, 'Fig') as Record<string, FigComponent>
