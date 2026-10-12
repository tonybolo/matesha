import type { Task, Topic, TaskGroup } from './types'

const files = import.meta.glob('../../../content/algebra8/*.yaml', {
  import: 'default',
  eager: true,
}) as Record<string, Topic>

// Сгенерированные задания (tools/generators): добавляются к теме по полю topic.
const generated = import.meta.glob('../../../content/algebra8/generated/*.json', {
  import: 'default',
  eager: true,
}) as Record<string, { topic: string; groups?: TaskGroup[]; tasks: Task[] }>

export const topics: Topic[] = Object.values(files).sort((a, b) => a.order - b.order)

for (const g of Object.values(generated)) {
  const topic = topics.find((t) => t.id === g.topic)
  if (!topic) throw new Error(`Нет темы ${g.topic} для сгенерированных заданий`)
  topic.groups = [...(topic.groups ?? []), ...(g.groups ?? [])]
  topic.tasks = [...topic.tasks, ...g.tasks]
}

export function getTopic(id: string): Topic | undefined {
  return topics.find((t) => t.id === id)
}

export function taskById(topic: Topic, id: string): Task | undefined {
  return topic.tasks.find((t) => t.id === id)
}
