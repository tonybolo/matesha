import { describe, expect, it } from 'vitest'
import { checkAnswer, parseNumberSet } from './check'
import { toTex } from './expr'
import { normalizeInput } from './normalize'

const ok = (input: string, answer: string, reduce = false) =>
  checkAnswer(input, answer, 'expr', { reduce }).status

describe('normalizeInput', () => {
  it('склеивает переменные и чинит символы', () => {
    expect(normalizeInput('2ab')).toBe('2a b')
    expect(normalizeInput('3х²')).toBe('3x^2')
    expect(normalizeInput('(a−b)÷2')).toBe('(a-b)/2')
    expect(normalizeInput('√2')).toBe('sqrt(2)')
    expect(normalizeInput('0,5x')).toBe('0.5x')
  })
})

describe('эквивалентность выражений', () => {
  it('одинаковые и перестановочные формы', () => {
    expect(ok('(x+2)/(x-3)', '(x+2)/(x-3)')).toBe('correct')
    expect(ok('(2+x)/(-3+x)', '(x+2)/(x-3)')).toBe('correct')
    expect(ok('2ab/(3b)', '2a/3')).toBe('correct')
    expect(ok('х/2', '0.5x')).toBe('correct')
    expect(ok('3/4', '0,75')).toBe('correct')
  })
  it('неверные ответы', () => {
    expect(ok('(x+2)/(x+3)', '(x+2)/(x-3)')).toBe('wrong')
    expect(ok('x+3', '3')).toBe('wrong')
    expect(ok('x/3', '1')).toBe('wrong')
  })
  it('мусор', () => {
    expect(ok('((x', 'x')).toBe('invalid')
    expect(ok('import(1)', 'x')).toBe('invalid')
    expect(ok('x=2', 'x')).toBe('invalid')
    expect(ok('', 'x')).toBe('empty')
  })
  it('сокращённую дробь заставляет сократить', () => {
    expect(ok('(x-3)/x', '(x-3)/x', true)).toBe('correct')
    expect(ok('(x-3)(x+3)/(x(x+3))', '(x-3)/x', true)).toBe('notReduced')
    expect(ok('(x^2-9)/(x^2+3x)', '(x-3)/x', true)).toBe('notReduced')
    expect(ok('(x-3)/x', '(x-3)/x', true)).toBe('correct')
    expect(ok('(x^2-9)/(x+3)', 'x-3', true)).toBe('notReduced')
    expect(ok('x-3', 'x-3', true)).toBe('correct')
    expect(ok('-(x-y)/(x+y)', '(y-x)/(x+y)', true)).toBe('correct')
  })
  it('сумма дробей — не «одна дробь»', () => {
    expect(ok('1/x+1/(3x)', '4/(3x)', true)).toBe('notSingle')
    expect(ok('4/(3x)', '4/(3x)', true)).toBe('correct')
    expect(ok('(3+1)/(3x)', '4/(3x)', true)).toBe('correct')
  })
  it('несколько переменных', () => {
    expect(ok('(a+b)/(a-b)', '(b+a)/(-b+a)', true)).toBe('correct')
    expect(ok('(a^2+b^2)/(a^2-b^2)', '(a^2+b^2)/((a-b)(a+b))', true)).toBe('correct')
  })
})

describe('наборы чисел', () => {
  it('разбор', () => {
    expect(parseNumberSet('3; -3')).toEqual([-3, 3])
    expect(parseNumberSet('x=4')).toEqual([4])
    expect(parseNumberSet('нет')).toEqual([])
    expect(parseNumberSet('1/2; 0,25')).toEqual([0.25, 0.5])
    expect(parseNumberSet('4, -4')).toEqual([-4, 4])
    expect(parseNumberSet('два')).toBeNull()
  })
  it('проверка', () => {
    expect(checkAnswer('-3;3', '3; -3', 'roots').status).toBe('correct')
    expect(checkAnswer('3', '3; -3', 'roots').status).toBe('wrong')
    expect(checkAnswer('нет корней', 'нет', 'roots').status).toBe('correct')
  })
})

describe('toTex', () => {
  it('рисует дробь', () => {
    expect(toTex('(x+1)/(x-2)')).toBe('\\frac{x+1}{x-2}')
    expect(toTex('3ab^2/(2x)')).toBe('\\frac{3ab^{2}}{2x}')
    expect(toTex('x(x+3)')).toBe('x\\left(x+3\\right)')
    expect(toTex('2*3')).toBe('2\\cdot 3')
    expect(toTex('0,5x')).toBe('0{,}5x')
    expect(toTex('((')).toBeNull()
  })
})
