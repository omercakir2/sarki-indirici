import { Download, FolderOpen, RotateCcw, Trash2, X } from 'lucide-react'
import { api, formatDuration, formatSpeed, type Job } from './api'
import { Cover } from './Results'

const ACTIVE = new Set(['downloading', 'converting'])

export function Queue({ jobs, canOpenFolder }: { jobs: Job[]; canOpenFolder: boolean }) {
  const ordered = [...jobs].sort((a, b) => b.created - a.created)
  const running = jobs.filter((j) => ACTIVE.has(j.status) || j.status === 'queued').length
  const done = jobs.filter((j) => j.status === 'done').length
  const finished = jobs.length - running

  return (
    <section aria-labelledby="queue-title" className="mt-10">
      <div className="mb-3 flex flex-wrap items-end justify-between gap-3 px-1">
        <div>
          <h2 id="queue-title" className="text-xl font-black">
            İndirmeler
          </h2>
          {jobs.length > 0 && (
            <p className="text-sm text-ink-2 tabular">
              {done} hazır{running ? `, ${running} yolda` : ''}
            </p>
          )}
        </div>
        <div className="flex gap-2">
          {finished > 0 && (
            <button
              type="button"
              onClick={() => api.clear()}
              className="flex h-11 items-center gap-2 rounded-xl px-3 pt-0.5 text-sm font-bold text-ink-2 transition-colors hover:bg-asphalt-2 hover:text-ink"
            >
              <Trash2 size={18} aria-hidden /> Listeyi temizle
            </button>
          )}
        </div>
      </div>

      {jobs.length === 0 ? (
        <EmptyQueue />
      ) : (
        <ol className="flex flex-col gap-2" aria-live="polite">
          {ordered.map((job) => (
            <JobRow key={job.id} job={job} canOpenFolder={canOpenFolder} />
          ))}
        </ol>
      )}
    </section>
  )
}

function EmptyQueue() {
  const steps = [
    'YouTube’da şarkıyı aç, adres çubuğundaki linki kopyala.',
    'Yukarıdaki kutuya yapıştır.',
    'İndir’e bas. Şarkı İndirilenler klasörüne gelir.',
  ]
  return (
    <div className="rounded-2xl border-2 border-dashed border-line px-5 py-6 sm:px-7">
      <p className="font-bold text-ink-2">Henüz indirme yok. Nasıl yapılır:</p>
      <ol className="mt-3 grid gap-3 sm:grid-cols-3 sm:gap-6">
        {steps.map((s, i) => (
          <li key={s} className="flex gap-3 text-sm text-ink-2">
            <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-asphalt-3 pt-0.5 font-black text-ink tabular">
              {i + 1}
            </span>
            <span className="pt-1">{s}</span>
          </li>
        ))}
      </ol>
    </div>
  )
}

function JobRow({ job, canOpenFolder }: { job: Job; canOpenFolder: boolean }) {
  const active = ACTIVE.has(job.status)
  return (
    <li
      className={`grid grid-cols-[24px_auto_1fr_auto] items-center gap-x-3 px-3 py-3 transition-[background-color,box-shadow,border-color] duration-500 ease-out-expo sm:grid-cols-[28px_auto_1fr_auto] sm:gap-x-4 sm:px-5 ${
        active
          ? 'sign sign-intercity'
          : 'rounded-2xl border-4 border-transparent bg-asphalt-2'
      }`}
    >
      <StatusMark status={job.status} />
      <div className={job.status === 'done' || active ? '' : 'opacity-70'}>
        <Cover src={job.thumbnail} size="xs" />
      </div>
      <div className="min-w-0">
        <p className={`truncate text-base font-extrabold ${active ? 'text-white' : ''}`}>
          {job.title}
        </p>
        <p
          className={`text-sm ${job.status === 'error' ? 'line-clamp-2' : 'truncate'} ${active ? 'text-white/85' : statusTone(job)}`}
        >
          {statusLine(job)}
        </p>
        {active && (
          <div
            className="mt-2 h-2 overflow-hidden rounded-full bg-white/20"
            role="progressbar"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={Math.round(job.percent)}
            aria-label={`${job.title} indiriliyor`}
          >
            <div
              className={`h-full rounded-full bg-sign-yellow transition-[width] duration-300 ease-out-expo ${
                job.status === 'converting' ? 'animate-pulse' : ''
              }`}
              style={{ width: `${Math.max(job.percent, 3)}%` }}
            />
          </div>
        )}
      </div>
      <div className="flex items-center justify-end gap-1 sm:gap-3">
        <Readout job={job} />
        <Actions job={job} canOpenFolder={canOpenFolder} />
      </div>
    </li>
  )
}

/** One mark in a fixed cell: hollow waits, filled is done, red failed. */
function StatusMark({ status }: { status: Job['status'] }) {
  const base = 'size-6 rounded-full'
  if (status === 'done')
    return <span aria-hidden className={`${base} bg-white ring-4 ring-white/15`} />
  if (status === 'error')
    return (
      <span aria-hidden className={`${base} flex items-center justify-center bg-signal`}>
        <X size={14} strokeWidth={3.5} className="text-white" />
      </span>
    )
  if (status === 'canceled')
    return <span aria-hidden className={`${base} border-[3px] border-dashed border-ink-3`} />
  if (status === 'queued')
    return <span aria-hidden className={`${base} border-[3px] border-ink-3`} />
  return (
    <span aria-hidden className={`${base} border-[3px] border-white`}>
      <span className="m-[3px] block size-3 animate-pulse rounded-full bg-sign-yellow" />
    </span>
  )
}

function Readout({ job }: { job: Job }) {
  if (job.status === 'downloading' && job.percent > 0) {
    return (
      <span className="hidden text-right leading-none tabular sm:block">
        <span className="block text-2xl font-black text-white">%{Math.floor(job.percent)}</span>
        {job.eta != null && job.eta > 0 && (
          <span className="mt-1 block text-xs font-semibold text-white/80">
            {formatDuration(job.eta)} kaldı
          </span>
        )}
      </span>
    )
  }
  return null
}

function Actions({ job, canOpenFolder }: { job: Job; canOpenFolder: boolean }) {
  const ghost =
    'flex h-10 items-center gap-1.5 rounded-lg px-3 pt-0.5 text-sm font-extrabold transition-colors'
  if (job.status === 'queued' || ACTIVE.has(job.status)) {
    return (
      <button
        type="button"
        onClick={() => api.cancel(job.id)}
        className={`${ghost} ${ACTIVE.has(job.status) ? 'text-white hover:bg-white/15' : 'text-ink-2 hover:bg-asphalt-3 hover:text-ink'}`}
      >
        <X size={18} aria-hidden /> <span className="sr-only sm:not-sr-only">İptal</span>
      </button>
    )
  }
  return (
    <>
      {job.status === 'done' &&
        (canOpenFolder ? (
          <button
            type="button"
            onClick={() => api.openFolder(job.id)}
            className={`${ghost} text-ink hover:bg-asphalt-3`}
          >
            <FolderOpen size={18} aria-hidden /> <span className="sr-only sm:not-sr-only">Göster</span>
          </button>
        ) : (
          <a href={api.fileUrl(job.id)} download className={`${ghost} text-ink hover:bg-asphalt-3`}>
            <Download size={18} aria-hidden /> Bilgisayara kaydet
          </a>
        ))}
      {(job.status === 'error' || job.status === 'canceled') && (
        <button
          type="button"
          onClick={() => api.retry(job.id)}
          className={`${ghost} text-sign-yellow hover:bg-asphalt-3`}
        >
          <RotateCcw size={18} aria-hidden /> <span className="sr-only sm:not-sr-only">Tekrar dene</span>
        </button>
      )}
      <button
        type="button"
        onClick={() => api.remove(job.id)}
        aria-label={`${job.title} listeden kaldır`}
        title="Listeden kaldır"
        className="flex size-10 items-center justify-center rounded-lg text-ink-3 transition-colors hover:bg-asphalt-3 hover:text-ink"
      >
        <X size={18} aria-hidden />
      </button>
    </>
  )
}

function statusLine(job: Job) {
  switch (job.status) {
    case 'queued':
      return 'Sırada bekliyor'
    case 'downloading':
      return job.percent > 0
        ? [`İniyor %${Math.floor(job.percent)}`, formatSpeed(job.speed)].filter(Boolean).join(', ')
        : 'Hazırlanıyor…'
    case 'converting':
      return 'MP3’e çevriliyor, kapak ekleniyor…'
    case 'done':
      return job.filename ?? 'Hazır'
    case 'canceled':
      return 'İptal edildi'
    case 'error':
      return job.error ?? 'İndirilemedi'
  }
}

function statusTone(job: Job) {
  if (job.status === 'error') return 'text-signal-ink'
  if (job.status === 'done') return 'text-ink-2'
  return 'text-ink-3'
}
