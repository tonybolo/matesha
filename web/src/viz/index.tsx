import type { Fig, VizBlock } from '../content/types'
import { figRegistry, vizRegistry } from './registry'

export function Viz({ id, preset }: { id: VizBlock['id']; preset?: string }) {
  const Component = vizRegistry[id]
  if (!Component) return <p className="muted">Картинки «{id}» пока нет.</p>
  return <Component preset={preset} />
}

/** Схематичный рисунок над условием задачи или вопроса. */
export function Figure({ fig }: { fig: Fig }) {
  const Component = figRegistry[fig.id]
  if (!Component) return null
  return (
    <div className="figure">
      <Component {...(fig.props ?? {})} />
    </div>
  )
}
