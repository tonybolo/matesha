import { parse } from 'yaml'
import type { Task, Topic } from './types'

const files = import.meta.glob('../../../content/algebra8/*.yaml', {
  query: '?raw',
  import: 'default',
  eager: true,
}) as Record<string, string>

export const topics: Topic[] = Object.values(files)
  .map((raw) => parse(raw) as Topic)
  .sort((a, b) => a.order - b.order)

export function getTopic(id: string): Topic | undefined {
  return topics.find((t) => t.id === id)
}

export function taskById(topic: Topic, id: string): Task | undefined {
  return topic.tasks.find((t) => t.id === id)
}
