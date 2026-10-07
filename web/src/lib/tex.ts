import type { MathNode } from 'mathjs'

type N = MathNode & { args?: MathNode[]; content?: MathNode; fn?: unknown; value?: unknown; name?: string }

function unwrapParens(n: MathNode): MathNode {
  let cur = n as N
  while (cur.type === 'ParenthesisNode' && cur.content) cur = cur.content as N
  return cur
}

function num(v: number): string {
  return String(v).replace('.', '{,}')
}

function isNumberLike(n: MathNode): boolean {
  const u = unwrapParens(n) as N
  if (n.type === 'ParenthesisNode') return false
  if (u.type === 'ConstantNode') return true
  if (u.type === 'OperatorNode' && u.fn === 'pow' && u.args) return isNumberLike(u.args[0])
  return false
}

/** Собственный генератор TeX: дроби, степени, корни как в учебнике (mathjs.toTex выдаёт лишнее). */
export function nodeToTex(node: MathNode): string {
  const n = node as N
  switch (n.type) {
    case 'ConstantNode':
      return num(n.value as number)
    case 'SymbolNode':
      return n.name ?? ''
    case 'ParenthesisNode':
      return `\\left(${nodeToTex(n.content as MathNode)}\\right)`
    case 'FunctionNode': {
      const name = (n.fn as { name: string }).name
      const arg = nodeToTex(unwrapParens((n.args as MathNode[])[0]))
      if (name === 'sqrt') return `\\sqrt{${arg}}`
      if (name === 'abs') return `\\left|${arg}\\right|`
      return `${name}\\left(${arg}\\right)`
    }
    case 'OperatorNode': {
      const args = n.args as MathNode[]
      switch (n.fn) {
        case 'add':
          return `${nodeToTex(args[0])}+${nodeToTex(args[1])}`
        case 'subtract':
          return `${nodeToTex(args[0])}-${nodeToTex(args[1])}`
        case 'unaryMinus':
          return `-${nodeToTex(args[0])}`
        case 'unaryPlus':
          return `+${nodeToTex(args[0])}`
        case 'multiply': {
          const sep = isNumberLike(args[1]) ? '\\cdot ' : ''
          return `${nodeToTex(args[0])}${sep}${nodeToTex(args[1])}`
        }
        case 'divide':
          return `\\frac{${nodeToTex(unwrapParens(args[0]))}}{${nodeToTex(unwrapParens(args[1]))}}`
        case 'pow': {
          const base = args[0]
          const b = base.type === 'OperatorNode' ? `\\left(${nodeToTex(base)}\\right)` : nodeToTex(base)
          return `${b}^{${nodeToTex(unwrapParens(args[1]))}}`
        }
      }
    }
  }
  return ''
}
