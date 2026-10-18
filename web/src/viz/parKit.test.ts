import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { describe, expect, it } from 'vitest'
import type { Fig, Task } from '../content/types'
import { figRegistry } from './registry'
import {
  angleAt,
  arcPath,
  bisectorHit,
  dist,
  fitView,
  fmt,
  foot,
  inPoly,
  intersect,
  mid,
  parallelogram,
  parseMark,
  parseNum,
  trapezoid,
  P,
} from './parKit'

describe('геометрия картинок про параллелограмм и трапецию', () => {
  it('параллелограмм: противоположные стороны равны, соседние углы дают 180°', () => {
    for (const [a, b, ang] of [[8, 5, 60], [7, 4, 120], [6, 6, 45], [10, 3, 150]]) {
      const q = parallelogram(a, b, ang)
      expect(dist(q.A, q.D)).toBeCloseTo(a, 9)
      expect(dist(q.B, q.C)).toBeCloseTo(a, 9)
      expect(dist(q.A, q.B)).toBeCloseTo(b, 9)
      expect(dist(q.C, q.D)).toBeCloseTo(b, 9)
      expect(angleAt(q.D, q.A, q.B)).toBeCloseTo(ang, 9)
      expect(angleAt(q.A, q.B, q.C)).toBeCloseTo(180 - ang, 9)
      expect(angleAt(q.B, q.C, q.D)).toBeCloseTo(ang, 9)
    }
  })

  it('диагонали параллелограмма делятся точкой пересечения пополам', () => {
    const q = parallelogram(9, 4, 70)
    const o = intersect(q.A, q.C, q.B, q.D)!.p
    expect(dist(o, q.A)).toBeCloseTo(dist(o, q.C), 9)
    expect(dist(o, q.B)).toBeCloseTo(dist(o, q.D), 9)
  })

  it('биссектриса угла A отсекает на BC отрезок BM = AB', () => {
    for (const [a, b, ang] of [[8, 5, 60], [9, 3, 110], [7, 6, 40], [10, 4, 140]]) {
      const q = parallelogram(a, b, ang)
      const m = bisectorHit(q, 'A', 'B', 'C')!
      expect(dist(q.B, m)).toBeCloseTo(b, 9)
      expect(dist(m, q.C)).toBeCloseTo(a - b, 9)
      // а биссектриса угла D отсекает CK = CD
      const k = bisectorHit(q, 'D', 'B', 'C')!
      expect(dist(q.C, k)).toBeCloseTo(b, 9)
    }
  })

  it('средняя линия трапеции равна полусумме оснований и параллельна им', () => {
    for (const [a, b, h, s] of [[10, 4, 3, 1], [9, 5, 4, 0], [12, 2, 5, 4]]) {
      const q = trapezoid(a, b, h, s)
      const M = mid(q.A, q.B)
      const N = mid(q.C, q.D)
      expect(dist(M, N)).toBeCloseTo((a + b) / 2, 9)
      expect(M.y).toBeCloseTo(N.y, 9)
    }
  })

  it('основание высоты и пересечение прямых', () => {
    const h = foot(P(2, 5), P(0, 0), P(10, 0))
    expect(h.x).toBeCloseTo(2, 9)
    expect(h.y).toBeCloseTo(0, 9)
    expect(intersect(P(0, 0), P(1, 0), P(0, 1), P(1, 1))).toBeNull()
  })

  it('числа по-русски и подписи рисунка', () => {
    expect(fmt(3.5)).toBe('3,5')
    expect(fmt(-2)).toBe('−2')
    expect(fmt(7.04)).toBe('7')
    expect(fmt(2 / 3, 2)).toBe('0,67')
    expect(parseNum('3,5')).toBe(3.5)
    expect(parseMark('AB=5')).toEqual({ name: 'AB', value: '5', unknown: false })
    expect(parseMark('CAD=?')).toEqual({ name: 'CAD', value: '?', unknown: true })
    expect(parseMark('A=40°')?.value).toBe('40°')
    expect(parseMark('мусор')).toBeNull()
  })

  it('вписывание в SVG и многоугольник', () => {
    const v = fitView([P(0, 0), P(10, 0), P(10, 5)], { w: 320, maxH: 160, padX: 30, padTop: 20, padBottom: 20 })
    expect(v.X(P(0, 0))).toBeGreaterThanOrEqual(30 - 1e-9)
    expect(v.X(P(10, 0))).toBeLessThanOrEqual(290 + 1e-9)
    expect(v.Y(P(0, 5))).toBeLessThan(v.Y(P(0, 0)))
    expect(inPoly([1, 1], [[0, 0], [4, 0], [4, 4], [0, 4]])).toBe(true)
    expect(inPoly([5, 1], [[0, 0], [4, 0], [4, 4], [0, 4]])).toBe(false)
    expect(arcPath([0, 0], [1, 0], [0, 1], 10)).toMatch(/^M10 0A10 10 0 0 1 0 10$/)
  })
})

// Рисунки всех сгенерированных заданий: собираются без ошибок, все подписи на месте.
const generated = import.meta.glob('../../../content/geometry8/generated/*.json', { import: 'default', eager: true }) as Record<string, { tasks: Task[] }>
const figTasks = Object.values(generated).flatMap((g) => g.tasks.filter((t): t is Task & { fig: Fig } => !!t.fig && (t.fig.id === 'par' || t.fig.id === 'trap')))

describe('рисунки к заданиям (par, trap)', () => {
  it.skipIf(figTasks.length === 0)('каждый рисунок собирается, подписи не потеряны', () => {
    for (const t of figTasks) {
      const C = figRegistry[t.fig.id]
      const html = renderToStaticMarkup(createElement(C, t.fig.props ?? {}))
      expect(html, t.id).not.toMatch(/NaN|undefined|Infinity/)
      expect(html, t.id).toContain('aria-label="Рисунок:')
      const marks = (t.fig.props?.marks as string[] | undefined) ?? []
      const drawn = (html.match(/class="pk-m[ "]/g) ?? []).length
      expect(drawn, `${t.id}: подписей на рисунке ${drawn}, а в данных ${marks.length}`).toBe(marks.length)
      // угловая подпись «?»: значения не пропали из разметки
      for (const raw of marks) {
        const m = parseMark(raw)!
        expect(html, `${t.id}: ${raw}`).toContain(`>${m.value}</text>`)
      }
      const legend = t.fig.props?.legend
      if (typeof legend === 'string') expect(html, t.id).toContain(legend)
    }
  })

  it.skipIf(figTasks.length === 0)('сгенерированных рисунков хватает на все группы', () => {
    expect(new Set(figTasks.map((t) => t.fig.id))).toEqual(new Set(['par', 'trap']))
  })
})
