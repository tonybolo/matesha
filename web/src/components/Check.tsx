import { useState } from 'react'
import { renderPrompt } from '../content/prompt'
import type { Question, Topic } from '../content/types'
import { checkAnswer } from '../lib/check'
import { go, hrefTopic } from '../route'
import { recordCheck } from '../store/progress'
import { useProgress } from '../store/useProgress'
import { AnswerInput, varsOf } from './AnswerInput'
import { Rich } from './Tex'

function QuestionView({
  topic,
  q,
  onDone,
}: {
  topic: Topic
  q: Question
  onDone: (correct: boolean) => void
}) {
  const [picked, setPicked] = useState<number | null>(null)
  const [value, setValue] = useState('')
  const [soft, setSoft] = useState<string | null>(null)
  const [result, setResult] = useState<{ correct: boolean } | null>(null)

  const submitInput = () => {
    if (q.kind !== 'input' || result) return
    const res = checkAnswer(value, q.answer, q.answerKind, { reduce: q.reduce })
    if (res.status === 'correct') setResult({ correct: true })
    else if (res.status === 'wrong') setResult({ correct: false })
    else setSoft(res.message)
  }

  return (
    <div className="question">
      <p className="q-prompt">
        <Rich text={renderPrompt(q.prompt, q.kind === 'input' ? q.expr : undefined)} />
      </p>
      {q.kind === 'choice' ? (
        <div className="options">
          {q.options.map((o, i) => {
            const state = picked === null ? '' : i === q.correct ? 'right' : i === picked ? 'wrong' : 'dim'
            return (
              <button
                key={i}
                className={`option ${state}`}
                disabled={picked !== null}
                onClick={() => {
                  setPicked(i)
                  setResult({ correct: i === q.correct })
                }}
              >
                <Rich text={o} />
              </button>
            )
          })}
        </div>
      ) : (
        <>
          <AnswerInput
            value={value}
            onChange={(v) => {
              setValue(v)
              setSoft(null)
            }}
            onSubmit={submitInput}
            kind={q.answerKind}
            vars={varsOf(q.answer)}
            disabled={result !== null}
          />
          {soft && <p className="soft-msg">{soft}</p>}
        </>
      )}
      {result && (
        <div className={`feedback ${result.correct ? 'ok' : 'bad'}`}>
          <strong>{result.correct ? 'Верно! 🎉' : 'Не совсем.'}</strong>
          <p className="explain">
            <Rich text={q.explain} />
          </p>
          {!result.correct && (
            <a className="link" href={hrefTopic(topic.id, 'learn', q.step)}>
              ↩ Перечитать шаг {q.step + 1}: {topic.steps[q.step].title}
            </a>
          )}
          <div className="nav-row end">
            <button className="btn primary" onClick={() => onDone(result.correct)}>
              Дальше ▸
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export function Check({ topic }: { topic: Topic }) {
  const { state, update } = useProgress()
  const [idx, setIdx] = useState(0)
  const [score, setScore] = useState(0)
  const [run, setRun] = useState(0)
  const total = topic.check.length
  const done = idx >= total
  const progress = state.topics[topic.id]

  const next = (correct: boolean) => {
    const newScore = score + (correct ? 1 : 0)
    setScore(newScore)
    if (idx + 1 >= total) update((s) => recordCheck(s, topic.id, newScore, topic.passScore))
    setIdx(idx + 1)
  }

  if (done) {
    const passed = score >= topic.passScore
    return (
      <section className="check-result">
        <h2>{passed ? 'Отлично, тема понята! 🎉' : 'Почти получилось'}</h2>
        <p className="big-score">
          {score} из {total}
        </p>
        <p>
          {passed
            ? 'Теперь закрепим на задачах. Начинай с уровня 1 и поднимайся выше.'
            : `Нужно набрать минимум ${topic.passScore}. Перечитай шаги объяснения и попробуй ещё раз: ошибки — это нормально, так и учатся.`}
        </p>
        <div className="nav-row">
          <button
            className="btn ghost"
            onClick={() => {
              setIdx(0)
              setScore(0)
              setRun(run + 1)
            }}
          >
            Пройти заново
          </button>
          {passed ? (
            <button className="btn primary" onClick={() => go(hrefTopic(topic.id, 'train'))}>
              К тренировке ▸
            </button>
          ) : (
            <button className="btn primary" onClick={() => go(hrefTopic(topic.id, 'learn'))}>
              Перечитать объяснение
            </button>
          )}
        </div>
      </section>
    )
  }

  return (
    <section className="check">
      <h2 className="step-title">
        <span className="step-num">
          Вопрос {idx + 1} из {total}
        </span>
        Проверим, что понятно
      </h2>
      {progress?.checkPassed && <p className="muted">Проверка уже пройдена (лучший результат {progress.checkBest} из {total}), можно повторить.</p>}
      <QuestionView key={`${run}-${topic.check[idx].id}`} topic={topic} q={topic.check[idx]} onDone={next} />
    </section>
  )
}
