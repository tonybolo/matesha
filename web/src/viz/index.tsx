import type { VizBlock } from '../content/types'
import { BarsViz } from './BarsViz'
import { CancelViz } from './CancelViz'
import { CommonDenomViz } from './CommonDenomViz'
import { OdzViz } from './OdzViz'

export function Viz({ id, preset }: { id: VizBlock['id']; preset?: string }) {
  switch (id) {
    case 'odz':
      return <OdzViz />
    case 'bars':
      return <BarsViz preset={preset} />
    case 'cancel':
      return <CancelViz preset={preset} />
    case 'commonDenominator':
      return <CommonDenomViz preset={preset} />
  }
}
