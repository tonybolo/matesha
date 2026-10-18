// Сквозной прогон темы в браузере на телефонном экране 390×844 (светлая и тёмная тема):
// все шаги урока (нажимает все кнопки картинок, ищет «сырой» TeX, горизонтальную прокрутку), проверка верными ответами,
// по три задания в каждой группе тренажёра, ошибки консоли.
//
// Использование (из корня репозитория, сайт уже собран и запущен: cd web && npm run build && npx vite preview --port 4173):
//   PLAYWRIGHT_MODULE=/путь/к/playwright/index.mjs CHROMIUM_PATH=/путь/к/chrome \
//   node tools/e2e/topic-e2e.mjs <каталог для скриншотов> <id темы> <папка content/…8> [порт]
// Например: node tools/e2e/topic-e2e.mjs /tmp/shots geo-01-quadrilaterals geometry8 4173
// CONTENT_ROOT — путь к другой копии content/ (например, к worktree). Код выхода 1, если есть строки FAIL.
import { readFileSync, mkdirSync, existsSync } from 'node:fs'
import { createRequire } from 'node:module'
import { fileURLToPath } from 'node:url'

const { chromium } = await import(process.env.PLAYWRIGHT_MODULE ?? 'playwright')
const ROOT = fileURLToPath(new URL('../../', import.meta.url))
const require = createRequire(`${ROOT}web/package.json`)
const { parse } = require('yaml')

const [SCR, TOPIC, DIR, PORT = '4173'] = process.argv.slice(2)
mkdirSync(`${SCR}/shots`, { recursive: true })
const BASE = `http://localhost:${PORT}/#/t/${TOPIC}`
const CONTENT = process.env.CONTENT_ROOT ?? `${ROOT}content`
const yamlPath = `${CONTENT}/${DIR}/${TOPIC}.yaml`
const topic = parse(readFileSync(yamlPath, 'utf8'))
const genPath = `${CONTENT}/${DIR}/generated/${TOPIC}.json`
const gen = existsSync(genPath) ? JSON.parse(readFileSync(genPath, 'utf8')) : { groups: [], tasks: [] }

const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {})
let fails = 0
const ok = (c, msg) => { if (!c) { fails++; console.log('FAIL ' + msg) } else if (process.env.VERBOSE) console.log('ok   ' + msg) }

async function run(scheme) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, locale: 'ru-RU', colorScheme: scheme })
  const page = await ctx.newPage()
  const errors = []
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message))
  page.on('console', (m) => { if (m.type() === 'error') errors.push('console: ' + m.text()) })
  await page.addInitScript(() => {
    if (!localStorage.getItem('matesha.v1')) localStorage.setItem('matesha.v1', JSON.stringify({ v: 1, name: 'Даня', xp: 0, streak: 0, lastDay: null, topics: {}, skills: {}, exams: [] }))
  })

  const noOverflow = async (where) => {
    const r = await page.evaluate(() => {
      const w = window.innerWidth
      const bad = [...document.querySelectorAll('main *')]
        .filter((el) => el.getBoundingClientRect().right > w + 1 && !el.closest('.katex-display, .readout'))
        .slice(0, 3)
        .map((el) => `${el.tagName.toLowerCase()}.${String(el.className).slice(0, 30)}`)
      return { sw: document.documentElement.scrollWidth, w, bad }
    })
    ok(r.sw <= r.w + 1, `${scheme}: ${where}: горизонтальная прокрутка (${r.sw} > ${r.w}) ${r.bad.join(' | ')}`)
  }

  // ---------- урок ----------
  console.log(`[${scheme}] урок: ${topic.steps.length} шагов`)
  for (let i = 0; i < topic.steps.length; i++) {
    await page.goto(`${BASE}/learn?step=${i}`)
    await page.reload()
    await page.waitForSelector('.step-body')
    const body = (await page.locator('.step-body').innerText()).replace(/\s+/g, ' ')
    ok(!/\\\\|\\[a-zA-Z]+|sqrt\b|\bfrac\b/.test(body), `${scheme}: шаг ${i + 1}: «сырой» TeX на экране`)
    ok(!/Картинки «[^»]+» пока нет/.test(body), `${scheme}: шаг ${i + 1}: картинки нет (${body.slice(0, 40)})`)
    await noOverflow(`шаг ${i + 1}`)
    const vizCount = await page.locator('.viz').count()
    for (let v = 0; v < vizCount; v++) {
      const viz = page.locator('.viz').nth(v)
      const before = (await viz.innerText()).replace(/\s+/g, ' ')
      // обезьяний тест: нажимаем все кнопки по очереди, двигаем ползунки, щёлкаем по картинкам
      const nb = await viz.locator('button:not([disabled])').count()
      const seen = new Set([before])
      const snap = async () => seen.add((await viz.innerText()).replace(/\s+/g, ' '))
      for (let b = 0; b < Math.min(nb, 60); b++) {
        const btn = viz.locator('button:not([disabled])').nth(b % Math.max(1, await viz.locator('button:not([disabled])').count()))
        await btn.click({ timeout: 3000 }).catch(() => {})
        await snap()
      }
      for (const r of await viz.locator('input[type=range]').all()) {
        for (const frac of [0, 1, 0.5]) {
          await r.evaluate((el, f) => {
            const min = Number(el.min || 0), max = Number(el.max || 100)
            const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set
            set.call(el, String(min + (max - min) * f))
            el.dispatchEvent(new Event('input', { bubbles: true }))
          }, frac)
          await snap()
        }
      }
      for (const svg of await viz.locator('svg').all()) {
        const box = await svg.boundingBox()
        if (box) {
          ok(box.x >= -1 && box.x + box.width <= 391, `${scheme}: шаг ${i + 1}, картинка ${v + 1}: svg вылезает за экран (${Math.round(box.x)}…${Math.round(box.x + box.width)})`)
          await page.mouse.click(box.x + box.width * 0.4, box.y + box.height * 0.5).catch(() => {})
          await snap()
        }
      }
      ok(seen.size > 1, `${scheme}: шаг ${i + 1}, картинка ${v + 1}: после нажатий текст под картинкой ни разу не изменился`)
      await noOverflow(`шаг ${i + 1}, картинка ${v + 1}`)
    }
    // раскрываем примеры
    for (const b of await page.locator('.example-actions .btn:has-text("Показать всё")').all()) await b.click().catch(() => {})
    await page.screenshot({ path: `${SCR}/shots/${scheme}-learn-${String(i + 1).padStart(2, '0')}.png`, fullPage: true })
  }

  // ---------- проверка ----------
  console.log(`[${scheme}] проверка: ${topic.check.length} вопросов`)
  await page.goto(`${BASE}/check`)
  await page.reload()
  let right = 0
  for (let q = 0; q < topic.check.length; q++) {
    const item = topic.check[q]
    await page.waitForFunction((n) => new RegExp(`вопрос\\s*${n}\\s*из`, 'i').test(document.querySelector('main').innerText), q + 1, { timeout: 10000 })
    const text = (await page.locator('.question').innerText()).replace(/\s+/g, ' ')
    ok(!/\\\\|\\[a-zA-Z]+|\bsqrt\b|\bfrac\b|\bge\d|\ble\d/.test(text), `${scheme}: вопрос ${q + 1}: «сырой» TeX (${text.slice(0, 60)})`)
    await noOverflow(`вопрос ${q + 1}`)
    if (item.kind === 'choice') await page.locator('.option').nth(item.correct).click()
    else {
      const kind = item.answerKind
      if (kind === 'compare') await page.locator('.sign', { hasText: item.answer }).click()
      else if (kind === 'choice') await page.locator('.option').nth(Number(item.answer)).click()
      else await page.locator('.answer-input input').fill(item.answer)
      await page.locator('.answer-input .btn.primary').click()
    }
    await page.waitForSelector('.feedback')
    const good = await page.locator('.feedback.ok').count()
    if (good) right++
    else ok(false, `${scheme}: вопрос ${q + 1} (${item.id}): верный ответ «${item.answer ?? item.correct}» не принят: ${(await page.locator('.feedback').innerText()).replace(/\s+/g, ' ').slice(0, 100)}`)
    if (q === 0) await page.screenshot({ path: `${SCR}/shots/${scheme}-check-q1.png`, fullPage: true })
    await page.locator('.feedback .btn.primary, .nav-row .btn.primary').first().click()
  }
  console.log(`[${scheme}] верно в проверке: ${right} из ${topic.check.length}`)
  await page.screenshot({ path: `${SCR}/shots/${scheme}-check-end.png`, fullPage: true })

  // ---------- тренажёр ----------
  console.log(`[${scheme}] тренажёр: ${gen.groups.length} групп`)
  await page.goto(`${BASE}/train`)
  await page.reload()
  await page.waitForSelector('.trainer')
  for (let gi = 0; gi < gen.groups.length; gi++) {
    const g = gen.groups[gi]
    await page.locator('.group').nth(gi).click()
    const tasks = gen.tasks.filter((t) => t.group === g.id)
    for (let k = 0; k < 3; k++) {
      await page.waitForSelector('.task')
      const t = tasks[k]
      const root = page.locator('.task')
      const ptext = (await root.locator('.q-prompt').innerText()).replace(/\s+/g, ' ')
      ok(!/\\\\|\\[a-zA-Z]+|\bsqrt\b|\bfrac\b|\{expr/.test(ptext), `${scheme}: ${t.id}: «сырой» TeX в условии (${ptext.slice(0, 60)})`)
      if (t.fig) ok((await root.locator('.figure > *').count()) > 0, `${scheme}: ${t.id}: рисунок «${t.fig.id}» не показан`)
      if (t.answerKind === 'compare') await root.locator('.sign', { hasText: t.answer }).click()
      else if (t.answerKind === 'choice') await root.locator('.option').nth(Number(t.answer)).click()
      else if (t.answerKind === 'order') {
        const remaining = t.items.map((_, i) => i)
        for (const idx of t.answer.split(',').map(Number)) {
          const pos = remaining.indexOf(idx)
          await root.locator('.order-row .tile').nth(pos).click()
          remaining.splice(pos, 1)
        }
      } else await root.locator('.answer-input input').fill(t.answer)
      await root.locator('.answer-input .btn.primary').click()
      const good = await page.locator('.feedback.ok').first().isVisible().catch(() => false)
      if (!good) {
        const msg = await page.locator('.feedback').first().innerText().catch(() => '(нет сообщения)')
        ok(false, `${scheme}: ${t.id} (${t.answerKind}) ответ «${t.answer}» не принят: ${msg.replace(/\s+/g, ' ')}`)
        await page.screenshot({ path: `${SCR}/shots/${scheme}-fail-${t.id}.png`, fullPage: true })
        break
      }
      if (k === 0 && gi < 3) await page.screenshot({ path: `${SCR}/shots/${scheme}-train-${g.id}.png`, fullPage: true })
      await page.locator('.task-nav .btn.primary', { hasText: 'Следующая' }).click()
    }
    await noOverflow(`группа ${g.id}`)
  }
  ok(errors.length === 0, `${scheme}: ошибки консоли: ${JSON.stringify(errors).slice(0, 400)}`)
  await ctx.close()
}

await run('light')
await run('dark')
console.log(`ИТОГ ${TOPIC}: fails=${fails}`)
await browser.close()
process.exit(fails ? 1 : 0)
