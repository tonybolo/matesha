export type SheetItem = { name: string; tex: string; lhs?: string; rhs?: string }
export type SheetSection = { title: string; items: SheetItem[] }

const files = import.meta.glob('../../../content/cheatsheet.yaml', {
  import: 'default',
  eager: true,
}) as Record<string, { sections: SheetSection[] }>

export const cheatsheet: SheetSection[] = Object.values(files)[0]?.sections ?? []

/** Таблицы: квадраты 1–20 и кубы 1–10 (считаются, а не вводятся вручную). */
export const squares = Array.from({ length: 20 }, (_, i) => ({ n: i + 1, v: (i + 1) ** 2 }))
export const cubes = Array.from({ length: 10 }, (_, i) => ({ n: i + 1, v: (i + 1) ** 3 }))
