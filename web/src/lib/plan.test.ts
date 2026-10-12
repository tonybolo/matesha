import { describe, expect, it } from 'vitest'
import { topics } from '../content/load'
import { emptyState, recordAttempt } from '../store/progress'
import { PLAN, PLAN_GOAL, planProgress } from './plan'

describe('план подготовки', () => {
  it('все типы заданий плана существуют', () => {
    for (const item of PLAN) {
      const topic = topics.find((t) => t.id === item.topic)
      expect(topic, item.id).toBeTruthy()
      for (const g of item.groups) expect(topic!.groups?.some((x) => x.id === g), `${item.id}/${g}`).toBe(true)
    }
  })
  it('сначала урок, потом типы по порядку, в конце «готово»', () => {
    let s = emptyState()
    let rows = planProgress(topics, s)
    expect(rows.map((r) => r.next.kind)).toEqual(['lesson', 'lesson', 'lesson'])
    expect(rows[0].total).toBe(PLAN[0].groups.length * PLAN_GOAL)
    const topic = topics.find((t) => t.id === PLAN[0].topic)!
    s = { ...s, topics: { [topic.id]: { stepReached: 0, explainDone: true, checkBest: 0, checkPassed: false, tasks: {} } } }
    rows = planProgress(topics, s)
    expect(rows[0].next.kind).toBe('train')
    expect(rows[0].next.href).toContain(`group=${PLAN[0].groups[0]}`)
    for (const gid of PLAN[0].groups) {
      for (const t of topic.tasks.filter((x) => x.group === gid).slice(0, PLAN_GOAL)) s = recordAttempt(s, topic.id, t.id, true)
      rows = planProgress(topics, s)
    }
    expect(rows[0].next.kind).toBe('done')
    expect(rows[0].done).toBe(rows[0].total)
  })
  it('решённые задания без урока всё равно двигают к тренажёру', () => {
    const topic = topics.find((t) => t.id === PLAN[1].topic)!
    let s = emptyState()
    for (const t of topic.tasks.filter((x) => x.group === PLAN[1].groups[0]).slice(0, 3)) s = recordAttempt(s, topic.id, t.id, true)
    const rows = planProgress(topics, s)
    expect(rows[1].next.kind).toBe('train')
    expect(rows[1].done).toBe(3)
  })
})
