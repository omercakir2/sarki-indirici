import { Check, Download, ListMusic, LoaderCircle, SearchX, TriangleAlert } from 'lucide-react'
import { formatDuration, type Track } from './api'
import type { View } from './App'

type Props = {
  view: View
  added: Set<string>
  quality: string
  onDownload: (tracks: Track[]) => void
}

export function Results({ view, added, quality, onDownload }: Props) {
  if (view.kind === 'idle') return null

  if (view.kind === 'loading') {
    return (
      <section aria-live="polite" className="mt-6 flex items-center gap-3 px-1 text-ink-2">
        <LoaderCircle size={22} className="animate-spin" aria-hidden />
        <span className="pt-0.5 font-semibold">
          {view.mode === 'link' ? 'Şarkı bilgileri getiriliyor…' : 'YouTube’da aranıyor…'}
        </span>
      </section>
    )
  }

  if (view.kind === 'error') {
    return (
      <section
        role="alert"
        className="mt-6 flex items-start gap-3 rounded-xl bg-signal/15 px-5 py-4 text-signal-ink"
      >
        <TriangleAlert size={22} className="mt-0.5 shrink-0" aria-hidden />
        <p className="pt-0.5 font-semibold">{view.message}</p>
      </section>
    )
  }

  if (view.kind === 'lookup' && view.data.kind === 'video') {
    const t = view.data.tracks[0]
    const isAdded = added.has(t.url)
    return (
      <section aria-label="Bulunan şarkı" className="mt-6">
        <div className="flex flex-col gap-4 rounded-2xl bg-asphalt-2 p-4 sm:flex-row sm:items-center sm:gap-6 sm:p-5">
          <Cover src={t.thumbnail} size="lg" />
          <div className="min-w-0 flex-1">
            <h2 className="text-xl font-extrabold leading-tight text-balance">{t.title}</h2>
            <Meta
              className="mt-1.5 text-ink-2"
              items={[t.artist, formatDuration(t.duration), `MP3, ${quality} kbps`]}
            />
          </div>
          <DownloadButton big isAdded={isAdded} onClick={() => onDownload([t])} />
        </div>
      </section>
    )
  }

  const tracks = view.kind === 'lookup' ? view.data.tracks : view.results
  const remaining = tracks.filter((t) => !added.has(t.url))

  if (!tracks.length) {
    return (
      <section className="mt-6 flex items-center gap-3 px-1 text-ink-2">
        <SearchX size={22} aria-hidden />
        <p className="pt-0.5 font-semibold">
          Sonuç bulunamadı. Şarkı adını ve sanatçıyı birlikte yazmayı dene.
        </p>
      </section>
    )
  }

  return (
    <section aria-label="Sonuçlar" className="mt-6">
      <div className="mb-3 flex flex-wrap items-end justify-between gap-3 px-1">
        {view.kind === 'lookup' ? (
          <div className="flex items-center gap-3">
            <ListMusic size={24} className="text-ink-2" aria-hidden />
            <div>
              <h2 className="text-lg font-extrabold leading-tight">{view.data.title}</h2>
              <p className="text-sm text-ink-2">
                Oynatma listesi, {tracks.length} şarkı
              </p>
            </div>
          </div>
        ) : (
          <h2 className="text-lg font-extrabold">
            “{view.query}” için sonuçlar
          </h2>
        )}
        {view.kind === 'lookup' && (
          <button
            type="button"
            disabled={!remaining.length}
            onClick={() => onDownload(remaining)}
            className="flex h-12 items-center gap-2 rounded-xl bg-sign-yellow px-5 pt-0.5 font-black text-asphalt transition-colors hover:bg-sign-yellow-2 disabled:bg-asphalt-3 disabled:text-ink-3"
          >
            {remaining.length ? (
              <>
                <Download size={20} aria-hidden /> Hepsini indir ({remaining.length})
              </>
            ) : (
              <>
                <Check size={20} aria-hidden /> Hepsi eklendi
              </>
            )}
          </button>
        )}
      </div>
      <ul className="max-h-[440px] divide-y divide-line overflow-y-auto rounded-2xl bg-asphalt-2">
        {tracks.map((t) => (
          <li key={t.url} className="flex items-center gap-4 px-4 py-3">
            <Cover src={t.thumbnail} size="sm" />
            <div className="min-w-0 flex-1">
              <p className="truncate font-bold">{t.title}</p>
              <Meta className="truncate text-sm text-ink-2" items={[t.artist, formatDuration(t.duration)]} />
            </div>
            <DownloadButton isAdded={added.has(t.url)} onClick={() => onDownload([t])} />
          </li>
        ))}
      </ul>
    </section>
  )
}

function DownloadButton({
  isAdded,
  onClick,
  big,
}: {
  isAdded: boolean
  onClick: () => void
  big?: boolean
}) {
  if (isAdded) {
    return (
      <span
        className={`flex shrink-0 items-center justify-center gap-2 rounded-xl font-extrabold text-ink-2 ${
          big ? 'h-14 px-6' : 'h-11 px-3 text-sm'
        }`}
      >
        <Check size={big ? 22 : 18} aria-hidden /> Sıraya eklendi
      </span>
    )
  }
  return (
    <button
      type="button"
      onClick={onClick}
      className={
        big
          ? 'flex h-14 shrink-0 items-center justify-center gap-2 rounded-xl bg-sign-yellow px-8 pt-0.5 text-lg font-black text-asphalt transition-colors hover:bg-sign-yellow-2'
          : 'flex h-11 shrink-0 items-center gap-2 rounded-xl border-2 border-ink-3 px-4 pt-0.5 text-sm font-extrabold text-ink transition-colors hover:border-sign-yellow hover:text-sign-yellow'
      }
    >
      <Download size={big ? 22 : 18} aria-hidden /> İndir
    </button>
  )
}

export function Cover({ src, size }: { src: string | null; size: 'lg' | 'sm' | 'xs' }) {
  const cls = {
    lg: 'size-28 rounded-xl',
    sm: 'size-14 rounded-lg',
    xs: 'size-12 rounded-md',
  }[size]
  return src ? (
    <img
      src={src}
      alt=""
      loading="lazy"
      referrerPolicy="no-referrer"
      className={`${cls} shrink-0 bg-asphalt-3 object-cover`}
    />
  ) : (
    <div className={`${cls} shrink-0 bg-asphalt-3`} />
  )
}

export function Meta({ items, className }: { items: (string | null | undefined)[]; className?: string }) {
  const parts = items.filter(Boolean) as string[]
  return (
    <p className={className}>
      {parts.map((p, i) => (
        <span key={i}>
          {i > 0 && (
            <span aria-hidden className="mx-2 opacity-60">
              ·
            </span>
          )}
          {p}
        </span>
      ))}
    </p>
  )
}
