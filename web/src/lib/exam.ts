import type { Task, Topic } from '../content/types'
import { mulberry32 } from './equivalence'

export type Difficulty = 'basic' | 'advanced'

export type ExamItem = {
  id: string
  /** Номер задания и буква: «1а», «2б», … */
  label: string
  topicId: string
  groupId: string
  groupTitle: string
  lessonStep: number
  task: Task
}

export type ExamSection = { title: string; items: ExamItem[] }
export type ExamVariant = { seed: number; difficulty: Difficulty; sections: ExamSection[] }

type Source = { topic: string; group: string; levels: [Task['level'][], Task['level'][]] }
// levels: [для «как в тетради», для «посложнее»]

const PLAN: { title: string; parts: [Source[], Source[]] }[] = [
  {
    title: 'Сравните числа',
    parts: [
      [{ topic: '03-roots-compare', group: 'cmp', levels: [[1], [2]] }],
      [
        { topic: '03-roots-compare', group: 'cmp', levels: [[2], [3]] },
        { topic: '03-roots-compare', group: 'ord', levels: [[1, 2], [2, 3]] },
        { topic: '03-roots-compare', group: 'rootnum', levels: [[2], [3]] },
      ],
    ],
  },
  {
    title: 'Упростите выражение',
    parts: [
      [
        { topic: '04-roots-simplify', group: 'dec', levels: [[1], [2]] },
        { topic: '04-roots-simplify', group: 'val2', levels: [[1, 2], [2, 3]] },
        { topic: '04-roots-simplify', group: 'out', levels: [[1, 2], [2, 3]] },
      ],
      [
        { topic: '04-roots-simplify', group: 'dec', levels: [[2], [3]] },
        { topic: '04-roots-simplify', group: 'val', levels: [[1, 2], [2, 3]] },
        { topic: '04-roots-simplify', group: 'rat', levels: [[1, 2], [2, 3]] },
        { topic: '04-roots-simplify', group: 'sq', levels: [[1, 2], [2, 3]] },
      ],
    ],
  },
  {
    title: 'Решите квадратное уравнение',
    parts: [
      [
        { topic: '05-quadratic', group: 'dsc', levels: [[2], [3]] },
        { topic: '05-quadratic', group: 'dsc', levels: [[1], [2]] },
      ],
      [
        { topic: '05-quadratic', group: 'dsc', levels: [[2], [3]] },
        { topic: '05-quadratic', group: 'brk', levels: [[1, 2], [2, 3]] },
        { topic: '05-quadratic', group: 'nbx', levels: [[2], [3]] },
        { topic: '05-quadratic', group: 'inc', levels: [[2], [3]] },
      ],
    ],
  },
]

export const PARTS = ['а', 'б'] as const

/** Собирает вариант контрольной: 3 задания по 2 примера. Один и тот же seed даёт один и тот же вариант. */
export function buildExam(topics: Topic[], seed: number, difficulty: Difficulty): ExamVariant {
  const rng = mulberry32(seed)
  const used = new Set<string>()
  const idx = difficulty === 'basic' ? 0 : 1
  const sections: ExamSection[] = PLAN.map((sec, si) => ({
    title: sec.title,
    items: sec.parts.map((sources, pi) => {
      for (let attempt = 0; attempt < 50; attempt++) {
        const src = sources[Math.floor(rng() * sources.length)]
        const topic = topics.find((t) => t.id === src.topic)
        const group = topic?.groups?.find((g) => g.id === src.group)
        if (!topic || !group) continue
        const pool = topic.tasks.filter((t) => t.group === src.group && src.levels[idx].includes(t.level) && !used.has(t.id))
        if (pool.length === 0) continue
        const task = pool[Math.floor(rng() * pool.length)]
        used.add(task.id)
        return {
          id: task.id,
          label: `${si + 1}${PARTS[pi]}`,
          topicId: topic.id,
          groupId: group.id,
          groupTitle: group.title,
          lessonStep: group.lessonStep ?? 0,
          task,
        }
      }
      throw new Error(`Не удалось подобрать задание для ${si + 1}${PARTS[pi]}`)
    }),
  }))
  return { seed, difficulty, sections }
}

export const EXAM_MINUTES = 40

export function gradeLabel(score: number, total: number): string {
  if (score === total) return 'Отлично! Все примеры верные.'
  if (score >= total - 1) return 'Очень хорошо, почти без ошибок.'
  if (score >= Math.ceil(total / 2)) return 'Неплохо, но есть над чем поработать. Смотри разбор ниже.'
  return 'Нужно повторить: разбери каждую ошибку ниже и пройди рекомендованные уроки.'
}
