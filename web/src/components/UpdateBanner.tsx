import { useEffect, useState } from 'react'
import { registerSW } from 'virtual:pwa-register'

const CHECK_EVERY_MS = 30 * 60 * 1000

/** Когда на сайте появилась новая версия, предлагаем обновиться (иначе открытая вкладка сидит на старой). */
export function UpdateBanner() {
  const [apply, setApply] = useState<(() => void) | null>(null)
  useEffect(() => {
    try {
      const updateSW = registerSW({
        immediate: true,
        onNeedRefresh() {
          setApply(() => () => void updateSW(true))
        },
        onRegisteredSW(_url, registration) {
          if (registration) window.setInterval(() => void registration.update().catch(() => {}), CHECK_EVERY_MS)
        },
      })
    } catch {
      /* без сервис-воркера приложение работает как обычный сайт */
    }
  }, [])
  if (!apply) return null
  return (
    <div className="update-banner" role="status">
      <span>Вышла новая версия приложения.</span>
      <button className="btn small primary" onClick={apply}>
        Обновить
      </button>
    </div>
  )
}
