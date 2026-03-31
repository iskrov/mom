import type { SongCaseData, TrackResult, WatchListEntry } from '../types'

// Define compact once here.
function compact(n: number): string {
  return Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(n)
}

interface TrackRowProps {
  label: string
  badge: 'OFFICIAL' | 'UNOFFICIAL' | null
  scPlays: number | null
  spPlays: number | null
  maxPlays: number
  highlight: boolean
  enriched: TrackResult['remix_artist_enriched'] | null
}

function BarRow({
  platform,
  plays,
  maxPlays,
  color,
}: {
  platform: string
  plays: number | null
  maxPlays: number
  color: string
}) {
  const pct = plays !== null ? Math.max((plays / maxPlays) * 100, 0.3) : 0
  return (
    <div className="scp-bar-row">
      <div className="scp-bar-platform">{platform}</div>
      <div className="scp-bar-track">
        {plays !== null ? (
          <div
            className="scp-bar-fill"
            style={{ width: `${pct}%`, background: color }}
          >
            {plays > 0 && <span className="scp-bar-label">{compact(plays)}</span>}
          </div>
        ) : (
          <div className="scp-bar-empty">
            <span className="scp-bar-none">Not on DSPs</span>
          </div>
        )}
      </div>
    </div>
  )
}

function TrackRow({ label, badge, scPlays, spPlays, maxPlays, highlight, enriched }: TrackRowProps) {
  return (
    <div className={`scp-track-row ${highlight ? 'scp-track-highlight' : ''}`}>
      <div className="scp-track-bars">
        <div className="scp-track-label">
          {label}
          {badge && (
            <span className={`scp-badge scp-badge-${badge.toLowerCase()}`}>{badge}</span>
          )}
        </div>
        <div className="scp-bars">
          <BarRow platform="SC" plays={scPlays} maxPlays={maxPlays} color="#ff8800" />
          <BarRow platform="SP" plays={spPlays} maxPlays={maxPlays} color="#1DB954" />
        </div>
      </div>
      {enriched && badge === 'UNOFFICIAL' && (
        <div className="scp-artist-profile">
          <span className="scp-artist-label">ARTIST:</span>
          {enriched.sp_monthly_listeners != null && (
            <div className="scp-artist-stat">
              <strong style={{ color: '#1DB954' }}>{compact(enriched.sp_monthly_listeners)}</strong>
              <span>Spotify</span>
            </div>
          )}
          {enriched.sp_followers != null && (
            <div className="scp-artist-stat">
              <strong style={{ color: '#ff8800' }}>{compact(enriched.sp_followers)}</strong>
              <span>SC</span>
            </div>
          )}
          {enriched.tiktok_followers != null && enriched.tiktok_followers > 0 && (
            <div className="scp-artist-stat">
              <strong style={{ color: '#69C9D0' }}>{compact(enriched.tiktok_followers)}</strong>
              <span>TikTok</span>
            </div>
          )}
          {enriched.career_stage && (
            <div className="scp-artist-stat">
              <strong>{enriched.career_stage}</strong>
              <span>Stage</span>
            </div>
          )}
          {enriched.momentum && (
            <div className="scp-artist-stat">
              <strong style={{ color: '#6b2fff' }}>{enriched.momentum}</strong>
              <span>Momentum</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function buildInsight(data: SongCaseData): string {
  const { unofficialRemixes } = data
  if (unofficialRemixes.length === 0) return 'No unofficial remixes found for this track.'
  const top = unofficialRemixes[0]
  const artistName = top.remix_artist || top.sc_user.username || 'An artist'
  const streams = compact(top.plays)
  return `${artistName}'s unofficial remix has ${streams} SoundCloud streams and has never been released on any DSP.`
}

interface SongCasePageProps {
  data: SongCaseData
  onAddToWatchList: (entry: WatchListEntry) => void
  onClose: () => void
}

export function SongCasePage({ data, onAddToWatchList, onClose }: SongCasePageProps) {
  const { original, unofficialRemixes } = data
  const maxPlays = Math.max(original.plays, ...unofficialRemixes.map((r) => r.plays), 1)
  const insight = buildInsight(data)
  const topRemix = unofficialRemixes[0] ?? null

  const songTitle = original.original_song || original.title
  const artistName =
    original.original_artist_enriched?.name || original.original_artist || 'Unknown'
  const label = original.original_artist_enriched?.record_label || ''
  const isrc = original.original_track_enriched?.isrc || ''
  const releaseDate = original.original_track_enriched?.release_date
    ? new Date(original.original_track_enriched.release_date).getFullYear()
    : null

  function handleAddToWatchList() {
    if (!topRemix) return
    onAddToWatchList({
      id: String(original.track_id),
      songTitle,
      artist: artistName,
      topRemixArtist: topRemix.remix_artist || topRemix.sc_user.username || 'Unknown',
      topRemixPlays: topRemix.plays,
      insight,
    })
  }

  return (
    <div className="song-case-page">
      {/* Header */}
      <div className="scp-header">
        <div className="scp-title-block">
          <h2 className="scp-title">{songTitle}</h2>
          <div className="scp-meta">
            {artistName}
            {label && <> &nbsp;·&nbsp; {label}</>}
            {releaseDate && <> &nbsp;·&nbsp; {releaseDate}</>}
            {isrc && <> &nbsp;·&nbsp; <span className="scp-isrc">{isrc}</span></>}
          </div>
        </div>
        <div className="scp-header-actions">
          <button className="scp-close-btn" type="button" onClick={onClose}>
            ← Back
          </button>
        </div>
      </div>

      {/* Legend */}
      <div className="scp-legend">
        <span className="scp-legend-item">
          <span className="scp-dot scp-dot-sc" />
          SoundCloud
        </span>
        <span className="scp-legend-item">
          <span className="scp-dot scp-dot-sp" />
          Spotify
        </span>
        <span className="scp-legend-item scp-legend-muted">
          <span className="scp-dot scp-dot-none" />
          Not on DSPs
        </span>
      </div>

      {/* Chart */}
      <div className="scp-chart">
        <div className="scp-section-label">ORIGINAL SONG</div>
        <TrackRow
          label={songTitle}
          badge={null}
          scPlays={original.plays}
          spPlays={null}
          maxPlays={maxPlays}
          highlight={false}
          enriched={null}
        />

        {unofficialRemixes.length > 0 && (
          <>
            <div className="scp-section-label scp-section-divider">
              UNOFFICIAL REMIXES ON SOUNDCLOUD ({unofficialRemixes.length})
            </div>
            {unofficialRemixes.map((remix) => (
              <TrackRow
                key={remix.track_id}
                label={remix.remix_artist || remix.sc_user.username || 'Unknown'}
                badge="UNOFFICIAL"
                scPlays={remix.plays}
                spPlays={null}
                maxPlays={maxPlays}
                highlight={remix.plays > maxPlays * 0.10}
                enriched={remix.remix_artist_enriched}
              />
            ))}
          </>
        )}
      </div>

      {/* Insight callout */}
      {topRemix && (
        <div className="scp-insight">
          <div className="scp-insight-label">AUTO-GENERATED INSIGHT</div>
          <p className="scp-insight-text">{insight}</p>
          <div className="scp-insight-actions">
            <button className="btn-primary" type="button">
              Recommend Release
            </button>
            <button className="btn-ghost" type="button" onClick={handleAddToWatchList}>
              Add to Watch List
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
