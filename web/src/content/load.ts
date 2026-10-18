import { SUBJECTS, subjectOf } from './subjects'
import type { Subject, Task, Topic, TaskGroup } from './types'

// Папки предметов: content/algebra8, content/geometry8, content/stats8 (имя заканчивается на 8 — класс).
const files = import.meta.glob('../../../content/*8/*.yaml', {
  import: 'default',
  eager: true,
}) as Record<string, Topic>

// Сгенерированные задания (tools/generators): добавляются к теме по полю topic.
const generated = import.meta.glob('../../../content/*8/generated/*.json', {
  import: 'default',
  eager: true,
}) as Record<string, { topic: string; groups?: TaskGroup[]; tasks: Task[] }>

const rank = (t: Topic) => SUBJECTS.findIndex((s) => s.id === subjectOf(t.subject))

/** Темы всех разделов: сначала по разделам (алгебра, геометрия, статистика), внутри раздела по номеру. */
export const topics: Topic[] = Object.values(files)
  .map((t) => ({ ...t, subject: subjectOf(t.subject), tasks: t.tasks ?? [], check: t.check ?? [] }))
  .sort((a, b) => rank(a) - rank(b) || a.order - b.order)

for (const g of Object.values(generated)) {
  const topic = topics.find((t) => t.id === g.topic)
  if (!topic) throw new Error(`Нет темы ${g.topic} для сгенерированных заданий`)
  topic.groups = [...(topic.groups ?? []), ...(g.groups ?? [])]
  topic.tasks = [...topic.tasks, ...g.tasks]
}

export function topicsOf(subject: Subject): Topic[] {
  return topics.filter((t) => subjectOf(t.subject) === subject)
}

export function getTopic(id: string): Topic | undefined {
  return topics.find((t) => t.id === id)
}

export function taskById(topic: Topic, id: string): Task | undefined {
  return topic.tasks.find((t) => t.id === id)
}
