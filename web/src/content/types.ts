/** Текст с формулами: $…$ — формула в строке, $$…$$ — формула отдельной строкой. */
export type Rich = string

/** Картинка урока: имя компонента без «Viz» с маленькой буквы (QuadFamilyViz → quadFamily), см. viz/registry.ts. */
export type VizId = string

/** Схематичный рисунок к заданию или вопросу: id — имя компонента без «Fig» (ParallelogramFig → parallelogram), props — его параметры. */
export type FigValue = number | string | boolean | (number | string)[]
export type Fig = { id: string; props?: Record<string, FigValue> }

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
  fig?: Fig
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
  /** Подсказка в пустом поле ввода (например «ответ в градусах»). */
  placeholder?: string
  explain: Rich
  step: number
  fig?: Fig
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
  /** Схематичный рисунок над условием (геометрия). */
  fig?: Fig
  /** Подсказка в пустом поле ввода (например «ответ в градусах»). */
  placeholder?: string
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

/** Раздел: алгебра, геометрия, вероятность и статистика. */
export type Subject = 'algebra' | 'geometry' | 'stats'

export type Topic = {
  id: string
  /** Раздел; у старых тем алгебры поля нет. */
  subject?: Subject
  /** Номер темы внутри раздела (0 — тема-повторение). */
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
  /** Олимпиадная группа («со звёздочкой»): не входит в процент прохождения темы. */
  star?: boolean
}
