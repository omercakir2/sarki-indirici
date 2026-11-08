import { useEffect, useState } from 'react'
import type { Job } from './api'

type Event =
  | { type: 'snapshot'; jobs: Job[] }
  | { type: 'job'; job: Job }
  | { type: 'removed'; id: string }

/** Live job list from the server's SSE stream; reconnects on its own. */
export function useJobs() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [connected, setConnected] = useState(true)

  useEffect(() => {
    const es = new EventSource('/api/events')
    es.onopen = () => setConnected(true)
    es.onerror = () => setConnected(false)
    es.onmessage = (e) => {
      const msg = JSON.parse(e.data) as Event
      setJobs((prev) => {
        if (msg.type === 'snapshot') return msg.jobs
        if (msg.type === 'removed') return prev.filter((j) => j.id !== msg.id)
        const i = prev.findIndex((j) => j.id === msg.job.id)
        if (i === -1) return [...prev, msg.job]
        const next = prev.slice()
        next[i] = msg.job
        return next
      })
    }
    return () => es.close()
  }, [])

  return { jobs, connected }
}
