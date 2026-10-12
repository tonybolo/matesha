import { toTex } from '../lib/expr'

type Extra = { expr2?: string; items?: string[]; tex?: string }

function texOrThrow(expr: string): string {
  const tex = toTex(expr)
  if (!tex) throw new Error(`Не удалось разобрать выражение: ${expr}`)
  return tex
}

/** Подставляет формулы на места {expr}, {expr2} и {items}. */
export function renderPrompt(prompt: string, expr?: string, extra: Extra = {}): string {
  let out = prompt
  const inline = prompt.includes('{expr2}') || prompt.includes('{items}')
  if (expr && out.includes('{expr}')) {
    const tex = extra.tex ?? texOrThrow(expr)
    out = out.replace('{expr}', inline ? `$${tex}$` : `$\\displaystyle ${tex}$`)
  }
  if (extra.expr2 && out.includes('{expr2}')) out = out.replace('{expr2}', `$${texOrThrow(extra.expr2)}$`)
  if (extra.items && out.includes('{items}')) {
    out = out.replace('{items}', extra.items.map((it) => `$${texOrThrow(it)}$`).join(';  '))
  }
  return out
}
