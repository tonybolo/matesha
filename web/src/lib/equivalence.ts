import type { Parsed } from './expr'

function mulberry32(seed: number) {
  let a = seed
  return () => {
    a |= 0
    a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

const SAMPLE_VALUES = [-9, -7, -5, -4, -3, -2, -1.5, -1, -0.5, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 7, 9, 11]

function close(a: number, b: number): boolean {
  return Math.abs(a - b) <= 1e-8 * Math.max(1, Math.abs(a), Math.abs(b))
}

/**
 * Равенство выражений как функций: сравниваем значения в случайных точках,
 * пропуская точки, где хотя бы одно выражение не определено (ОДЗ).
 */
export function equivalent(a: Parsed, b: Parsed): boolean {
  const vars = [...new Set([...a.vars, ...b.vars])]
  const rng = mulberry32(12345)
  const attempts = vars.length === 0 ? 1 : 80
  let valid = 0
  for (let i = 0; i < attempts; i++) {
    const scope: Record<string, number> = {}
    for (const v of vars) scope[v] = SAMPLE_VALUES[Math.floor(rng() * SAMPLE_VALUES.length)]
    const va = a.fn(scope)
    const vb = b.fn(scope)
    if (va === null || vb === null) continue
    if (!close(va, vb)) return false
    valid++
  }
  return vars.length === 0 ? valid === 1 : valid >= 6
}

export { mulberry32 }
