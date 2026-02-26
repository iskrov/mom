import type { LicensingPayload, TrackResult } from '../types'

interface TrackDetailProps {
  track: TrackResult | null
  licensing: LicensingPayload | null
  loadingLicensing: boolean
  onClose: () => void
}

function compact(n: number): string {
  return Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(n)
}


function badgeLabel(label: string): string {
  if (label === 'STRONG') return 'A'
  if (label === 'MODERATE') return 'B'
  if (label === 'MARGINAL') return 'C'
  return 'D'
}

function formatDate(value?: string): string {
  if (!value) return 'Unknown date'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Unknown date'
  return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
}

function formatReleaseDate(value?: string): string {
  if (!value) return 'Unknown'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function formatCareerStage(value?: string): string {
  if (!value) return 'Early'
  const key = value.trim().toLowerCase()
  const mapped: Record<string, string> = {
    undiscovered: 'Early',
    developing: 'Developing',
    'mid-level': 'Mid',
    mainstream: 'Mainstream',
    superstar: 'Superstar',
    legendary: 'Legend',
  }
  return mapped[key] || 'Early'
}

export function TrackDetail({ track, licensing, loadingLicensing, onClose }: TrackDetailProps) {
  if (!track) {
    return (
      <aside className="detail-panel empty">
        <div>Select a track via Opportunity to inspect details.</div>
      </aside>
    )
  }

  const opp = track.opportunity_score
  const midRevenue = track.revenue.projections?.mid?.revenue?.all_dsps_avg ?? 0
  const splitEntries = licensing?.entries || []
  const careerStage = formatCareerStage(track.remix_artist_enriched.career_stage)
  const trackMeta = track.original_track_enriched || { songwriters: [] }
  const songwriterCount = trackMeta.songwriters.length
  const songwriterFull = songwriterCount > 0 ? trackMeta.songwriters.join(', ') : 'Unknown'
  const songwriterPreview =
    songwriterCount > 2
      ? `${trackMeta.songwriters.slice(0, 2).join(', ')} +${songwriterCount - 2} others`
      : songwriterFull
  const scFollowers = track.sc_user.followers_count || 0
  const spFollowers = track.remix_artist_enriched.sp_followers || 0
  const ttFollowers = track.remix_artist_enriched.tiktok_followers || 0
  const totalAudience = scFollowers + spFollowers + ttFollowers
  const audienceTooltip = [
    spFollowers > 0 && `Spotify     ${compact(spFollowers)}`,
    ttFollowers > 0 && `TikTok      ${compact(ttFollowers)}`,
    scFollowers > 0 && `SoundCloud  ${compact(scFollowers)}`,
  ]
    .filter(Boolean)
    .join('\n') || 'No follower data'

  const velocityBars = Array.from({ length: 30 }, (_, idx) => {
    const base = Math.max(track.daily_velocity * 0.55, 1)
    const growth = idx / 29
    return Math.round(base * (0.7 + growth * 0.6))
  })
  const maxBar = Math.max(...velocityBars, 1)

  return (
    <aside className="detail-panel">
      <div className="detail-head">
        <div>
          <h3 className="detail-title">{track.title}</h3>
          <div className="detail-subtitle">
            {track.remix_artist || track.sc_user.username} · {formatDate(track.created_at)} ·{' '}
            {compact(track.plays)} streams
          </div>
        </div>
        <button className="detail-close-btn" type="button" onClick={onClose} aria-label="Close detail panel">
          ×
        </button>
      </div>

      <div className="detail-tabs">
        <button className="detail-tab active" type="button">
          ① Opportunity
        </button>
        <button className="detail-tab" type="button">
          ② Action
        </button>
      </div>

      <div className="score-box modern">
        <div>
          <div className="metric-label">OPPORTUNITY SCORE</div>
          <div className="big-score">{opp.overall.toFixed(1)}</div>
          <div className="cell-muted">out of 10 · {opp.label.toLowerCase()} priority</div>
        </div>
        <div className="grade-badge">{badgeLabel(opp.label)}</div>
      </div>

      <div className="detail-section">
        <div className="detail-section-title">VELOCITY & HEAT SCORE</div>
        <div className="chart-card">
          <div className="velocity-caption">STREAMS PER DAY - LAST 30 DAYS</div>
          <div className="velocity-wrap">
            {velocityBars.map((value, idx) => (
              <div
                key={`${idx}-${value}`}
                className={`velocity-bar ${idx > 20 ? 'active' : ''}`}
                style={{ height: `${Math.max((value / maxBar) * 44, 8)}px` }}
              />
            ))}
          </div>
          <div className="velocity-labels">
            <span>30d ago</span>
            <span>today</span>
          </div>
        </div>

        <div className="detail-grid">
          <div className="detail-stat">
            <span>Heat Score</span>
            <strong>{track.heat_score.toFixed(1)}</strong>
          </div>
          <div className="detail-stat">
            <span>Streams / Day</span>
            <strong>{Math.round(track.daily_velocity).toLocaleString()}</strong>
          </div>
          <div className="detail-stat">
            <span>Total Streams</span>
            <strong>{compact(track.plays)}</strong>
          </div>
          <div className="detail-stat">
            <span>Total Likes</span>
            <strong>{compact(track.likes)}</strong>
          </div>
        </div>
      </div>

      <div className="detail-section">
        <div className="detail-section-title">REMIX ARTIST IMPACT</div>
        <div className="impact-grid">
          <div className="impact-cell">
            <div
              className="impact-value impact-value-audience hover-tooltip hover-tooltip-pre"
              data-tooltip={audienceTooltip}
              tabIndex={0}
            >
              {compact(totalAudience)}
            </div>
            <div className="impact-label">Total Audience</div>
          </div>
<div className="impact-cell">
            <div className="impact-value impact-value-stage">{careerStage}</div>
            <div className="impact-label">Career Stage</div>
          </div>
          <div className="impact-cell">
            <div className="impact-value">{compact(track.remix_artist_enriched.sp_monthly_listeners || 0)}</div>
            <div className="impact-label">Monthly Listeners</div>
          </div>
        </div>
      </div>

      <div className="detail-section">
        <div className="detail-section-title">ORIGINAL ARTIST</div>
        <div className="detail-grid">
          <div className="detail-stat">
            <span>Artist</span>
            <strong>{track.original_artist_enriched.name || track.original_artist || 'Unknown'}</strong>
          </div>
          <div className="detail-stat">
            <span>Record Label</span>
            <strong>{track.original_artist_enriched.record_label || 'Unknown'}</strong>
          </div>
          <div className="detail-stat">
            <span>Career Stage</span>
            <strong>{formatCareerStage(track.original_artist_enriched.career_stage)}</strong>
          </div>
          <div className="detail-stat">
            <span>Monthly Listeners</span>
            <strong>{compact(track.original_artist_enriched.sp_monthly_listeners || 0)}</strong>
          </div>
          <div className="detail-stat">
            <span>Release Date</span>
            <strong>{formatReleaseDate(trackMeta.release_date)}</strong>
          </div>
          <div className="detail-stat">
            <span>ISRC</span>
            <strong>{trackMeta.isrc || 'Unknown'}</strong>
          </div>
          <div className="detail-stat">
            <span>Songwriters</span>
            <strong className="hover-tooltip" data-tooltip={songwriterFull} tabIndex={0}>
              {songwriterPreview}
            </strong>
          </div>
          <div className="detail-stat">
            <span>Match Confidence</span>
            <strong>
              {typeof trackMeta.match_confidence === 'number'
                ? `${Math.round(trackMeta.match_confidence * 100)}%`
                : 'N/A'}
            </strong>
          </div>
        </div>
      </div>

      <div className="detail-section">
        <div className="detail-section-title">LICENSING SPLITS</div>
        {loadingLicensing && <div className="cell-muted">Loading mock split data...</div>}
        {!loadingLicensing && splitEntries.length > 0 && (
          <div className="licensing-card">
            <div className="split-bar">
              {splitEntries.map((entry) => (
                <div
                  key={`${entry.party}-${entry.role}-bar`}
                  className="split-segment"
                  style={{ width: `${entry.share_pct}%` }}
                  title={`${entry.party}: ${entry.share_pct.toFixed(1)}%`}
                />
              ))}
            </div>
            <div className="split-legend">
              {splitEntries.map((entry) => (
                <div className="legend-item" key={`${entry.party}-${entry.role}-legend`}>
                  <span className="legend-dot" />
                  <span>
                    {entry.party} {entry.share_pct.toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
            <div className="split-table">
              <div className="split-head">
                <span>Party</span>
                <span>Role</span>
                <span>Share</span>
              </div>
              {splitEntries.map((entry) => (
                <div className="split-row row-grid" key={`${entry.party}-${entry.role}`}>
                  <span>{entry.party}</span>
                  <span>{entry.role}</span>
                  <strong>{entry.share_pct.toFixed(1)}%</strong>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="detail-section">
        <div className="detail-section-title">ROYALTY PROJECTION</div>
        <div className="royalty-card">
          <div className="split-row">
            <span>All DSPs Avg</span>
            <strong>${Math.round(midRevenue).toLocaleString()}</strong>
          </div>
          <div className="cell-muted">{track.viability.recommendation}</div>
        </div>
      </div>
    </aside>
  )
}
