import type { Topic } from '../content/types'
import { hrefTopic } from '../route'
import type { State } from '../store/progress'

/** Для плана «на один день» хватает пяти задач каждого типа (в теме цель — восемь). */
export const PLAN_GOAL = 5

export type PlanItem = {
  id: string
  title: string
  topic: string
  /** Типы заданий этой части контрольной (по порядку работы). */
  groups: string[]
}

const T3 = '03-roots-compare'
const T4 = '04-roots-simplify'
const T5 = '05-quadratic'

/** Три задания контрольной: сравнить, упростить, решить. */
export const PLAN: PlanItem[] = [
  { id: 'compare', title: 'Сравнить числа', topic: T3, groups: ['rootnum', 'cmp', 'ord'] },
  { id: 'simplify', title: 'Упростить выражения с корнями', topic: T4, groups: ['dec', 'out', 'val2', 'sq', 'rat'] },
  { id: 'quad', title: 'Решить квадратные уравнения', topic: T5, groups: ['inc', 'nbx', 'dsc', 'brk', 'cnt'] },
]

export type PlanNext = { kind: 'lesson' | 'train' | 'done'; href: string; label: string }
export type PlanRow = { item: PlanItem; done: number; total: number; lessonHref: string; next: PlanNext }

export function planProgress(topics: Topic[], state: State, plan: PlanItem[] = PLAN): PlanRow[] {
  return plan.map((item) => {
    const topic = topics.find((t) => t.id === item.topic)
    const p = state.topics[item.topic]
    const groups = item.groups.map((id) => topic?.groups?.find((g) => g.id === id)).filter((g): g is NonNullable<typeof g> => !!g)
    const solvedIn = (gid: string) => topic?.tasks.filter((t) => t.group === gid && p?.tasks[t.id]?.solved).length ?? 0
    const done = groups.reduce((acc, g) => acc + Math.min(PLAN_GOAL, solvedIn(g.id)), 0)
    const total = groups.length * PLAN_GOAL
    const lessonHref = hrefTopic(item.topic, 'learn', p?.stepReached)
    let next: PlanNext
    const open = groups.find((g) => solvedIn(g.id) < PLAN_GOAL)
    if (!p?.explainDone && done === 0) next = { kind: 'lesson', href: lessonHref, label: 'Пройти урок' }
    else if (open) next = { kind: 'train', href: hrefTopic(item.topic, 'train', undefined, open.id), label: `${open.title} (${Math.min(PLAN_GOAL, solvedIn(open.id))} из ${PLAN_GOAL})` }
    else next = { kind: 'done', href: hrefTopic(item.topic, 'train'), label: 'Готово! Потренироваться ещё' }
    return { item, done, total, lessonHref, next }
  })
}
