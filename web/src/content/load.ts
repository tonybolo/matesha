import type { Task, Topic } from './types'

const files = import.meta.glob('../../../content/algebra8/*.yaml', {
  import: 'default',
  eager: true,
}) as Record<string, Topic>

export const topics: Topic[] = Object.values(files).sort((a, b) => a.order - b.order)

export function getTopic(id: string): Topic | undefined {
  return topics.find((t) => t.id === id)
}

export function taskById(topic: Topic, id: string): Task | undefined {
  return topic.tasks.find((t) => t.id === id)
}
