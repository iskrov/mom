import type { TrackResult } from '../types'

interface SummaryBarProps {
  tracks: TrackResult[]
  totalFound: number
}

function compact(n: number): string {
  return Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(n)
}

export function SummaryBar({ tracks, totalFound }: SummaryBarProps) {
  const totalStreams = tracks.reduce((sum, row) => sum + row.plays, 0)
  const totalLikes = tracks.reduce((sum, row) => sum + row.likes, 0)
  const avgHeat = tracks.length ? tracks.reduce((sum, row) => sum + row.heat_score, 0) / tracks.length : 0
  const avgOpp = tracks.length
    ? tracks.reduce((sum, row) => sum + row.opportunity_score.overall, 0) / tracks.length
    : 0

  return (
    <div className="summary-grid">
      <div className="metric-card">
        <div className="metric-label">TRACKS (FILTERED)</div>
        <div className="metric-value">{tracks.length}</div>
        <div className="metric-meta">of {totalFound} found</div>
      </div>
      <div className="metric-card">
        <div className="metric-label">TOTAL STREAMS</div>
        <div className="metric-value">{compact(totalStreams)}</div>
        <div className="metric-meta">across results</div>
      </div>
      <div className="metric-card">
        <div className="metric-label">TOTAL LIKES</div>
        <div className="metric-value">{compact(totalLikes)}</div>
        <div className="metric-meta">across results</div>
      </div>
      <div className="metric-card">
        <div className="metric-label">AVG HEAT SCORE</div>
        <div className="metric-value">{avgHeat.toFixed(1)}</div>
        <div className="metric-meta">out of 10</div>
      </div>
      <div className="metric-card">
        <div className="metric-label">AVG OPPORTUNITY SCORE</div>
        <div className="metric-value">{avgOpp.toFixed(1)}</div>
        <div className="metric-meta">out of 10</div>
      </div>
    </div>
  )
}
