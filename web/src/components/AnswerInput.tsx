import { useLayoutEffect, useRef } from 'react'
import type { AnswerKind } from '../content/types'
import { Rich } from './Tex'
import { parseNumberSet } from '../lib/check'
import { toTex, tryParse } from '../lib/expr'
import { Tex } from './Tex'

type Key = { label: string; insert: string; caret?: number; title?: string; wide?: boolean }

function keysFor(kind: AnswerKind, vars: string[], sqrtKey: boolean): Key[] {
  const root: Key[] = sqrtKey ? [{ label: '√', insert: '√()', caret: 2, title: 'квадратный корень' }] : []
  if (kind === 'roots') {
    return [
      { label: '−', insert: '-', title: 'минус' },
      { label: '/', insert: '/', title: 'дробная черта' },
      ...root,
      { label: ';', insert: '; ', title: 'разделитель значений' },
      { label: 'нет', insert: 'нет', title: 'таких значений нет', wide: true },
    ]
  }
  return [
    ...vars.map((v) => ({ label: v, insert: v })),
    ...root,
    { label: 'дробь', insert: '()/()', caret: 1, title: 'числитель / знаменатель', wide: true },
    { label: '( )', insert: '()', caret: 1 },
    { label: 'xⁿ', insert: '^', title: 'степень' },
    { label: '+', insert: '+' },
    { label: '−', insert: '-' },
    { label: '·', insert: '*', title: 'умножить' },
  ]
}

export function varsOf(...sources: (string | undefined)[]): string[] {
  const set = new Set<string>()
  for (const s of sources) {
    if (!s) continue
    const p = tryParse(s)
    p?.vars.forEach((v) => set.add(v))
  }
  return [...set].sort().slice(0, 5)
}

type Props = {
  value: string
  onChange: (v: string) => void
  onSubmit: () => void
  kind: AnswerKind
  vars: string[]
  disabled?: boolean
  submitLabel?: string
  /** Кнопка √ на клавиатуре. */
  sqrtKey?: boolean
  /** Варианты ответа (kind = choice), текст с формулами. */
  options?: string[]
  /** Плитки для расстановки по порядку (kind = order), записи для компьютера. */
  items?: string[]
  /** Подсказка в пустом поле. */
  placeholder?: string
}

function CompareInput({ value, onChange, onSubmit, disabled, submitLabel }: Pick<Props, 'value' | 'onChange' | 'onSubmit' | 'disabled' | 'submitLabel'>) {
  return (
    <div className="answer-input">
      <div className="compare-row" role="group" aria-label="Знак сравнения">
        {['<', '=', '>'].map((sgn) => (
          <button key={sgn} type="button" className={`sign ${value === sgn ? 'on' : ''}`} disabled={disabled} onClick={() => onChange(sgn)} aria-pressed={value === sgn}>
            {sgn}
          </button>
        ))}
      </div>
      <button className="btn primary" disabled={disabled || !value} onClick={onSubmit}>
        {submitLabel}
      </button>
    </div>
  )
}

function ChoiceInput({ value, onChange, onSubmit, disabled, submitLabel, options = [] }: Pick<Props, 'value' | 'onChange' | 'onSubmit' | 'disabled' | 'submitLabel' | 'options'>) {
  return (
    <div className="answer-input">
      <div className="options">
        {options.map((o, i) => (
          <button key={i} type="button" className={`option ${value === String(i) ? 'picked' : ''}`} disabled={disabled} onClick={() => onChange(String(i))} aria-pressed={value === String(i)}>
            <Rich text={o} />
          </button>
        ))}
      </div>
      <button className="btn primary" disabled={disabled || value === ''} onClick={onSubmit}>
        {submitLabel}
      </button>
    </div>
  )
}

function OrderInput({ value, onChange, onSubmit, disabled, submitLabel, items = [] }: Pick<Props, 'value' | 'onChange' | 'onSubmit' | 'disabled' | 'submitLabel' | 'items'>) {
  const chosen = value ? value.split(',').map(Number) : []
  const left = items.map((_, i) => i).filter((i) => !chosen.includes(i))
  const tex = (i: number) => toTex(items[i]) ?? items[i]
  return (
    <div className="answer-input">
      <p className="muted">Нажимай числа от меньшего к большему:</p>
      <div className="order-row" aria-label="Ещё не выбраны">
        {left.map((i) => (
          <button key={i} type="button" className="tile" disabled={disabled} onClick={() => onChange([...chosen, i].join(','))}>
            <Tex tex={tex(i)} />
          </button>
        ))}
      </div>
      <div className="order-chosen" aria-live="polite">
        {chosen.length === 0 ? <span className="muted">Здесь появится твой порядок</span> : null}
        {chosen.map((i, k) => (
          <span key={i} className="order-item">
            {k > 0 && <span className="lt">&lt;</span>}
            <span className="tile static c1">
              <Tex tex={tex(i)} />
            </span>
          </span>
        ))}
      </div>
      <div className="input-row">
        <button className="btn ghost" disabled={disabled || chosen.length === 0} onClick={() => onChange('')}>
          Сбросить
        </button>
        <button className="btn primary" disabled={disabled || chosen.length < items.length} onClick={onSubmit}>
          {submitLabel}
        </button>
      </div>
    </div>
  )
}

export function AnswerInput(props: Props) {
  if (props.kind === 'compare') return <CompareInput {...props} submitLabel={props.submitLabel ?? 'Проверить'} />
  if (props.kind === 'choice') return <ChoiceInput {...props} submitLabel={props.submitLabel ?? 'Проверить'} />
  if (props.kind === 'order') return <OrderInput {...props} submitLabel={props.submitLabel ?? 'Проверить'} />
  return <TextInput {...props} />
}

function TextInput({ value, onChange, onSubmit, kind, vars, disabled, submitLabel = 'Проверить', sqrtKey = false, placeholder }: Props) {
  const ref = useRef<HTMLInputElement>(null)
  const caret = useRef<number | null>(null)

  useLayoutEffect(() => {
    if (caret.current !== null && ref.current) {
      ref.current.focus()
      ref.current.setSelectionRange(caret.current, caret.current)
      caret.current = null
    }
  })

  const insert = (k: Key) => {
    const el = ref.current
    const start = el?.selectionStart ?? value.length
    const end = el?.selectionEnd ?? value.length
    const next = value.slice(0, start) + k.insert + value.slice(end)
    caret.current = start + (k.caret ?? k.insert.length)
    onChange(next)
  }

  const backspace = () => {
    const el = ref.current
    const start = el?.selectionStart ?? value.length
    const end = el?.selectionEnd ?? value.length
    if (start === end && start > 0) {
      caret.current = start - 1
      onChange(value.slice(0, start - 1) + value.slice(end))
    } else if (start !== end) {
      caret.current = start
      onChange(value.slice(0, start) + value.slice(end))
    }
  }

  let preview: React.ReactNode = null
  if (value.trim()) {
    if (kind === 'expr') {
      const tex = toTex(value)
      preview = tex ? <Tex tex={tex} display /> : <span className="muted">Пока не могу разобрать запись…</span>
    } else {
      const set = parseNumberSet(value)
      preview =
        set === null ? (
          <span className="muted">Пока не могу разобрать запись…</span>
        ) : set.length === 0 ? (
          <span>таких значений нет</span>
        ) : (
          <Tex tex={value.split(';').map((part) => toTex(part.replace(/^\s*[xх]\s*=\s*/i, '')) ?? part).join(';\\ ')} />
        )
    }
  }

  return (
    <div className="answer-input">
      <div className="input-row">
        <input
          ref={ref}
          type="text"
          inputMode="text"
          autoCapitalize="off"
          autoCorrect="off"
          autoComplete="off"
          spellCheck={false}
          disabled={disabled}
          value={value}
          maxLength={120}
          placeholder={placeholder ?? (kind === 'roots' ? 'например: 3; -3' : 'например: (x+1)/(x-2)')}
          aria-label="Ответ"
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') onSubmit()
          }}
        />
        <button className="btn primary" disabled={disabled || !value.trim()} onClick={onSubmit}>
          {submitLabel}
        </button>
      </div>
      <div className="keypad" aria-label="Клавиши для ввода">
        {keysFor(kind, vars, sqrtKey).map((k) => (
          <button key={k.label} type="button" className={`key ${k.wide ? 'wide' : ''}`} title={k.title} disabled={disabled} onClick={() => insert(k)}>
            {k.label}
          </button>
        ))}
        <button type="button" className="key" title="стереть" aria-label="Стереть" disabled={disabled} onClick={backspace}>
          ⌫
        </button>
      </div>
      <div className="preview" aria-live="polite">
        {preview ? (
          <>
            <span className="preview-label">Я понял так:</span>
            {preview}
          </>
        ) : (
          <span className="muted">
            {kind === 'expr'
              ? 'Дробь пиши через «/», числитель и знаменатель — в скобках: (x+1)/(x-2).'
              : 'Несколько значений пиши через «;». Если значений нет — напиши «нет».'}
          </span>
        )}
      </div>
    </div>
  )
}
