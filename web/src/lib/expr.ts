import type { MathNode } from 'mathjs'
import { mj } from './mj'
import { normalizeInput } from './normalize'
import { nodeToTex } from './tex'

export type Parsed = { node: MathNode; vars: string[]; fn: (scope: Record<string, number>) => number | null }

const ALLOWED_OPS = new Set(['add', 'subtract', 'multiply', 'divide', 'pow', 'unaryMinus', 'unaryPlus'])
const ALLOWED_FUNCS = new Set(['sqrt', 'abs'])

/** Разбор строки в безопасное дерево. Бросает Error при любой неподдерживаемой конструкции. */
export function parseExpr(raw: string): Parsed {
  const text = normalizeInput(raw)
  if (!text) throw new Error('empty')
  const node = mj.parse(text)
  const vars = new Set<string>()
  node.traverse((n, path) => {
    switch (n.type) {
      case 'ConstantNode': {
        const v = (n as unknown as { value: unknown }).value
        if (typeof v !== 'number') throw new Error('bad constant')
        break
      }
      case 'ParenthesisNode':
        break
      case 'OperatorNode': {
        const fn = (n as unknown as { fn: string }).fn
        if (!ALLOWED_OPS.has(fn)) throw new Error('bad operator')
        break
      }
      case 'FunctionNode': {
        const name = (n as unknown as { fn: { name: string } }).fn.name
        if (!ALLOWED_FUNCS.has(name)) throw new Error('bad function')
        break
      }
      case 'SymbolNode': {
        const name = (n as unknown as { name: string }).name
        if (path === 'fn') break
        if (name.length !== 1) throw new Error('bad symbol')
        if (name === 'e' || name === 'i') throw new Error('reserved symbol')
        vars.add(name)
        break
      }
      default:
        throw new Error('unsupported node ' + n.type)
    }
  })
  const compiled = node.compile()
  const fn = (scope: Record<string, number>): number | null => {
    try {
      const v = compiled.evaluate(scope)
      return typeof v === 'number' && Number.isFinite(v) ? v : null
    } catch {
      return null
    }
  }
  return { node, vars: [...vars].sort(), fn }
}

export function tryParse(raw: string): Parsed | null {
  try {
    return parseExpr(raw)
  } catch {
    return null
  }
}

/** TeX для живого предпросмотра. null — если ввод не разобрался. */
export function toTex(raw: string): string | null {
  const p = tryParse(raw)
  if (!p) return null
  try {
    return nodeToTex(p.node)
  } catch {
    return null
  }
}
