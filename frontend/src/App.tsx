import { FolderOpen, Link2, LoaderCircle, Search, TriangleAlert } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { api, ApiError, isLikelyUrl, type Lookup, type Status, type Track } from './api'
import { Queue } from './Queue'
import { Results } from './Results'
import { useJobs } from './useJobs'

const QUALITIES = [
  { value: '320', label: '320 kbps', hint: 'En iyi ses' },
  { value: '192', label: '192 kbps', hint: 'Dengeli' },
  { value: '128', label: '128 kbps', hint: 'Küçük dosya' },
]

export type View =
  | { kind: 'idle' }
  | { kind: 'loading'; mode: 'link' | 'search' }
  | { kind: 'lookup'; data: Lookup }
  | { kind: 'search'; query: string; results: Track[] }
  | { kind: 'error'; message: string }

export default function App() {
  const [input, setInput] = useState('')
  const [quality, setQuality] = useState(() => localStorageGet('quality') ?? '320')
  const [view, setView] = useState<View>({ kind: 'idle' })
  const [status, setStatus] = useState<Status | null>(null)
  const [added, setAdded] = useState<Set<string>>(new Set())
  const { jobs, connected } = useJobs()
  const inputRef = useRef<HTMLInputElement>(null)
  const requestId = useRef(0)

  // Poll status until the download engine is ready (first launch downloads it).
  useEffect(() => {
    let timer: number
    const tick = async () => {
      try {
        const s = await api.status()
        setStatus(s)
        if (!s.ready || s.updating) timer = window.setTimeout(tick, 1500)
      } catch {
        timer = window.setTimeout(tick, 3000)
      }
    }
    tick()
    return () => window.clearTimeout(timer)
  }, [])

  useEffect(() => {
    localStorageSet('quality', quality)
  }, [quality])

  const isUrl = isLikelyUrl(input)

  async function find(text = input) {
    const value = text.trim()
    if (!value) {
      inputRef.current?.focus()
      return
    }
    const id = ++requestId.current
    const link = isLikelyUrl(value)
    setView({ kind: 'loading', mode: link ? 'link' : 'search' })
    try {
      if (link) {
        const data = await api.lookup(value)
        if (id === requestId.current) setView({ kind: 'lookup', data })
      } else {
        const { results } = await api.search(value)
        if (id === requestId.current) setView({ kind: 'search', query: value, results })
      }
    } catch (e) {
      if (id === requestId.current)
        setView({
          kind: 'error',
          message: e instanceof ApiError ? e.message : 'Bir şeyler ters gitti. Tekrar dene.',
        })
    }
  }

  async function download(tracks: Track[]) {
    const fresh = tracks.filter((t) => !added.has(t.url))
    if (!fresh.length) return
    setAdded((prev) => new Set([...prev, ...fresh.map((t) => t.url)]))
    try {
      await api.addJobs(fresh, quality)
    } catch (e) {
      setAdded((prev) => {
        const next = new Set(prev)
        fresh.forEach((t) => next.delete(t.url))
        return next
      })
      setView({
        kind: 'error',
        message: e instanceof ApiError ? e.message : 'İndirme başlatılamadı.',
      })
    }
  }

  const engineBusy = status && (!status.ready || status.updating)

  return (
    <div className="mx-auto flex min-h-dvh max-w-[1080px] flex-col px-4 pb-10 pt-6 sm:px-8 sm:pt-10">
      <header className="sign sign-motorway px-5 pb-6 pt-5 sm:px-8 sm:pb-8 sm:pt-7">
        <div className="flex flex-wrap items-center justify-between gap-x-6 gap-y-3">
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
            <h1 className="text-2xl font-black leading-none tracking-[-0.01em] sm:text-3xl">
              MP3 Şarkı İndirici
            </h1>
            <span className="rounded-lg bg-white px-2.5 pb-1 pt-1.5 text-sm font-extrabold leading-none text-motorway">
              Bedava ve Reklamsız
            </span>
          </div>
          {status?.can_open_folder && (
            <button
              type="button"
              onClick={() => api.openFolder()}
              className="-ml-2 flex items-center gap-2 rounded-lg px-2 py-1 text-sm font-semibold text-white/90 sm:ml-0 transition-colors hover:bg-white/10 hover:text-white"
            >
              <FolderOpen size={18} strokeWidth={2} aria-hidden />
              İndirilenler klasörü
            </button>
          )}
        </div>

        <form
          className="mt-6 grid gap-3 sm:grid-cols-[1fr_auto_auto]"
          onSubmit={(e) => {
            e.preventDefault()
            find()
          }}
        >
          <label className="relative block">
            <span className="sr-only">YouTube linki veya şarkı adı</span>
            <span className="pointer-events-none absolute left-5 top-1/2 -translate-y-1/2 text-motorway">
              {isUrl ? <Link2 size={24} aria-hidden /> : <Search size={24} aria-hidden />}
            </span>
            <input
              ref={inputRef}
              autoFocus
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onPaste={(e) => {
                const text = e.clipboardData.getData('text')
                if (isLikelyUrl(text) && !input.trim()) {
                  e.preventDefault()
                  setInput(text.trim())
                  find(text)
                }
              }}
              placeholder="Link yapıştır ya da şarkı ara"
              className="h-16 w-full rounded-xl bg-white pl-14 pr-4 pt-1 text-lg font-semibold text-asphalt placeholder:text-[#5d6b63] focus-visible:outline-sign-yellow"
            />
          </label>
          <label className="relative">
            <span className="sr-only">Ses kalitesi</span>
            <select
              value={quality}
              onChange={(e) => setQuality(e.target.value)}
              className="h-16 w-full appearance-none rounded-xl border-[3px] border-white bg-motorway pl-5 pr-11 pt-1 text-lg font-extrabold text-white sm:w-auto"
            >
              {QUALITIES.map((q) => (
                <option key={q.value} value={q.value}>
                  {q.label} – {q.hint}
                </option>
              ))}
            </select>
            <svg
              aria-hidden
              viewBox="0 0 24 24"
              className="pointer-events-none absolute right-4 top-1/2 size-5 -translate-y-1/2 fill-none stroke-white stroke-[2.5]"
            >
              <path d="m6 9 6 6 6-6" />
            </svg>
          </label>
          <button
            type="submit"
            disabled={view.kind === 'loading'}
            className="flex h-16 items-center justify-center gap-2 rounded-xl bg-sign-yellow px-8 pt-1 text-lg font-black text-asphalt transition-[background-color,transform] duration-200 ease-out-expo hover:bg-sign-yellow-2 active:translate-y-px disabled:opacity-70"
          >
            {view.kind === 'loading' ? (
              <LoaderCircle size={22} className="animate-spin" aria-hidden />
            ) : null}
            {isUrl ? 'Getir' : 'Ara'}
          </button>
        </form>
        <p className="mt-3 text-sm text-white/85">
          Linki yapıştırınca şarkı kendiliğinden gelir. Tek bir video ya da bütün bir oynatma
          listesi olabilir.
        </p>
      </header>

      {engineBusy && (
        <Notice tone="info">
          {status?.updating
            ? 'İndirme motoru güncelleniyor. Birkaç saniye sürer.'
            : 'İndirme motoru hazırlanıyor. İlk açılışta biraz sürebilir.'}
        </Notice>
      )}
      {status?.error && <Notice tone="error">{status.error}</Notice>}
      {!connected && (
        <Notice tone="error">Uygulamayla bağlantı koptu. Yeniden bağlanılıyor…</Notice>
      )}

      <Results view={view} added={added} onDownload={download} quality={quality} />

      <Queue jobs={jobs} canOpenFolder={!!status?.can_open_folder} />

      <footer className="mt-auto flex flex-wrap justify-between gap-x-6 gap-y-1 pt-10 text-xs text-ink-3">
        <span className="break-all">Dosyalar: {status?.download_dir ?? '…'}</span>
        {status?.ytdlp_version && (
          <EngineVersion version={status.ytdlp_version} onUpdated={setStatus} />
        )}
      </footer>
    </div>
  )
}

function Notice({ tone, children }: { tone: 'info' | 'error'; children: React.ReactNode }) {
  return (
    <div
      role={tone === 'error' ? 'alert' : 'status'}
      className={`mt-5 flex items-center gap-3 rounded-xl px-5 py-3.5 text-sm font-semibold ${
        tone === 'error' ? 'bg-signal/15 text-signal-ink' : 'bg-asphalt-2 text-ink-2'
      }`}
    >
      {tone === 'error' ? (
        <TriangleAlert size={20} aria-hidden className="shrink-0" />
      ) : (
        <LoaderCircle size={20} aria-hidden className="shrink-0 animate-spin" />
      )}
      {children}
    </div>
  )
}

function EngineVersion({
  version,
  onUpdated,
}: {
  version: string
  onUpdated: (s: Status) => void
}) {
  const [msg, setMsg] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  return (
    <span className="flex items-center gap-2">
      Motor: {version}
      <button
        type="button"
        disabled={busy}
        onClick={async () => {
          setBusy(true)
          try {
            const r = await api.update()
            setMsg(r.message)
            onUpdated(await api.status())
          } catch (e) {
            setMsg(e instanceof Error ? e.message : 'Güncellenemedi.')
          } finally {
            setBusy(false)
          }
        }}
        className="font-semibold text-ink-2 underline decoration-line underline-offset-4 hover:text-ink disabled:opacity-60"
      >
        {busy ? 'Kontrol ediliyor…' : 'Güncelle'}
      </button>
      {msg && <span className="text-ink-2">{msg}</span>}
    </span>
  )
}

function localStorageGet(key: string) {
  try {
    return window.localStorage.getItem(key)
  } catch {
    return null
  }
}
function localStorageSet(key: string, value: string) {
  try {
    window.localStorage.setItem(key, value)
  } catch {
    /* private mode */
  }
}
