import type { Subject } from './types'

/** Разделы в том порядке, в котором они идут на главной. */
export const SUBJECTS: { id: Subject; title: string; icon: string }[] = [
  { id: 'algebra', title: 'Алгебра', icon: '➗' },
  { id: 'geometry', title: 'Геометрия', icon: '📐' },
  { id: 'stats', title: 'Вероятность и статистика', icon: '🎲' },
]

export const subjectOf = (s: Subject | undefined): Subject => s ?? 'algebra'

export function subjectTitle(s: Subject | undefined): string {
  return SUBJECTS.find((x) => x.id === subjectOf(s))?.title ?? ''
}
