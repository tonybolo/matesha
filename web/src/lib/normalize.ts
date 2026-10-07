const LOOKALIKES: Record<string, string> = {
  а: 'a',
  с: 'c',
  о: 'o',
  р: 'p',
  х: 'x',
  у: 'y',
  к: 'k',
  м: 'm',
  т: 't',
}

const FUNCTIONS = ['sqrt', 'abs']

/**
 * Приводит ввод ребёнка к синтаксису mathjs:
 * русские буквы-двойники, знаки − × ÷ √ ², десятичная запятая,
 * слитное умножение переменных (ab → a*b).
 */
export function normalizeInput(raw: string): string {
  let s = raw.trim().toLowerCase()
  s = s.replace(/[а-я]/g, (ch) => LOOKALIKES[ch] ?? ch)
  s = s.replace(/[−–—]/g, '-')
  s = s.replace(/[×·∙⋅]/g, '*')
  s = s.replace(/[÷:]/g, '/')
  s = s.replace(/²/g, '^2').replace(/³/g, '^3')
  s = s.replace(/√\s*\(/g, 'sqrt(')
  s = s.replace(/√\s*(\d+(?:\.\d+)?|[a-z])/g, 'sqrt($1)')
  s = s.replace(/(\d),(\d)/g, '$1.$2')
  // ab → a b (слитное умножение), но sqrt/abs остаются функциями
  s = s.replace(/[a-z]+/g, (word) => {
    if (FUNCTIONS.includes(word)) return word
    return word.split('').join(' ')
  })
  // x(x+3) и (a-b)(a+b) — это произведения, а не вызов функции
  s = s.replace(/\)\s*\(/g, ')*(')
  s = s.replace(/(?<![a-z])([a-z])\s*\(/g, '$1*(')
  return s
}
