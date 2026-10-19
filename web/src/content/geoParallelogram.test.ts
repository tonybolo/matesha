import { describe, expect, it } from 'vitest'
import { mathOf, parseRich } from '../lib/rich'
import { getTopic } from './load'
import { skills } from './skills'
import type { Block, Rich } from './types'

const TOPIC = 'geo-02-parallelogram-trapezoid'

function texts(b: Block): Rich[] {
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

/** После разбора в тексте не должно остаться «**»: это значит, что формула попала внутрь жирного шрифта и звёздочки видны на экране. */
const noStars = (rich: Rich, where: string) => {
  for (const seg of parseRich(rich)) if (seg.kind === 'text') expect(seg.text.includes('**'), `${where}: «${rich.slice(0, 70)}»`).toBe(false)
}

describe(`тема ${TOPIC}`, () => {
  const topic = getTopic(TOPIC)

  it('тема есть, шагов 8, вопросов 7, проходной балл 5', () => {
    expect(topic).toBeDefined()
    expect(topic!.steps).toHaveLength(8)
    expect(topic!.check).toHaveLength(7)
    expect(topic!.passScore).toBe(5)
    expect(topic!.steps[7].title.startsWith('⭐')).toBe(true)
  })

  it('в уроке и проверке нет «**» вокруг формул', () => {
    for (const s of topic!.steps) for (const b of s.blocks) for (const r of texts(b)) noStars(r, `${s.id}`)
    for (const q of topic!.check) {
      noStars(q.prompt, q.id)
      noStars(q.explain, q.id)
      if (q.kind === 'choice') for (const o of q.options) noStars(o, q.id)
    }
  })

  it('в каждом шаге урока есть правило в рамке и пример, а картинки подписаны ссылками на шаги навыков', () => {
    for (const s of topic!.steps) {
      expect(s.blocks.some((b) => b.type === 'note' && b.kind === 'tip'), `${s.id}: нет правила в рамке`).toBe(true)
      expect(s.blocks.some((b) => b.type === 'example'), `${s.id}: нет примера`).toBe(true)
    }
    expect(topic!.steps.filter((s) => s.blocks.some((b) => b.type === 'viz'))).toHaveLength(8)
  })

  it('у картинок урока допустимые режимы (preset)', () => {
    const allowed: Record<string, string[]> = { parallelogram: ['sides', 'angles', 'diagonals', 'signs'], areaCut: ['parallelogram', 'trapezoid'] }
    const used: string[] = []
    for (const s of topic!.steps)
      for (const b of s.blocks) {
        if (b.type !== 'viz') continue
        used.push(b.id + (b.preset ? ':' + b.preset : ''))
        if (b.preset) expect(allowed[b.id], `${s.id}: у картинки ${b.id} нет режимов`).toContain(b.preset)
      }
    expect(used).toEqual(['parallelogram:sides', 'parallelogram:angles', 'parallelogram:diagonals', 'bisector', 'parallelogram:signs', 'trapezoid', 'midline', 'areaCut:parallelogram', 'areaCut:trapezoid'])
  })

  it('все задания: id навыков наши (geo-p-), у каждой группы есть шаг урока', () => {
    const ids = new Set(topic!.tasks.flatMap((t) => t.skills ?? []))
    expect(ids.size).toBeGreaterThan(10)
    for (const id of ids) {
      expect(id.startsWith('geo-p-'), id).toBe(true)
      expect(skills[id]?.topic, id).toBe(TOPIC)
    }
    for (const g of topic!.groups ?? []) {
      expect(g.lessonStep, g.id).toBeDefined()
      expect(g.lessonStep!, g.id).toBeLessThan(topic!.steps.length)
    }
    expect(topic!.groups).toHaveLength(9)
    expect(topic!.groups!.filter((g) => g.star)).toHaveLength(1)
    for (const g of topic!.groups!) expect(topic!.tasks.filter((t) => t.group === g.id)).toHaveLength(24)
  })

  it('навык указывает на шаг, где в уроке есть формулы или слова про него', () => {
    // у каждого навыка шаг лежит внутри урока, а на этом шаге есть пояснение
    for (const [id, sk] of Object.entries(skills)) {
      if (!id.startsWith('geo-p-')) continue
      expect(sk.step, id).toBeLessThan(topic!.steps.length)
      const step = topic!.steps[sk.step]
      expect(mathOf(step.blocks.flatMap(texts).join(' ')).length, `${id}: на шаге ${sk.step + 1} нет формул`).toBeGreaterThan(0)
    }
  })
})
