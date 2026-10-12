import katex from 'katex'
import { useMemo } from 'react'
import { parseRich } from '../lib/rich'

export function Tex({ tex, display = false }: { tex: string; display?: boolean }) {
  const html = useMemo(
    () =>
      katex.renderToString(display ? tex : tex.replace(/\\frac(?![a-z])/g, '\\dfrac'), {
        displayMode: display,
        throwOnError: false,
        strict: 'ignore',
      }),
    [tex, display],
  )
  return <span className={display ? 'tex-display' : 'tex'} dangerouslySetInnerHTML={{ __html: html }} />
}

const PUNCT = /^[.,;:!?…)»]+/

/** Текст с $формулами$ и **жирным**. Знаки препинания сразу после формулы не отрываются от неё при переносе строки. */
export function Rich({ text }: { text: string }) {
  const segs = useMemo(() => {
    const out: { seg: ReturnType<typeof parseRich>[number]; glue?: string }[] = []
    const parsed = parseRich(text)
    for (let i = 0; i < parsed.length; i++) {
      const cur = parsed[i]
      const next = parsed[i + 1]
      if (cur.kind === 'math' && !cur.display && next?.kind === 'text') {
        const m = next.text.match(PUNCT)
        if (m) {
          out.push({ seg: cur, glue: m[0] })
          parsed[i + 1] = { kind: 'text', text: next.text.slice(m[0].length) }
          continue
        }
      }
      out.push({ seg: cur })
    }
    return out
  }, [text])
  return (
    <>
      {segs.map(({ seg: s, glue }, i) => {
        if (s.kind === 'text') return s.text ? <span key={i}>{s.text}</span> : null
        if (s.kind === 'bold') return <strong key={i}>{s.text}</strong>
        const tex = <Tex tex={s.tex} display={s.display} />
        return glue ? (
          <span key={i} className="glue">
            {tex}
            {glue}
          </span>
        ) : (
          <span key={i}>{tex}</span>
        )
      })}
    </>
  )
}
