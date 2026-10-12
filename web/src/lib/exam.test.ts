import { describe, expect, it } from 'vitest'
import { topics } from '../content/load'
import { buildExam, FORMATS, type ExamKind } from './exam'

const idsOf = (kind: ExamKind, seed: number, d: 'basic' | 'advanced') =>
  buildExam(topics, seed, d, kind).sections.flatMap((s) => s.items.map((i) => i.id))

describe('контрольная: классная работа', () => {
  it('3 задания по 2 примера, без повторов', () => {
    const exam = buildExam(topics, 1234, 'basic')
    expect(exam.sections).toHaveLength(3)
    const ids = exam.sections.flatMap((s) => s.items.map((i) => i.id))
    expect(ids).toHaveLength(6)
    expect(new Set(ids).size).toBe(6)
    exam.sections.forEach((s, si) => s.items.forEach((it, pi) => expect(it.label).toBe(`${si + 1}${['а', 'б'][pi]}`)))
  })
  it('на любом seed есть задания обеих сложностей, все с уроком', () => {
    for (const difficulty of ['basic', 'advanced'] as const) {
      for (let seed = 1; seed <= 200; seed++) {
        const exam = buildExam(topics, seed, difficulty)
        for (const s of exam.sections) {
          for (const it of s.items) {
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

describe('контрольная: общие свойства всех форматов', () => {
  for (const f of FORMATS) {
    it(`${f.id}: один seed — один вариант, разные seed — разные, задания с уроком`, () => {
      expect(idsOf(f.id, 7, 'basic')).toEqual(idsOf(f.id, 7, 'basic'))
      const variants = new Set<string>()
      for (let seed = 1; seed <= 30; seed++) variants.add(idsOf(f.id, seed, 'basic').join())
      expect(variants.size).toBeGreaterThan(20)
      for (const difficulty of ['basic', 'advanced'] as const) {
        for (let seed = 1; seed <= 100; seed++) {
          const exam = buildExam(topics, seed, difficulty, f.id)
          const items = exam.sections.flatMap((s) => s.items)
          expect(new Set(items.map((i) => i.id)).size).toBe(items.length)
          expect(items.map((i) => i.label)).toEqual(f.sections.flatMap((s) => s.slots.map((x) => x.label)))
          for (const it of items) {
            expect(it.task.group).toBe(it.groupId)
            const topic = topics.find((t) => t.id === it.topicId)!
            expect(it.lessonStep).toBeLessThan(topic.steps.length)
          }
        }
      }
    })
  }
})

describe('контрольная: формат книги', () => {
  it('КР № 3: А1–А3 из тем про корни, как в книге', () => {
    const items = buildExam(topics, 11, 'basic', 'kr3').sections.flatMap((s) => s.items)
    expect(items.map((i) => i.label)).toEqual(['А1', 'А2', 'А3', 'В1', 'С1', 'С2'])
    expect(items.map((i) => i.groupId)).toEqual(['irr', 'val', 'dom', 'inc', 'ord', 'gsq'])
    expect(items[0].task.answerKind).toBe('choice')
    expect(items[2].task.answerKind).toBe('choice')
    expect(items[4].task.answerKind).toBe('order')
  })
  it('КР № 4 и № 5: нужные группы', () => {
    const g4 = buildExam(topics, 11, 'basic', 'kr4').sections.flatMap((s) => s.items.map((i) => i.groupId))
    expect(g4).toEqual(['irr', 'val2', 'arg', 'sq', 'conj', 'rat'])
    const g5 = buildExam(topics, 11, 'basic', 'kr5').sections.flatMap((s) => s.items.map((i) => i.groupId))
    expect(g5).toEqual(['incd', 'cnt', 'mk', 'dsc', 'brk', 'wrd'])
  })
  it('КР № 5, С2 «как в книге» — всегда задача про прямоугольник', () => {
    for (let seed = 1; seed <= 100; seed++) {
      const c2 = buildExam(topics, seed, 'basic', 'kr5').sections[2].items[1]
      expect(c2.task.tag).toBe('rect')
    }
  })
  it('КР № 4, А1 «как в книге» — «не является рациональным»', () => {
    for (let seed = 1; seed <= 50; seed++) {
      const a1 = buildExam(topics, seed, 'basic', 'kr4').sections[0].items[0]
      expect(a1.task.prompt).toContain('не является')
    }
  })
})
