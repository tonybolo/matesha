const gcd = (a: number, b: number): number => (b === 0 ? Math.abs(a) : gcd(b, a % b))

/** Число для TeX: десятичная запятая, обычный минус. */
export function texNum(v: number): string {
  return String(Math.round(v * 100) / 100).replace('.', '{,}')
}

/** Подстановка x в выражение ax+b: «5\cdot 2+5=15», «-16\cdot (-1)=16». */
export function substitutionTex(a: number, b: number, x: number): string {
  const xs = texNum(x)
  const head = a === 1 ? xs : a === -1 ? (x < 0 ? `-(${xs})` : `-${xs}`) : `${a}\\cdot ${x < 0 ? `(${xs})` : xs}`
  const tail = b === 0 ? '' : b > 0 ? `+${b}` : `-${-b}`
  return `${head}${tail}=${texNum(a * x + b)}`
}

/** Решение неравенства ax+b ≥ 0: «x ≥ -1», «x ≤ 0», «x ≥ -5/3» (граница — несократимая дробь). */
export function boundaryTex(a: number, b: number): string {
  let n = -b
  let d = a
  if (d < 0) {
    n = -n
    d = -d
  }
  const g = gcd(Math.abs(n), d)
  n /= g
  d /= g
  const value = d === 1 ? String(n) : `${n < 0 ? '-' : ''}\\dfrac{${Math.abs(n)}}{${d}}`
  return `x\\ ${a > 0 ? '\\ge' : '\\le'}\\ ${value}`
}
