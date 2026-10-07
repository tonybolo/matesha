import { getTopic } from '../content/load'
import { hrefTopic, type Route } from '../route'
import { topicStats } from '../store/progress'
import { useProgress } from '../store/useProgress'
import { Check } from './Check'
import { Lesson } from './Lesson'
import { Trainer } from './Trainer'

export function TopicPage({ route }: { route: Extract<Route, { name: 'topic' }> }) {
  const topic = getTopic(route.id)
  const { state } = useProgress()
  if (!topic) {
    return (
      <main className="page">
        <p>Такой темы нет.</p>
        <a className="link" href="#/">← На главную</a>
      </main>
    )
  }
  const progress = state.topics[topic.id]
  const stats = topicStats(topic, progress)
  const tabs = [
    { tab: 'learn' as const, label: 'Объяснение', done: progress?.explainDone },
    { tab: 'check' as const, label: 'Проверка', done: progress?.checkPassed },
    { tab: 'train' as const, label: 'Тренировка', done: stats.total > 0 && stats.solved === stats.total },
  ]
  return (
    <main className="page">
      <a className="back" href="#/">← Все темы</a>
      <header className="topic-head">
        <p className="eyebrow">Тема {topic.order}</p>
        <h1>{topic.title}</h1>
        <div className="progress-bar" aria-label={`Освоено ${stats.percent}%`}>
          <div style={{ width: `${stats.percent}%` }} />
        </div>
        <p className="muted">Освоено {stats.percent}% · задач решено {stats.solved} из {stats.total}</p>
      </header>
      <nav className="tabs" aria-label="Этапы темы">
        {tabs.map((t, i) => (
          <a key={t.tab} href={hrefTopic(topic.id, t.tab)} className={`tab ${route.tab === t.tab ? 'on' : ''} ${t.done ? 'done' : ''}`} aria-current={route.tab === t.tab ? 'page' : undefined}>
            <span className="tab-num">{t.done ? '✓' : i + 1}</span>
            {t.label}
          </a>
        ))}
      </nav>
      {route.tab === 'learn' && <Lesson topic={topic} step={route.step} />}
      {route.tab === 'check' && <Check topic={topic} />}
      {route.tab === 'train' && <Trainer topic={topic} />}
    </main>
  )
}
