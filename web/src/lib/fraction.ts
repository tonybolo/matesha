import type { MathNode } from 'mathjs'
import { mulberry32 } from './equivalence'
import type { Parsed } from './expr'

type N = MathNode & { args?: MathNode[]; content?: MathNode; fn?: unknown }

function unwrap(node: MathNode): MathNode {
  let n = node as N
  for (;;) {
    if (n.type === 'ParenthesisNode' && n.content) n = n.content as N
    else if (n.type === 'OperatorNode' && ['unaryMinus', 'unaryPlus'].includes(n.fn as string) && n.args)
      n = n.args[0] as N
    else return n
  }
}

function hasDivision(node: MathNode): boolean {
  let found = false
  node.traverse((n) => {
    if (n.type === 'OperatorNode' && (n as N).fn === 'divide') found = true
  })
  return found
}

export type FractionShape = { single: boolean; num: MathNode; den: MathNode | null }

/** «Одна дробь»: сверху/снизу нет вложенных делений, либо деления нет вовсе. */
export function fractionShape(node: MathNode): FractionShape {
  const n = unwrap(node) as N
  if (n.type === 'OperatorNode' && n.fn === 'divide' && n.args) {
    const [num, den] = n.args
    return { single: !hasDivision(num) && !hasDivision(den), num, den }
  }
  return { single: !hasDivision(node), num: node, den: null }
}

function evalNode(node: MathNode, scope: Record<string, number>): number {
  const v = node.compile().evaluate(scope)
  return typeof v === 'number' ? v : NaN
}

/** Степень многочлена (суммарная) — по конечным разностям вдоль случайной прямой. -1: не многочлен. */
export function polyDegree(node: MathNode, vars: string[]): number {
  const MAX = 9
  let best = 0
  for (let seed = 1; seed <= 2; seed++) {
    const rng = mulberry32(seed * 7919)
    const base: Record<string, number> = {}
    const dir: Record<string, number> = {}
    for (const v of vars) {
      base[v] = Math.floor(rng() * 7) - 3
      dir[v] = (rng() < 0.5 ? -1 : 1) * (1 + Math.floor(rng() * 3))
    }
    const vals: number[] = []
    for (let t = 0; t <= MAX + 1; t++) {
      const scope: Record<string, number> = {}
      for (const v of vars) scope[v] = base[v] + dir[v] * t
      const y = evalNode(node, scope)
      if (!Number.isFinite(y)) return -1
      vals.push(y)
    }
    const scale = Math.max(1, ...vals.map(Math.abs))
    let diffs = vals
    let deg = -1
    for (let k = 0; k <= MAX; k++) {
      if (diffs.every((d) => Math.abs(d) <= 1e-7 * scale)) {
        deg = Math.max(0, k - 1)
        break
      }
      diffs = diffs.slice(1).map((d, i) => d - diffs[i])
    }
    if (deg < 0) return -1
    best = Math.max(best, deg)
  }
  return best
}

/** Сумма степеней числителя и знаменателя; null, если оценить не удалось. */
export function fractionSize(p: Parsed): number | null {
  const shape = fractionShape(p.node)
  if (!shape.single) return null
  const vars = p.vars
  const dn = polyDegree(shape.num, vars)
  const dd = shape.den ? polyDegree(shape.den, vars) : 0
  if (dn < 0 || dd < 0) return null
  return dn + dd
}

