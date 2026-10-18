import { SUBJECTS } from './subjects'
import type { Subject } from './types'

export type SheetItem = { name: string; tex: string; lhs?: string; rhs?: string }
export type SheetSection = { title: string; items: SheetItem[] }
export type SheetGroup = { subject: Subject; title: string; sections: SheetSection[] }

// Шпаргалка лежит по одному файлу на раздел: content/cheatsheet/algebra.yaml, geometry.yaml, stats.yaml
const files = import.meta.glob('../../../content/cheatsheet/*.yaml', {
  import: 'default',
  eager: true,
}) as Record<string, { subject?: Subject; sections: SheetSection[] }>

export const cheatsheetGroups: SheetGroup[] = SUBJECTS.map((s) => ({
  subject: s.id,
  title: s.title,
  sections: Object.values(files)
    .filter((f) => (f.subject ?? 'algebra') === s.id)
    .flatMap((f) => f.sections),
})).filter((g) => g.sections.length > 0)

export const cheatsheet: SheetSection[] = cheatsheetGroups.flatMap((g) => g.sections)

/** Таблицы: квадраты 1–20 и кубы 1–10 (считаются, а не вводятся вручную). */
export const squares = Array.from({ length: 20 }, (_, i) => ({ n: i + 1, v: (i + 1) ** 2 }))
export const cubes = Array.from({ length: 10 }, (_, i) => ({ n: i + 1, v: (i + 1) ** 3 }))
