export type Track = {
  id: string | null
  url: string
  title: string
  artist: string | null
  duration: number | null
  thumbnail: string | null
}

export type Lookup = {
  kind: 'video' | 'playlist'
  title: string
  uploader?: string | null
  tracks: Track[]
}

export type JobStatus = 'queued' | 'downloading' | 'converting' | 'done' | 'error' | 'canceled'

export type Job = {
  id: string
  url: string
  title: string
  artist: string | null
  thumbnail: string | null
  duration: number | null
  quality: string
  status: JobStatus
  percent: number
  speed: number | null
  eta: number | null
  error: string | null
  filename: string | null
  created: number
}

export type Status = {
  app: string
  download_dir: string
  can_open_folder: boolean
  desktop: boolean
  ytdlp_version: string | null
  ytdlp_ok: boolean
  ffmpeg_ok: boolean
  deno_ok: boolean
  updating: boolean
  update_message: string | null
  error: string | null
  ready: boolean
}

export class ApiError extends Error {}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(path, {
      ...init,
      headers: { 'content-type': 'application/json', ...init?.headers },
    })
  } catch {
    throw new ApiError('Uygulamaya ulaşılamıyor. Pencereyi kapatıp yeniden aç.')
  }
  if (!res.ok) {
    let detail = 'Bir şeyler ters gitti. Tekrar dene.'
    try {
      const body = await res.json()
      if (typeof body.detail === 'string') detail = body.detail
    } catch {
      /* keep default */
    }
    throw new ApiError(detail)
  }
  return res.json() as Promise<T>
}

export const api = {
  status: () => request<Status>('/api/status'),
  lookup: (url: string) =>
    request<Lookup>('/api/lookup', { method: 'POST', body: JSON.stringify({ url }) }),
  search: (q: string) =>
    request<{ results: Track[] }>(`/api/search?q=${encodeURIComponent(q)}`),
  addJobs: (tracks: Track[], quality: string) =>
    request<{ jobs: Job[] }>('/api/jobs', {
      method: 'POST',
      body: JSON.stringify({ tracks, quality }),
    }),
  cancel: (id: string) => request(`/api/jobs/${id}/cancel`, { method: 'POST' }),
  retry: (id: string) => request(`/api/jobs/${id}/retry`, { method: 'POST' }),
  remove: (id: string) => request(`/api/jobs/${id}`, { method: 'DELETE' }),
  clear: () => request<{ removed: number }>('/api/jobs/clear', { method: 'POST' }),
  openFolder: (jobId?: string) =>
    request(`/api/open-folder${jobId ? `?job_id=${jobId}` : ''}`, { method: 'POST' }),
  update: () => request<{ updated: boolean; message: string }>('/api/update', { method: 'POST' }),
  fileUrl: (id: string) => `/api/jobs/${id}/file`,
}

export function isLikelyUrl(text: string) {
  const t = text.trim()
  return /^(https?:\/\/)?(www\.|m\.|music\.)?(youtube\.com|youtu\.be)\//i.test(t)
}

export function formatDuration(sec: number | null | undefined) {
  if (!sec || sec <= 0) return ''
  const s = Math.round(sec)
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const r = String(s % 60).padStart(2, '0')
  return h ? `${h}:${String(m).padStart(2, '0')}:${r}` : `${m}:${r}`
}

export function formatSpeed(bps: number | null) {
  if (!bps) return ''
  const mb = bps / 1024 / 1024
  return mb >= 1
    ? `${mb.toLocaleString('tr-TR', { maximumFractionDigits: 1 })} MB/sn`
    : `${Math.round(bps / 1024)} KB/sn`
}
