import { describe, expect, it } from 'vitest'
import { topics } from '../content/load'
import { buildExam, PARTS } from './exam'

describe('контрольная', () => {
  it('3 задания по 2 примера, без повторов', () => {
    const exam = buildExam(topics, 1234, 'basic')
    expect(exam.sections).toHaveLength(3)
    const ids = exam.sections.flatMap((s) => s.items.map((i) => i.id))
    expect(ids).toHaveLength(6)
    expect(new Set(ids).size).toBe(6)
    exam.sections.forEach((s, si) => s.items.forEach((it, pi) => expect(it.label).toBe(`${si + 1}${PARTS[pi]}`)))
  })
  it('один seed — один вариант, разные seed — разные варианты', () => {
    const a = buildExam(topics, 7, 'basic').sections.flatMap((s) => s.items.map((i) => i.id))
    const b = buildExam(topics, 7, 'basic').sections.flatMap((s) => s.items.map((i) => i.id))
    expect(a).toEqual(b)
    const variants = new Set<string>()
    for (let seed = 1; seed <= 30; seed++) variants.add(buildExam(topics, seed, 'basic').sections.flatMap((s) => s.items.map((i) => i.id)).join())
    expect(variants.size).toBeGreaterThan(25)
  })
  it('на любом seed есть задания обеих сложностей, все с уроком', () => {
    for (const difficulty of ['basic', 'advanced'] as const) {
      for (let seed = 1; seed <= 200; seed++) {
        const exam = buildExam(topics, seed, difficulty)
        for (const s of exam.sections) {
          for (const it of s.items) {
            expect(it.task.group).toBe(it.groupId)
            const topic = topics.find((t) => t.id === it.topicId)!
            expect(it.lessonStep).toBeLessThan(topic.steps.length)
            if (difficulty === 'basic') expect(it.task.level).toBeLessThanOrEqual(2)
            else expect(it.task.level).toBeGreaterThanOrEqual(2)
          }
        }
      }
    }
  })
  it('уровни «как в тетради»: первые примеры проще', () => {
    for (let seed = 1; seed <= 50; seed++) {
      const exam = buildExam(topics, seed, 'basic')
      expect(exam.sections[0].items[0].task.level).toBe(1)
    }
  })
})
