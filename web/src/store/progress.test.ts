import { describe, expect, it } from 'vitest'
import { topics } from '../content/load'
import {
  emptyState,
  finishExplain,
  markRevealed,
  recordAttempt,
  recordCheck,
  topicStats,
  touchStreak,
  XP,
} from './progress'

const day = (s: string) => new Date(`${s}T12:00:00`)

describe('серия дней', () => {
  it('растёт по дням и сбрасывается после пропуска', () => {
    let s = touchStreak(emptyState(), day('2026-10-07'))
    expect(s.streak).toBe(1)
    s = touchStreak(s, day('2026-10-07'))
    expect(s.streak).toBe(1)
    s = touchStreak(s, day('2026-10-08'))
    expect(s.streak).toBe(2)
    s = touchStreak(s, day('2026-10-10'))
    expect(s.streak).toBe(1)
  })
})

describe('прогресс', () => {
  it('очки за задачу с первой попытки и позже', () => {
    let s = recordAttempt(emptyState(), 't', 'a', true)
    expect(s.xp).toBe(XP.taskFirstTry)
    s = recordAttempt(s, 't', 'b', false)
    s = recordAttempt(s, 't', 'b', true)
    expect(s.xp).toBe(XP.taskFirstTry + XP.taskLater)
    expect(s.topics.t.tasks.b.firstTry).toBe(false)
    expect(recordAttempt(s, 't', 'a', true).xp).toBe(s.xp)
  })
  it('после показа решения очки меньше', () => {
    let s = markRevealed(emptyState(), 't', 'a')
    s = recordAttempt(s, 't', 'a', true)
    expect(s.xp).toBe(XP.taskLater)
  })
  it('проверка засчитывается один раз', () => {
    let s = recordCheck(emptyState(), 't', 3, 4)
    expect(s.topics.t.checkPassed).toBe(false)
    s = recordCheck(s, 't', 4, 4)
    s = recordCheck(s, 't', 5, 4)
    expect(s.xp).toBe(XP.checkPassed)
    expect(s.topics.t.checkBest).toBe(5)
  })
  it('процент по теме', () => {
    const topic = topics[0]
    let s = finishExplain(emptyState(), topic.id)
    s = recordCheck(s, topic.id, topic.passScore, topic.passScore)
    for (const t of topic.tasks) s = recordAttempt(s, topic.id, t.id, true)
    const st = topicStats(topic, s.topics[topic.id])
    expect(st.percent).toBe(100)
    expect(st.status).toBe('trained')
    expect(topicStats(topic, undefined).percent).toBe(0)
  })
})
