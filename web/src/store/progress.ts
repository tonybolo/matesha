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

export type State = {
  v: 1
  name: string
  xp: number
  streak: number
  lastDay: string | null
  topics: Record<string, TopicProgress>
}

export const emptyTopic = (): TopicProgress => ({
  stepReached: 0,
  explainDone: false,
  checkBest: 0,
  checkPassed: false,
  tasks: {},
})

export const emptyState = (): State => ({ v: 1, name: '', xp: 0, streak: 0, lastDay: null, topics: {} })

export const XP = { taskFirstTry: 10, taskLater: 5, checkPassed: 25, explainDone: 10 }

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

export function recordAttempt(s: State, topic: string, taskId: string, correct: boolean, now?: Date): State {
  const cur = s.topics[topic]?.tasks[taskId] ?? { attempts: 0, solved: false, firstTry: false, revealed: false }
  if (cur.solved) return s
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

export type TopicStats = {
  solved: number
  total: number
  percent: number
  status: 'new' | 'learning' | 'checked' | 'trained'
}

export function topicStats(topic: Topic, p: TopicProgress | undefined): TopicStats {
  const total = topic.tasks.length
  const solved = p ? topic.tasks.filter((t) => p.tasks[t.id]?.solved).length : 0
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
