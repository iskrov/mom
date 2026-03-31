import type { WatchListEntry } from '../types'

interface WatchListProps {
  entries: WatchListEntry[]
  onRemove: (id: string) => void
  onClose: () => void
}

function compact(n: number): string {
  return Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(n)
}

export function WatchList({ entries, onRemove, onClose }: WatchListProps) {
  return (
    <div className="watchlist-panel">
      <div className="watchlist-header">
        <h3 className="watchlist-title">Watch List ({entries.length})</h3>
        <button className="watchlist-close" type="button" onClick={onClose}>
          ×
        </button>
      </div>

      {entries.length === 0 && (
        <p className="watchlist-empty">
          No cases saved yet. Click "Add to Watch List" on a Song Case Page.
        </p>
      )}

      <div className="watchlist-cards">
        {entries.map((entry) => (
          <div key={entry.id} className="watchlist-card">
            <div className="watchlist-card-header">
              <div>
                <div className="watchlist-card-title">{entry.songTitle}</div>
                <div className="watchlist-card-artist">{entry.artist}</div>
              </div>
              <button
                className="watchlist-remove"
                type="button"
                onClick={() => onRemove(entry.id)}
                aria-label="Remove from watch list"
              >
                ×
              </button>
            </div>
            <div className="watchlist-card-remix">
              {entry.topRemixArtist} &nbsp;·&nbsp; {compact(entry.topRemixPlays)} SC streams
            </div>
            <p className="watchlist-card-insight">{entry.insight}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
