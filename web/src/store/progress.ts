import type { Topic } from '../content/types'

export type TaskState = { attempts: number; solved: boolean; firstTry: boolean; revealed: boolean }

export type TopicProgress = {
  /** Наибольший открытый шаг объяснения (индекс). */
  stepReached: number
  explainDone: boolean
  checkBest: number
  checkPassed: boolean
  tasks: Record<string, TaskState>
}

export type SkillStat = { ok: number; bad: number }

export type ExamResult = {
  at: string
  seed: number
  difficulty: 'basic' | 'advanced'
  /** Формат работы: class, kr3, kr4, kr5 (в старых записях нет). */
  kind?: string
  score: number
  total: number
  /** Идентификаторы заданий с ошибками. */
  wrong: string[]
  seconds: number
}

export type State = {
  v: 1
  name: string
  xp: number
  streak: number
  lastDay: string | null
  topics: Record<string, TopicProgress>
  /** Сколько раз навык получился и не получился (основа поиска пробелов). */
  skills: Record<string, SkillStat>
  exams: ExamResult[]
}

export const emptyTopic = (): TopicProgress => ({
  stepReached: 0,
  explainDone: false,
  checkBest: 0,
  checkPassed: false,
  tasks: {},
})

export const emptyState = (): State => ({ v: 1, name: '', xp: 0, streak: 0, lastDay: null, topics: {}, skills: {}, exams: [] })

/** Сколько заданий в группе считается «целью» по типу. */
export const GROUP_GOAL = 8

export const XP = { taskFirstTry: 10, taskLater: 5, checkPassed: 25, explainDone: 10, examItem: 5, examPerfect: 20 }

const dayKey = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

/** Серия дней подряд: вызывается при любой учебной активности. */
export function touchStreak(s: State, now: Date = new Date()): State {
  const today = dayKey(now)
  if (s.lastDay === today) return s
  const y = new Date(now)
  y.setDate(y.getDate() - 1)
  const streak = s.lastDay === dayKey(y) ? s.streak + 1 : 1
  return { ...s, streak, lastDay: today }
}

function withTopic(s: State, id: string, fn: (t: TopicProgress) => TopicProgress): State {
  const cur = s.topics[id] ?? emptyTopic()
  return { ...s, topics: { ...s.topics, [id]: fn(cur) } }
}

export function setName(s: State, name: string): State {
  return { ...s, name: name.trim() }
}

export function reachStep(s: State, topic: string, step: number): State {
  return withTopic(s, topic, (t) => (step > t.stepReached ? { ...t, stepReached: step } : t))
}

export function finishExplain(s: State, topic: string, now?: Date): State {
  const cur = s.topics[topic] ?? emptyTopic()
  if (cur.explainDone) return s
  return touchStreak({ ...withTopic(s, topic, (t) => ({ ...t, explainDone: true })), xp: s.xp + XP.explainDone }, now)
}

export function recordCheck(s: State, topic: string, score: number, passScore: number, now?: Date): State {
  const cur = s.topics[topic] ?? emptyTopic()
  const passed = score >= passScore
  const firstPass = passed && !cur.checkPassed
  const next = withTopic(s, topic, (t) => ({
    ...t,
    checkBest: Math.max(t.checkBest, score),
    checkPassed: t.checkPassed || passed,
  }))
  return touchStreak({ ...next, xp: next.xp + (firstPass ? XP.checkPassed : 0) }, now)
}

function withSkills(s: State, skills: string[] | undefined, correct: boolean): State {
  if (!skills?.length) return s
  const next = { ...s.skills }
  for (const id of skills) {
    const cur = next[id] ?? { ok: 0, bad: 0 }
    next[id] = correct ? { ...cur, ok: cur.ok + 1 } : { ...cur, bad: cur.bad + 1 }
  }
  return { ...s, skills: next }
}

export function recordAttempt(
  s0: State,
  topic: string,
  taskId: string,
  correct: boolean,
  now?: Date,
  skills?: string[],
): State {
  const cur = s0.topics[topic]?.tasks[taskId] ?? { attempts: 0, solved: false, firstTry: false, revealed: false }
  const s = withSkills(s0, skills, correct)
  if (cur.solved) return s0
  const attempts = cur.attempts + 1
  const solved = correct
  const firstTry = correct && attempts === 1 && !cur.revealed
  const gain = !correct ? 0 : firstTry ? XP.taskFirstTry : XP.taskLater
  const next = withTopic(s, topic, (t) => ({ ...t, tasks: { ...t.tasks, [taskId]: { ...cur, attempts, solved, firstTry } } }))
  return touchStreak({ ...next, xp: next.xp + gain }, now)
}

export function markRevealed(s: State, topic: string, taskId: string): State {
  const cur = s.topics[topic]?.tasks[taskId] ?? { attempts: 0, solved: false, firstTry: false, revealed: false }
  if (cur.revealed || cur.solved) return s
  return withTopic(s, topic, (t) => ({ ...t, tasks: { ...t.tasks, [taskId]: { ...cur, revealed: true } } }))
}

export type WeakSkill = { id: string; ok: number; bad: number; share: number }

/** Навыки, где ошибок заметно больше, чем успехов (не меньше 2 ошибок): что стоит повторить. */
export function weakSkills(s: State, limit = 3): WeakSkill[] {
  return Object.entries(s.skills)
    .map(([id, v]) => ({ id, ok: v.ok, bad: v.bad, share: v.bad / Math.max(1, v.ok + v.bad) }))
    .filter((w) => w.bad >= 2 && w.share >= 0.4)
    .sort((a, b) => b.share - a.share || b.bad - a.bad)
    .slice(0, limit)
}

export function recordExam(s: State, result: ExamResult, skillResults: { skills: string[]; correct: boolean }[], now?: Date): State {
  let next = s
  for (const r of skillResults) next = withSkills(next, r.skills, r.correct)
  const gain = result.score * XP.examItem + (result.score === result.total ? XP.examPerfect : 0)
  next = { ...next, exams: [...next.exams, result].slice(-30), xp: next.xp + gain }
  return touchStreak(next, now)
}

export type TopicStats = {
  solved: number
  total: number
  percent: number
  status: 'new' | 'learning' | 'checked' | 'trained'
}

export function topicStats(topic: Topic, p: TopicProgress | undefined): TopicStats {
  const isSolved = (id: string) => !!p?.tasks[id]?.solved
  let total = topic.tasks.length
  let solved = p ? topic.tasks.filter((t) => isSolved(t.id)).length : 0
  if (topic.groups?.length) {
    // сгенерированные группы: цель — GROUP_GOAL заданий в каждой; решённые вне цели не накручивают процент
    const own = topic.tasks.filter((t) => !t.group)
    total = own.length + topic.groups.length * GROUP_GOAL
    solved =
      own.filter((t) => isSolved(t.id)).length +
      topic.groups.reduce((acc, g) => acc + Math.min(GROUP_GOAL, topic.tasks.filter((t) => t.group === g.id && isSolved(t.id)).length), 0)
  }
  // Шкала: объяснение 15%, проверка 15%, тренировка 70%
  const percent = Math.round(
    (p?.explainDone ? 15 : 0) + (p?.checkPassed ? 15 : 0) + (total ? (solved / total) * 70 : 0),
  )
  let status: TopicStats['status'] = 'new'
  if (p && (p.explainDone || p.stepReached > 0 || solved > 0)) status = 'learning'
  if (p?.checkPassed) status = 'checked'
  if (total && solved / total >= 0.8 && p?.checkPassed) status = 'trained'
  return { solved, total, percent, status }
}

const KEY = 'matesha.v1'

export function loadState(): State {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return emptyState()
    const parsed = JSON.parse(raw) as State
    return parsed && parsed.v === 1 ? { ...emptyState(), ...parsed } : emptyState()
  } catch {
    return emptyState()
  }
}

export function saveState(s: State): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(s))
  } catch {
    /* приватный режим и т.п.: прогресс живёт только в памяти */
  }
}
