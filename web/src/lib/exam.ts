import type { Task, Topic } from '../content/types'
import { mulberry32 } from './equivalence'

export type Difficulty = 'basic' | 'advanced'
export type ExamKind = 'class' | 'kr3' | 'kr4' | 'kr5'

export type ExamItem = {
  id: string
  /** Номер задания: «1а», «2б» (классная работа) или «А1», «В1», «С2» (как в книге). */
  label: string
  topicId: string
  groupId: string
  groupTitle: string
  lessonStep: number
  task: Task
}

export type ExamSection = { kicker: string; title: string; items: ExamItem[] }
export type ExamVariant = { seed: number; difficulty: Difficulty; kind: ExamKind; sections: ExamSection[] }

/** basic — «как в тетради/книге», adv — «посложнее»; пустой список уровней — источник в этом режиме не используется. */
type Source = { topic: string; group: string; basic: Task['level'][]; adv: Task['level'][]; tag?: string }
type Slot = { label: string; sources: Source[] }
type PlanSection = { kicker: string; title: string; slots: Slot[] }

export type ExamFormat = { id: ExamKind; title: string; blurb: string; minutes: number; sections: PlanSection[] }

const T3 = '03-roots-compare'
const T4 = '04-roots-simplify'
const T5 = '05-quadratic'

const src = (topic: string, group: string, basic: Task['level'][], adv: Task['level'][], tag?: string): Source => ({ topic, group, basic, adv, tag })

export const FORMATS: ExamFormat[] = [
  {
    id: 'class',
    title: 'Как в классной работе',
    blurb: '3 задания по 2 примера: сравнить числа, упростить выражения, решить квадратные уравнения.',
    minutes: 40,
    sections: [
      {
        kicker: 'Задание 1',
        title: 'Сравните числа',
        slots: [
          { label: '1а', sources: [src(T3, 'cmp', [1], [2])] },
          {
            label: '1б',
            sources: [src(T3, 'cmp', [2], [3]), src(T3, 'ord', [1, 2], [2, 3]), src(T3, 'rootnum', [2], [3]), src(T3, 'o3dif', [], [3]), src(T3, 'o3int', [], [3]), src(T3, 'o3btw', [], [3])],
          },
        ],
      },
      {
        kicker: 'Задание 2',
        title: 'Упростите выражение',
        slots: [
          { label: '2а', sources: [src(T4, 'dec', [1], [2]), src(T4, 'val2', [1, 2], [2, 3]), src(T4, 'out', [1, 2], [2, 3])] },
          {
            label: '2б',
            sources: [src(T4, 'dec', [2], [3]), src(T4, 'val', [1, 2], [2, 3]), src(T4, 'rat', [1, 2], [2, 3]), src(T4, 'sq', [1, 2], [2, 3]), src(T4, 'o4nest', [], [3]), src(T4, 'o4sum', [], [3]), src(T4, 'o4inv', [], [3])],
          },
        ],
      },
      {
        kicker: 'Задание 3',
        title: 'Решите квадратное уравнение',
        slots: [
          { label: '3а', sources: [src(T5, 'dsc', [2], [3]), src(T5, 'dsc', [1], [2])] },
          {
            label: '3б',
            sources: [src(T5, 'dsc', [2], [3]), src(T5, 'brk', [1, 2], [2, 3]), src(T5, 'nbx', [2], [3]), src(T5, 'inc', [2], [3]), src(T5, 'o5vie', [], [3]), src(T5, 'o5par', [], [3]), src(T5, 'o5bq', [], [3]), src(T5, 'o5two', [], [3])],
          },
        ],
      },
    ],
  },
  {
    id: 'kr3',
    title: 'КР № 3 · Арифметический квадратный корень',
    blurb: 'Иррациональное число, значение выражения, когда корень имеет смысл, уравнение, порядок чисел, графическое решение.',
    minutes: 45,
    sections: [
      {
        kicker: 'Часть А',
        title: 'Выбери верный ответ или впиши число',
        slots: [
          { label: 'А1', sources: [src(T3, 'irr', [1], [2, 3])] },
          { label: 'А2', sources: [src(T4, 'val', [1, 2], [2, 3])] },
          { label: 'А3', sources: [src(T3, 'dom', [1], [2, 3])] },
        ],
      },
      { kicker: 'Часть В', title: 'Решите уравнение', slots: [{ label: 'В1', sources: [src(T5, 'inc', [2], [3])] }] },
      {
        kicker: 'Часть С',
        title: 'Задания посложнее',
        slots: [
          { label: 'С1', sources: [src(T3, 'ord', [1], [2, 3]), src(T3, 'o3dif', [], [3])] },
          { label: 'С2', sources: [src(T3, 'gsq', [1, 2], [2, 3]), src(T3, 'o3int', [], [3]), src(T3, 'o3btw', [], [3])] },
        ],
      },
    ],
  },
  {
    id: 'kr4',
    title: 'КР № 4 · Свойства корня',
    blurb: 'Не рациональное число, значение выражения, значение аргумента, упрощение, пара чисел, корень в знаменателе.',
    minutes: 45,
    sections: [
      {
        kicker: 'Часть А',
        title: 'Выбери верный ответ или впиши число',
        slots: [
          { label: 'А1', sources: [src(T3, 'irr', [2], [3])] },
          { label: 'А2', sources: [src(T4, 'val2', [2], [3])] },
          { label: 'А3', sources: [src(T3, 'arg', [1], [2, 3])] },
        ],
      },
      { kicker: 'Часть В', title: 'Упростите выражение', slots: [{ label: 'В1', sources: [src(T4, 'sq', [1], [2, 3]), src(T4, 'o4nest', [], [3])] }] },
      {
        kicker: 'Часть С',
        title: 'Задания посложнее',
        slots: [
          { label: 'С1', sources: [src(T4, 'conj', [1, 2], [2, 3]), src(T4, 'o4inv', [], [3])] },
          { label: 'С2', sources: [src(T4, 'rat', [2, 3], [3]), src(T4, 'o4sum', [], [3]), src(T4, 'o4tel', [], [3])] },
        ],
      },
    ],
  },
  {
    id: 'kr5',
    title: 'КР № 5 · Квадратные уравнения',
    blurb: 'Разность корней, число корней, уравнение к задаче, формула корней, скобки, текстовая задача.',
    minutes: 45,
    sections: [
      {
        kicker: 'Часть А',
        title: 'Выбери верный ответ или впиши число',
        slots: [
          { label: 'А1', sources: [src(T5, 'incd', [1], [2, 3])] },
          { label: 'А2', sources: [src(T5, 'cnt', [1, 2], [2, 3])] },
          { label: 'А3', sources: [src(T5, 'mk', [1, 2], [2, 3])] },
        ],
      },
      { kicker: 'Часть В', title: 'Решите уравнение', slots: [{ label: 'В1', sources: [src(T5, 'dsc', [2], [3]), src(T5, 'o5bq', [], [3])] }] },
      {
        kicker: 'Часть С',
        title: 'Задания посложнее',
        slots: [
          { label: 'С1', sources: [src(T5, 'brk', [2], [3]), src(T5, 'o5vie', [], [3])] },
          { label: 'С2', sources: [src(T5, 'wrd', [2], [], 'rect'), src(T5, 'wrd', [], [3]), src(T5, 'o5par', [], [3]), src(T5, 'o5two', [], [3])] },
        ],
      },
    ],
  },
]

export const formatOf = (kind: ExamKind): ExamFormat => FORMATS.find((f) => f.id === kind) ?? FORMATS[0]

/** Собирает вариант контрольной. Один и тот же seed даёт один и тот же вариант. */
export function buildExam(topics: Topic[], seed: number, difficulty: Difficulty, kind: ExamKind = 'class'): ExamVariant {
  const rng = mulberry32(seed)
  const used = new Set<string>()
  const adv = difficulty === 'advanced'
  const sections: ExamSection[] = formatOf(kind).sections.map((sec) => ({
    kicker: sec.kicker,
    title: sec.title,
    items: sec.slots.map((slot) => {
      const usable = slot.sources.filter((s) => (adv ? s.adv : s.basic).length > 0)
      for (let attempt = 0; attempt < 50; attempt++) {
        const source = usable[Math.floor(rng() * usable.length)]
        const topic = topics.find((t) => t.id === source?.topic)
        const group = topic?.groups?.find((g) => g.id === source.group)
        if (!topic || !group) continue
        const levels = adv ? source.adv : source.basic
        const pool = topic.tasks.filter((t) => t.group === source.group && levels.includes(t.level) && (!source.tag || t.tag === source.tag) && !used.has(t.id))
        if (pool.length === 0) continue
        const task = pool[Math.floor(rng() * pool.length)]
        used.add(task.id)
        return {
          id: task.id,
          label: slot.label,
          topicId: topic.id,
          groupId: group.id,
          groupTitle: group.title,
          lessonStep: group.lessonStep ?? 0,
          task,
        }
      }
      throw new Error(`Не удалось подобрать задание для ${slot.label} (${kind})`)
    }),
  }))
  return { seed, difficulty, kind, sections }
}

export function gradeLabel(score: number, total: number): string {
  if (score === total) return 'Отлично! Все примеры верные.'
  if (score >= total - 1) return 'Очень хорошо, почти без ошибок.'
  if (score >= Math.ceil(total / 2)) return 'Неплохо, но есть над чем поработать. Смотри разбор ниже.'
  return 'Нужно повторить: разбери каждую ошибку ниже и пройди рекомендованные уроки.'
}
