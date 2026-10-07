import { toTex } from '../lib/expr'

/** Подставляет формулу из expr на место {expr}. */
export function renderPrompt(prompt: string, expr?: string): string {
  if (!expr || !prompt.includes('{expr}')) return prompt
  const tex = toTex(expr)
  if (!tex) throw new Error(`Не удалось разобрать выражение: ${expr}`)
  return prompt.replace('{expr}', `$\\displaystyle ${tex}$`)
}
