/** Текст с формулами: $…$ — формула в строке, $$…$$ — формула отдельной строкой. */
export type Rich = string

export type VizId =
  | 'cancel'
  | 'odz'
  | 'commonDenominator'
  | 'bars'
  | 'rug'
  | 'bringIn'
  | 'pairs'
  | 'parabola'
  | 'domain'
  | 'sqrtGraph'
  | 'areaMult'
  | 'divide'
  | 'hyperbola'

export type VizBlock = { type: 'viz'; id: VizId; preset?: string }

export type Block =
  | { type: 'text'; text: Rich }
  | { type: 'math'; tex: string }
  | { type: 'note'; kind: 'warn' | 'tip'; text: Rich }
  | { type: 'example'; title?: Rich; steps: Rich[]; reveal?: boolean }
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
  radical?: boolean
  explain: Rich
  step: number
}

export type Question = ChoiceQuestion | InputQuestion

/**
 * expr — выражение; roots — набор чисел через «;» (или «нет»);
 * compare — знак < = >; choice — номер варианта; order — порядок плиток (номера через запятую).
 */
export type AnswerKind = 'expr' | 'roots' | 'compare' | 'order' | 'choice'

export type Task = {
  id: string
  level: 1 | 2 | 3
  source: string
  /** В prompt подставляется {expr} — формула из поля expr. */
  prompt: Rich
  expr?: string
  /** Готовая запись {expr} в TeX (если нужна запись как в книге, например с «:» между дробями). */
  tex?: string
  /** Вторая формула для {expr2} (сравнение двух чисел). */
  expr2?: string
  /** Для answerKind order: формулы-плитки (подставляются в {items}). */
  items?: string[]
  /** Для answerKind choice: варианты ответа; answer — номер верного (с нуля). */
  options?: Rich[]
  answer: string
  /** Красивая запись ответа для показа (TeX), если запись `answer` для компьютера выглядит некрасиво. */
  answerTex?: string
  answerKind: AnswerKind
  /** Ответ обязан быть одной несократимой дробью. */
  reduce?: boolean
  /** Ответ обязан быть в простейшем виде с корнями (без корней из квадратов, без корня в знаменателе). */
  radical?: boolean
  /** Группа тренажёра (для сгенерированных заданий). */
  group?: string
  /** Вид задания внутри группы (нужен, чтобы собрать контрольную точно по образцу, например «rect»). */
  tag?: string
  /** Номер для показа вместо № из id. */
  num?: string
  /** Навыки, которые нужны для решения (основа поиска пробелов). */
  skills?: string[]
  /** Как SymPy проверяет ответ (используется только в tools/verify_answers.py). */
  verify?: Verify
  hint: Rich
  solution: Rich[]
}

/** self — ответ равен значению expr (сгенерированные задания); reduce — cancel(expr); simplify — cancel(together(expr)); value — expr.subs(subs); odz — нули знаменателей; custom — выражение SymPy. */
export type Verify = {
  op: 'reduce' | 'simplify' | 'value' | 'odz' | 'custom' | 'self'
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
  /** Группы типов заданий (если задачи сгенерированы, а не перечислены по номерам). */
  groups?: TaskGroup[]
}

export type TaskGroup = {
  id: string
  title: string
  hint?: string
  /** Шаг урока этой темы (с нуля), где объясняется этот тип заданий. */
  lessonStep?: number
}
