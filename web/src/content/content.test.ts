import katex from 'katex'
import { describe, expect, it } from 'vitest'
import { cheatsheet, cubes, squares } from './cheatsheet'
import { equivalent } from '../lib/equivalence'
import { checkAnswer } from '../lib/check'
import { tryParse } from '../lib/expr'
import { mathOf } from '../lib/rich'
import { topics } from './load'
import { renderPrompt } from './prompt'
import type { Block, Rich } from './types'

function richOfBlock(b: Block): Rich[] {
  switch (b.type) {
    case 'text':
    case 'note':
      return [b.text]
    case 'example':
      return [...(b.title ? [b.title] : []), ...b.steps]
    default:
      return []
  }
}

function texOk(tex: string, where: string) {
  expect(() => katex.renderToString(tex, { throwOnError: true, strict: 'ignore' }), `${where}: ${tex}`).not.toThrow()
}

describe('контент', () => {
  it('темы загружены по порядку', () => {
    expect(topics.length).toBeGreaterThanOrEqual(2)
    expect(topics.map((t) => t.order)).toEqual([...topics.map((t) => t.order)].sort((a, b) => a - b))
  })

  for (const topic of topics) {
    describe(topic.id, () => {
      it('уникальные id и ссылки на шаги', () => {
        const ids = [...topic.tasks.map((t) => t.id), ...topic.check.map((q) => q.id), ...topic.steps.map((s) => s.id)]
        expect(new Set(ids).size).toBe(ids.length)
        for (const q of topic.check) expect(q.step).toBeLessThan(topic.steps.length)
        expect(topic.passScore).toBeLessThanOrEqual(topic.check.length)
      })

      it('все формулы в уроке компилируются в KaTeX', () => {
        for (const s of topic.steps) {
          for (const b of s.blocks) {
            if (b.type === 'math') texOk(b.tex, `${topic.id}/${s.id}`)
            for (const r of richOfBlock(b)) for (const tex of mathOf(r)) texOk(tex, `${topic.id}/${s.id}`)
          }
        }
        for (const t of [topic.summary, topic.title]) for (const tex of mathOf(t)) texOk(tex, topic.id)
      })

      it('проверочные вопросы корректны', () => {
        for (const q of topic.check) {
          for (const tex of mathOf(q.prompt)) texOk(tex, q.id)
          for (const tex of mathOf(q.explain)) texOk(tex, q.id)
          if (q.kind === 'choice') {
            expect(q.correct).toBeGreaterThanOrEqual(0)
            expect(q.correct).toBeLessThan(q.options.length)
            for (const o of q.options) for (const tex of mathOf(o)) texOk(tex, q.id)
          } else {
            expect(checkAnswer(q.answer, q.answer, q.answerKind, { reduce: q.reduce }).status, q.id).toBe('correct')
          }
        }
      })

      it('задачи: формулы, эталонный ответ принимается', () => {
        for (const t of topic.tasks) {
          const prompt = renderPrompt(t.prompt, t.expr)
          expect(prompt.includes('{expr}'), t.id).toBe(false)
          for (const tex of mathOf(prompt)) texOk(tex, t.id)
          for (const tex of mathOf(t.hint)) texOk(tex, t.id)
          for (const s of t.solution) for (const tex of mathOf(s)) texOk(tex, t.id)
          if (t.expr) expect(tryParse(t.expr), `${t.id}: expr`).not.toBeNull()
          const res = checkAnswer(t.answer, t.answer, t.answerKind, { reduce: t.reduce })
          expect(res.status, `${t.id}: ${t.answer}`).toBe('correct')
        }
      })

      it('в каждом уровне есть задачи', () => {
        for (const level of [1, 2, 3]) expect(topic.tasks.filter((t) => t.level === level).length).toBeGreaterThan(3)
      })
    })
  }
})

describe('шпаргалка', () => {
  const items = cheatsheet.flatMap((s) => s.items)
  it('не пустая', () => {
    expect(cheatsheet.length).toBeGreaterThanOrEqual(4)
    expect(items.length).toBeGreaterThan(15)
  })
  it('формулы собираются в KaTeX', () => {
    for (const it of items) texOk(it.tex, it.name)
  })
  it('тождества верны (проверка числами)', () => {
    for (const it of items) {
      if (!it.lhs || !it.rhs) continue
      const l = tryParse(it.lhs)
      const r = tryParse(it.rhs)
      expect(l, `${it.name}: lhs`).not.toBeNull()
      expect(r, `${it.name}: rhs`).not.toBeNull()
      expect(equivalent(l!, r!), it.name).toBe(true)
    }
  })
  it('ловит неверное тождество', () => {
    expect(equivalent(tryParse('(a+b)^2')!, tryParse('a^2+b^2')!)).toBe(false)
  })
  it('таблицы квадратов и кубов', () => {
    expect(squares[19]).toEqual({ n: 20, v: 400 })
    expect(cubes[9]).toEqual({ n: 10, v: 1000 })
  })
})
