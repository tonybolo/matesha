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

/** Текст с $формулами$ и **жирным**. */
export function Rich({ text }: { text: string }) {
  const segs = useMemo(() => parseRich(text), [text])
  return (
    <>
      {segs.map((s, i) => {
        if (s.kind === 'text') return <span key={i}>{s.text}</span>
        if (s.kind === 'bold') return <strong key={i}>{s.text}</strong>
        return <Tex key={i} tex={s.tex} display={s.display} />
      })}
    </>
  )
}
