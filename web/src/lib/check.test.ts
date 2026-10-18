import { describe, expect, it } from 'vitest'
import { checkAnswer, MESSAGES, parseNumberSet } from './check'
import { toTex } from './expr'
import { normalizeInput } from './normalize'
import { radicalIssue } from './radical'
import { tryParse } from './expr'

const ok = (input: string, answer: string, reduce = false) =>
  checkAnswer(input, answer, 'expr', { reduce }).status

describe('normalizeInput', () => {
  it('склеивает переменные и чинит символы', () => {
    expect(normalizeInput('2ab')).toBe('2a b')
    expect(normalizeInput('3х²')).toBe('3x^2')
    expect(normalizeInput('(a−b)÷2')).toBe('(a-b)/2')
    expect(normalizeInput('√2')).toBe('sqrt(2)')
    expect(normalizeInput('0,5x')).toBe('0.5x')
    expect(normalizeInput('x(y(z))')).toBe('x*(y*(z))')
    expect(normalizeInput('sqrt(x)(x+1)')).toBe('sqrt(x)*(x+1)')
    expect(normalizeInput('a(b+c)')).toBe('a*(b+c)')
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

describe('числовые подсказки', () => {
  const run = (input: string, answer: string) => checkAnswer(input, answer, 'expr')
  it('точное десятичное значение засчитывается', () => {
    expect(run('1.5', '3/2').status).toBe('correct')
    expect(run('0,25', '1/4').status).toBe('correct')
  })
  it('округление не засчитывается, но и не считается ошибкой', () => {
    expect(run('0.67', '2/3').status).toBe('approx')
    expect(run('0,6667', '2/3').status).toBe('approx')
    expect(run('0.7', '2/3').status).toBe('wrong')
  })
  it('перевёрнутая дробь', () => {
    const r = run('1.5', '2/3')
    expect(r.status).toBe('wrong')
    expect(r.message).toContain('перевёрнута')
    expect(run('3/2', '2/3').message).toContain('перевёрнута')
  })
  it('обычный неверный ответ без особых подсказок', () => {
    expect(run('5', '2/3').message).toBe(MESSAGES.wrong)
    expect(run('1.51', '1.5').message).toBe(MESSAGES.wrong)
  })
})

describe('сравнение, выбор и порядок', () => {
  it('знак сравнения', () => {
    expect(checkAnswer('<', '<', 'compare').status).toBe('correct')
    expect(checkAnswer('>', '<', 'compare').status).toBe('wrong')
    expect(checkAnswer('', '<', 'compare').status).toBe('empty')
    expect(checkAnswer('меньше', '<', 'compare').status).toBe('invalid')
  })
  it('выбор варианта', () => {
    expect(checkAnswer('2', '2', 'choice').status).toBe('correct')
    expect(checkAnswer('1', '2', 'choice').status).toBe('wrong')
  })
  it('порядок плиток', () => {
    const items = ['sqrt(51)', '7', 'sqrt(101/2)']
    expect(checkAnswer('1,2,0', '1,2,0', 'order', { items }).status).toBe('correct')
    expect(checkAnswer('0,1,2', '1,2,0', 'order', { items }).status).toBe('wrong')
    expect(checkAnswer('1,2', '1,2,0', 'order', { items }).status).toBe('invalid')
  })
})

describe('простейший вид с корнями', () => {
  const issue = (s: string) => radicalIssue(tryParse(s)!.node)
  it('допустимое', () => {
    expect(issue('6*sqrt(2)')).toBeNull()
    expect(issue('3+2*sqrt(5)')).toBeNull()
    expect(issue('(sqrt(2)+1)/2')).toBeNull()
    expect(issue('-4')).toBeNull()
  })
  it('недопустимое', () => {
    expect(issue('sqrt(72)')).toContain('множители')
    expect(issue('sqrt(16)')).toContain('нацело')
    expect(issue('1/sqrt(2)')).toContain('знаменателе')
    expect(issue('sqrt(1/2)')).toContain('дроби')
    expect(issue('sqrt(0.25)')).toContain('дроби')
  })
  it('проверка ответа требует упрощения', () => {
    expect(checkAnswer('sqrt(72)', '6*sqrt(2)', 'expr', { radical: true }).status).toBe('notSimplified')
    expect(checkAnswer('6sqrt(2)', '6*sqrt(2)', 'expr', { radical: true }).status).toBe('correct')
    expect(checkAnswer('√72', '6*sqrt(2)', 'expr').status).toBe('correct')
  })
})

describe('мусорный ввод не роняет проверку', () => {
  const garbage = ['()', '1/0', '2^^3', '😀', 'x=', 'sqrt(-1)', '1e400', '9^9^9^9', 'x/', '/x', ')(', '((((((((((x', 'a'.repeat(300), '1,2,3', ';;;', 'x;y', 'abs(', 'sin(x)', '5!', 'x%2', '[1,2]', '{a:1}', 'x:=3']
  for (const g of garbage) {
    it(JSON.stringify(g).slice(0, 30), () => {
      for (const kind of ['expr', 'roots'] as const) {
        expect(() => checkAnswer(g, kind === 'expr' ? '(x+1)/x' : '3; -3', kind, { reduce: true })).not.toThrow()
      }
      expect(checkAnswer(g, '(x+1)/x', 'expr', { reduce: true }).status).not.toBe('correct')
    })
  }
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
  it('разбор: подписи x₁ =, «ответ:», «или»', () => {
    expect(parseNumberSet('x1 = 2, x2 = 3')).toEqual([2, 3])
    expect(parseNumberSet('x₁=2; x₂=-3')).toEqual([-3, 2])
    expect(parseNumberSet('ответ: 2 или 3')).toEqual([2, 3])
    expect(parseNumberSet('x=2 или x=3')).toEqual([2, 3])
    expect(parseNumberSet('Корни: 5; -5')).toEqual([-5, 5])
  })
  it('подсказки: не все корни, лишние, корней нет', () => {
    expect(checkAnswer('3', '3; -3', 'roots').message).toBe(MESSAGES.rootsMissing)
    expect(checkAnswer('3; -3; 5', '3; -3', 'roots').message).toBe(MESSAGES.rootsExtra)
    expect(checkAnswer('2', 'нет', 'roots').message).toBe(MESSAGES.rootsNone)
    expect(checkAnswer('нет', '2; 5', 'roots').message).toBe(MESSAGES.rootsHave)
    expect(checkAnswer('7; 9', '3; -3', 'roots').message).toBe(MESSAGES.wrong)
    for (const m of Object.values(MESSAGES)) expect(m.includes('$')).toBe(false)
  })
  it('проверка', () => {
    expect(checkAnswer('-3;3', '3; -3', 'roots').status).toBe('correct')
    expect(checkAnswer('3', '3; -3', 'roots').status).toBe('wrong')
    expect(checkAnswer('нет корней', 'нет', 'roots').status).toBe('correct')
  })
})

describe('удобство ввода', () => {
  it('«x = 5» и «ответ: 5» принимаются как 5, если ответ — число', () => {
    expect(checkAnswer('x = 5', '5', 'expr').status).toBe('correct')
    expect(checkAnswer('ответ: 5', '5', 'expr').status).toBe('correct')
    expect(checkAnswer('p=12', '12', 'expr').status).toBe('correct')
    expect(checkAnswer('x = 6', '5', 'expr').status).toBe('wrong')
  })
  it('смешанное число просим записать дробью', () => {
    const r = checkAnswer('2 1/3', '7/3', 'expr')
    expect(r.status).toBe('invalid')
    expect(r.message).toBe(MESSAGES.mixed)
    expect(checkAnswer('-1 1/2', '-3/2', 'expr').message).toBe(MESSAGES.mixed)
    expect(checkAnswer('2 1/3', '7/3', 'roots').message).toBe(MESSAGES.mixed)
    expect(checkAnswer('7/3', '7/3', 'expr').status).toBe('correct')
  })
  it('единицы измерения в конце числового ответа не мешают', () => {
    expect(checkAnswer('68 см', '68', 'expr').status).toBe('correct')
    expect(checkAnswer('19 кустов', '19', 'expr').status).toBe('correct')
    expect(checkAnswer('x = 7 м', '7', 'expr').status).toBe('correct')
    expect(checkAnswer('69 см', '68', 'expr').status).toBe('wrong')
  })
  it('градусы и квадратные единицы: 40°, 40 градусов, 24 см², 24 см2, 24 кв. см', () => {
    for (const a of ['40°', '40 °', '40 градусов', '40 град', 'угол = 40°', '40']) expect(checkAnswer(a, '40', 'expr').status, a).toBe('correct')
    for (const a of ['24 см²', '24 см2', '24 см^2', '24 кв. см', '24 кв см', '24 м²', 'S = 24 дм2']) expect(checkAnswer(a, '24', 'expr').status, a).toBe('correct')
    for (const a of ['угол A = 40°', '∠A = 40°', '∠ABC=40', 'AB = 40 см', 'угол 40', 'P = 40', 'E(X) = 40', 'D(X)=40', 'σ = 40', 'дисперсия = 40', 'ожидание: 40']) {
      expect(checkAnswer(a, '40', 'expr').status, a).toBe('correct')
    }
    expect(checkAnswer('E(X) = 3,5', '7/2', 'expr').status).toBe('correct')
    expect(checkAnswer('41°', '40', 'expr').status).toBe('wrong')
    expect(checkAnswer('7,5 см', '15/2', 'expr').status).toBe('correct')
  })
  it('sqrt3 без скобок и ± в корнях', () => {
    expect(checkAnswer('5sqrt3', '5*sqrt(3)', 'expr').status).toBe('correct')
    expect(checkAnswer('sqrt 12', '2*sqrt(3)', 'expr').status).toBe('correct')
    expect(parseNumberSet('±3')).toEqual([-3, 3])
    expect(parseNumberSet('x = ±2')).toEqual([-2, 2])
    expect(checkAnswer('±3', '3; -3', 'roots').status).toBe('correct')
    expect(checkAnswer('(-3±√7)/2', '(-3+sqrt(7))/2; (-3-sqrt(7))/2', 'roots').status).toBe('correct')
    expect(checkAnswer('x=±3', '3', 'roots').status).toBe('wrong')
  })
  it('в ответах с буквами метка не отрезается', () => {
    expect(checkAnswer('x+1', 'x+1', 'expr').status).toBe('correct')
    expect(checkAnswer('2x', '2*x', 'expr').status).toBe('correct')
  })
})

describe('toTex', () => {
  it('рисует дробь', () => {
    expect(toTex('(x+1)/(x-2)')).toBe('\\frac{x+1}{x-2}')
    expect(toTex('3ab^2/(2x)')).toBe('\\frac{3ab^{2}}{2x}')
    expect(toTex('x(x+3)')).toBe('x\\left(x+3\\right)')
    expect(toTex('2*3')).toBe('2\\cdot 3')
    expect(toTex('0,5x')).toBe('0{,}5x')
    expect(toTex('sqrt(36)*sqrt(81)')).toBe('\\sqrt{36}\\cdot \\sqrt{81}')
    expect(toTex('3*sqrt(2)')).toBe('3\\sqrt{2}')
    expect(toTex('x*sqrt(2)')).toBe('x\\sqrt{2}')
    expect(toTex('((')).toBeNull()
  })
})
