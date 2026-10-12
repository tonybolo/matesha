import type { MathNode } from 'mathjs'

type N = MathNode & { args?: MathNode[]; content?: MathNode; fn?: unknown }

function unwrap(n: MathNode): MathNode {
  let cur = n as N
  while (cur.type === 'ParenthesisNode' && cur.content) cur = cur.content as N
  return cur
}

function hasSqrt(node: MathNode): boolean {
  let found = false
  node.traverse((n) => {
    if (n.type === 'FunctionNode' && (n as unknown as { fn: { name: string } }).fn.name === 'sqrt') found = true
  })
  return found
}

function numericValue(node: MathNode): number | null {
  try {
    const v = node.compile().evaluate({})
    return typeof v === 'number' && Number.isFinite(v) ? v : null
  } catch {
    return null
  }
}

export const RADICAL_MESSAGES = {
  perfect: 'Один из корней извлекается нацело: посчитай его.',
  factor: 'Вынеси множители из-под корня: каждая пара одинаковых множителей выходит наружу.',
  fraction: 'Под корнем не должно быть дроби или десятичной: упрости.',
  denominator: 'Избавься от корня в знаменателе: умножь верх и низ на нужное выражение.',
}

/** Что мешает считать запись «простейшей»; null — всё в порядке. */
export function radicalIssue(node: MathNode): string | null {
  let issue: string | null = null
  node.traverse((n) => {
    if (issue) return
    const nn = n as N
    if (n.type === 'OperatorNode' && nn.fn === 'divide' && nn.args) {
      if (hasSqrt(nn.args[1])) issue = RADICAL_MESSAGES.denominator
      return
    }
    if (n.type === 'FunctionNode' && (n as unknown as { fn: { name: string } }).fn.name === 'sqrt') {
      const arg = unwrap((nn.args as MathNode[])[0])
      const v = numericValue(arg)
      if (v === null) return
      if (!Number.isInteger(v)) {
        issue = RADICAL_MESSAGES.fraction
        return
      }
      const root = Math.round(Math.sqrt(v))
      if (v >= 0 && root * root === v) {
        issue = RADICAL_MESSAGES.perfect
        return
      }
      for (let d = 2; d * d <= v; d++) {
        if (v % (d * d) === 0) {
          issue = RADICAL_MESSAGES.factor
          return
        }
      }
    }
  })
  return issue
}
