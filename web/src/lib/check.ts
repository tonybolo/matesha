import { equivalent } from './equivalence'
import { fractionShape, fractionSize } from './fraction'
import { normalizeInput } from './normalize'
import { tryParse, type Parsed } from './expr'
import type { AnswerKind } from '../content/types'

export type CheckStatus = 'correct' | 'wrong' | 'invalid' | 'notReduced' | 'notSingle' | 'empty'
export type CheckResult = { status: CheckStatus; message: string }

export const MESSAGES = {
  empty: 'Введи ответ.',
  invalid:
    'Не получилось разобрать запись. Проверь скобки и знаки; дробь пиши через «/», числитель и знаменатель — в скобках.',
  wrong: 'Пока не верно. Посмотри на подсказку и попробуй ещё раз.',
  notReduced: 'Значение верное, но дробь можно сократить ещё.',
  notSingle: 'Значение верное, но запиши ответ одной дробью.',
  correct: 'Верно!',
}

const EMPTY_SET = /^(нет|нет корней|нет таких|нет таких значений|пусто|∅|none|-)$/

/** Разбор «2; -3» в отсортированный список чисел. null — не разобралось. */
export function parseNumberSet(raw: string): number[] | null {
  let s = raw.trim().toLowerCase()
  s = s.replace(/^[xх]\s*(=|∈)\s*/, '').replace(/[{}]/g, '')
  if (!s) return null
  if (EMPTY_SET.test(s)) return []
  const parts = s.includes(';') ? s.split(';') : s.split(/\s*(?:,|\sи\s)\s*/)
  const out: number[] = []
  for (const part of parts) {
    const t = part.replace(/^[xх]\s*=\s*/, '').trim()
    if (!t) continue
    const p = tryParse(normalizeInput(t) === t ? t : t)
    if (!p || p.vars.length > 0) return null
    const v = p.fn({})
    if (v === null) return null
    out.push(v)
  }
  const uniq = out.sort((a, b) => a - b).filter((v, i, arr) => i === 0 || Math.abs(v - arr[i - 1]) > 1e-9)
  return uniq
}

function sameSet(a: number[], b: number[]): boolean {
  return a.length === b.length && a.every((v, i) => Math.abs(v - b[i]) <= 1e-9 * Math.max(1, Math.abs(v)))
}

export function checkAnswer(
  input: string,
  answer: string,
  kind: AnswerKind,
  opts: { reduce?: boolean } = {},
): CheckResult {
  if (!input.trim()) return { status: 'empty', message: MESSAGES.empty }

  if (kind === 'roots') {
    const user = parseNumberSet(input)
    if (!user) return { status: 'invalid', message: MESSAGES.invalid }
    const ref = parseNumberSet(answer) ?? []
    return sameSet(user, ref)
      ? { status: 'correct', message: MESSAGES.correct }
      : { status: 'wrong', message: MESSAGES.wrong }
  }

  const user: Parsed | null = tryParse(input)
  if (!user) return { status: 'invalid', message: MESSAGES.invalid }
  const ref = tryParse(answer)
  if (!ref) throw new Error(`Некорректный эталонный ответ: ${answer}`)
  if (!equivalent(user, ref)) return { status: 'wrong', message: MESSAGES.wrong }

  if (opts.reduce) {
    if (!fractionShape(user.node).single) return { status: 'notSingle', message: MESSAGES.notSingle }
    const us = fractionSize(user)
    const rs = fractionSize(ref)
    if (us !== null && rs !== null && us > rs) return { status: 'notReduced', message: MESSAGES.notReduced }
  }
  return { status: 'correct', message: MESSAGES.correct }
}
