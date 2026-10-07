/** Текст с формулами: $…$ — формула в строке, $$…$$ — формула отдельной строкой. */
export type Rich = string

export type VizBlock = { type: 'viz'; id: 'cancel' | 'odz' | 'commonDenominator' | 'bars'; preset?: string }

export type Block =
  | { type: 'text'; text: Rich }
  | { type: 'math'; tex: string }
  | { type: 'note'; kind: 'warn' | 'tip'; text: Rich }
  | { type: 'example'; title?: Rich; steps: Rich[] }
  | VizBlock

export type Step = { id: string; title: string; blocks: Block[] }

export type ChoiceQuestion = {
  id: string
  kind: 'choice'
  prompt: Rich
  options: Rich[]
  correct: number
  explain: Rich
  step: number
}

export type InputQuestion = {
  id: string
  kind: 'input'
  prompt: Rich
  expr?: string
  answer: string
  answerKind: AnswerKind
  reduce?: boolean
  explain: Rich
  step: number
}

export type Question = ChoiceQuestion | InputQuestion

/** expr — выражение; roots — набор чисел через «;» (или «нет»). */
export type AnswerKind = 'expr' | 'roots'

export type Task = {
  id: string
  level: 1 | 2 | 3
  source: string
  /** В prompt подставляется {expr} — формула из поля expr. */
  prompt: Rich
  expr?: string
  answer: string
  answerKind: AnswerKind
  /** Ответ обязан быть одной несократимой дробью. */
  reduce?: boolean
  /** Как SymPy проверяет ответ (используется только в tools/verify_answers.py). */
  verify?: Verify
  hint: Rich
  solution: Rich[]
}

/** reduce — cancel(expr); simplify — cancel(together(expr)); value — expr.subs(subs); odz — нули знаменателей; custom — выражение SymPy. */
export type Verify = {
  op: 'reduce' | 'simplify' | 'value' | 'odz' | 'custom'
  subs?: Record<string, string>
  sympy?: string
}

export type Topic = {
  id: string
  order: number
  title: string
  summary: Rich
  steps: Step[]
  check: Question[]
  /** Сколько вопросов проверки нужно решить верно. */
  passScore: number
  tasks: Task[]
}
