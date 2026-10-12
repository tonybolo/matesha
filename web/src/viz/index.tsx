import type { VizBlock } from '../content/types'
import { BarsViz } from './BarsViz'
import { BringInViz } from './BringInViz'
import { CancelViz } from './CancelViz'
import { CommonDenomViz } from './CommonDenomViz'
import { DomainViz } from './DomainViz'
import { OdzViz } from './OdzViz'
import { PairsViz } from './PairsViz'
import { ParabolaViz } from './ParabolaViz'
import { RugViz } from './RugViz'
import { SqrtGraphViz } from './SqrtGraphViz'

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
    case 'rug':
      return <RugViz />
    case 'bringIn':
      return <BringInViz />
    case 'pairs':
      return <PairsViz />
    case 'parabola':
      return <ParabolaViz />
    case 'domain':
      return <DomainViz />
    case 'sqrtGraph':
      return <SqrtGraphViz />
  }
}
