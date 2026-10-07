import { Home } from './components/Home'
import { TopicPage } from './components/TopicPage'
import { useRoute } from './route'
import { ProgressProvider } from './store/useProgress'

export default function App() {
  const route = useRoute()
  return (
    <ProgressProvider>{route.name === 'home' ? <Home /> : <TopicPage key={route.id} route={route} />}</ProgressProvider>
  )
}
