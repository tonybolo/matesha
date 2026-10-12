import { equivalent } from './equivalence'
import { fractionShape, fractionSize } from './fraction'
import { normalizeInput } from './normalize'
import { tryParse, type Parsed } from './expr'
import { radicalIssue } from './radical'
import type { AnswerKind } from '../content/types'

export type CheckStatus =
  | 'correct'
  | 'wrong'
  | 'invalid'
  | 'notReduced'
  | 'notSingle'
  | 'notSimplified'
  | 'approx'
  | 'empty'
export type CheckResult = { status: CheckStatus; message: string }

export const MESSAGES = {
  empty: 'Введи ответ.',
  invalid:
    'Не получилось разобрать запись. Проверь скобки и знаки; дробь пиши через «/», числитель и знаменатель — в скобках.',
  wrong: 'Пока не верно. Посмотри на подсказку и попробуй ещё раз.',
  notReduced: 'Значение верное, но дробь можно сократить ещё.',
  notSingle: 'Значение верное, но запиши ответ одной дробью.',
  approx: 'Это приблизительное значение. Запиши точный ответ обыкновенной дробью, например 2/3.',
  inverted: 'Похоже, дробь перевёрнута: проверь, что у тебя в числителе, а что в знаменателе.',
  correct: 'Верно!',
  rootsMissing: 'Найденные значения верные, но это не все корни. Проверь, нет ли ещё одного (например, у x² = число два корня: плюс и минус).',
  rootsExtra: 'Среди ответов есть лишнее значение: проверь каждое подстановкой в уравнение.',
  rootsNone: 'На самом деле корней нет: проверь дискриминант (D меньше нуля) или знак числа справа.',
  rootsHave: 'Корни есть: проверь дискриминант (D больше или равен нулю) и реши ещё раз.',
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

/** Подсказки для числовых ответов: округление и «перевёрнутая» дробь. */
function diagnoseNumbers(input: string, user: Parsed, ref: Parsed): CheckResult | null {
  if (user.vars.length > 0 || ref.vars.length > 0) return null
  const vu = user.fn({})
  const vr = ref.fn({})
  if (vu === null || vr === null || vr === 0 || vu === 0) return null
  const refIsShortDecimal = Math.abs(vr * 1000 - Math.round(vr * 1000)) < 1e-6
  const typedDecimal = /\d\.\d/.test(normalizeInput(input))
  if (typedDecimal && !refIsShortDecimal && Math.abs(vu - vr) / Math.abs(vr) < 0.03) {
    return { status: 'approx', message: MESSAGES.approx }
  }
  if (Math.abs(Math.abs(vr) - 1) > 1e-9 && Math.abs(vu * vr - 1) < 1e-9) {
    return { status: 'wrong', message: MESSAGES.inverted }
  }
  return null
}

export type CheckOpts = { reduce?: boolean; radical?: boolean; items?: string[] }

/** Верный порядок плиток по возрастанию значения (номера с нуля). */
export function expectedOrder(items: string[]): number[] | null {
  const vals = items.map((it) => tryParse(it)?.fn({}) ?? null)
  if (vals.some((v) => v === null)) return null
  return vals
    .map((v, i) => ({ v: v as number, i }))
    .sort((a, b) => a.v - b.v)
    .map((x) => x.i)
}

export function checkAnswer(input: string, answer: string, kind: AnswerKind, opts: CheckOpts = {}): CheckResult {
  if (!input.trim()) return { status: 'empty', message: MESSAGES.empty }

  if (kind === 'compare') {
    const t = input.trim()
    if (!['<', '>', '='].includes(t)) return { status: 'invalid', message: 'Выбери знак: <, = или >.' }
    return t === answer
      ? { status: 'correct', message: MESSAGES.correct }
      : { status: 'wrong', message: 'Не то. Сравни квадраты чисел: у кого площадь больше, у того и число больше.' }
  }

  if (kind === 'choice') {
    return input.trim() === answer.trim()
      ? { status: 'correct', message: MESSAGES.correct }
      : { status: 'wrong', message: MESSAGES.wrong }
  }

  if (kind === 'order') {
    const got = input.split(',').map((x) => x.trim())
    const want = opts.items ? expectedOrder(opts.items) : answer.split(',').map(Number)
    if (!want) throw new Error(`Не удалось вычислить порядок: ${opts.items?.join('; ')}`)
    if (got.length !== want.length) return { status: 'invalid', message: 'Расставь все числа по порядку.' }
    return got.every((g, i) => Number(g) === want[i])
      ? { status: 'correct', message: MESSAGES.correct }
      : { status: 'wrong', message: 'Порядок не тот. Подсказка: сравни квадраты чисел.' }
  }

  if (kind === 'roots') {
    const user = parseNumberSet(input)
    if (!user) return { status: 'invalid', message: MESSAGES.invalid }
    const ref = parseNumberSet(answer) ?? []
    if (sameSet(user, ref)) return { status: 'correct', message: MESSAGES.correct }
    const has = (list: number[], v: number) => list.some((r) => Math.abs(r - v) <= 1e-9 * Math.max(1, Math.abs(v)))
    if (ref.length === 0) return { status: 'wrong', message: MESSAGES.rootsNone }
    if (user.length === 0) return { status: 'wrong', message: MESSAGES.rootsHave }
    if (user.every((v) => has(ref, v)) && user.length < ref.length) return { status: 'wrong', message: MESSAGES.rootsMissing }
    if (user.length > ref.length && ref.every((v) => has(user, v))) return { status: 'wrong', message: MESSAGES.rootsExtra }
    return { status: 'wrong', message: MESSAGES.wrong }
  }

  const user: Parsed | null = tryParse(input)
  if (!user) return { status: 'invalid', message: MESSAGES.invalid }
  const ref = tryParse(answer)
  if (!ref) throw new Error(`Некорректный эталонный ответ: ${answer}`)
  if (!equivalent(user, ref)) return diagnoseNumbers(input, user, ref) ?? { status: 'wrong', message: MESSAGES.wrong }

  if (opts.radical) {
    const issue = radicalIssue(user.node)
    if (issue) return { status: 'notSimplified', message: `Значение верное, но запись не упрощена. ${issue}` }
  }

  if (opts.reduce) {
    if (!fractionShape(user.node).single) return { status: 'notSingle', message: MESSAGES.notSingle }
    const us = fractionSize(user)
    const rs = fractionSize(ref)
    if (us !== null && rs !== null && us > rs) return { status: 'notReduced', message: MESSAGES.notReduced }
  }
  return { status: 'correct', message: MESSAGES.correct }
}
