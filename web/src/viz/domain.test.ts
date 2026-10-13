import katex from 'katex'
import { describe, expect, it } from 'vitest'
import { boundaryTex, substitutionTex, texNum } from './domain'

describe('подстановка x в ax+b', () => {
  it('записывает вычисление как в тетради', () => {
    expect(substitutionTex(5, 5, 2)).toBe('5\\cdot 2+5=15')
    expect(substitutionTex(-16, 0, 2)).toBe('-16\\cdot 2=-32')
    expect(substitutionTex(-16, 0, -1)).toBe('-16\\cdot (-1)=16')
    expect(substitutionTex(4, 0, 0.5)).toBe('4\\cdot 0{,}5=2')
    expect(substitutionTex(1, -3, 2)).toBe('2-3=-1')
    expect(substitutionTex(1, -3, -3)).toBe('-3-3=-6')
    expect(substitutionTex(-1, 5, 2)).toBe('-2+5=3')
    expect(substitutionTex(-1, 5, -2)).toBe('-(-2)+5=7')
  })
  it('результат после «=» всегда равен ax+b, формула собирается в KaTeX', () => {
    for (let a = -9; a <= 9; a++) {
      if (a === 0) continue
      for (let b = -9; b <= 9; b++) {
        for (let x = -8; x <= 8; x += 0.5) {
          const tex = substitutionTex(a, b, x)
          expect(() => katex.renderToString(tex, { throwOnError: true, strict: 'ignore' }), tex).not.toThrow()
          expect(Number(tex.slice(tex.lastIndexOf('=') + 1).replace('{,}', '.')), tex).toBeCloseTo(a * x + b, 9)
        }
      }
    }
  })
  it('числа с запятой', () => {
    expect(texNum(2.5)).toBe('2{,}5')
    expect(texNum(-0.5)).toBe('-0{,}5')
    expect(texNum(3)).toBe('3')
  })
})

describe('где корень существует', () => {
  it('граница: целая, нулевая и дробная, знак по знаку a', () => {
    expect(boundaryTex(5, 5)).toBe('x\\ \\ge\\ -1')
    expect(boundaryTex(-16, 0)).toBe('x\\ \\le\\ 0')
    expect(boundaryTex(1, -3)).toBe('x\\ \\ge\\ 3')
    expect(boundaryTex(-1, 5)).toBe('x\\ \\le\\ 5')
    expect(boundaryTex(3, 5)).toBe('x\\ \\ge\\ -\\dfrac{5}{3}')
    expect(boundaryTex(-2, 5)).toBe('x\\ \\le\\ \\dfrac{5}{2}')
    expect(boundaryTex(4, 6)).toBe('x\\ \\ge\\ -\\dfrac{3}{2}')
  })
  it('граница действительно разделяет подходящие и неподходящие x', () => {
    for (let a = -9; a <= 9; a++) {
      if (a === 0) continue
      for (let b = -9; b <= 9; b++) {
        const tex = boundaryTex(a, b)
        expect(() => katex.renderToString(tex, { throwOnError: true, strict: 'ignore' }), tex).not.toThrow()
        const edge = -b / a
        expect(a * edge + b).toBeCloseTo(0, 9)
        const inside = a > 0 ? edge + 1 : edge - 1
        const outside = a > 0 ? edge - 1 : edge + 1
        expect(a * inside + b).toBeGreaterThanOrEqual(0)
        expect(a * outside + b).toBeLessThan(0)
      }
    }
  })
})
