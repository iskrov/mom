import type { TrackResult } from '../types'

interface ResultsTableProps {
  rows: TrackResult[]
  selectedTrackId: number | null
  onToggleTrackSelect: (track: TrackResult) => void
  onOpenCasePage: (track: TrackResult) => void
}

function compact(n: number): string {
  return Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(n)
}

function trendSymbol(trend: TrackResult['heat_trend']) {
  if (trend === 'rising') return '↑'
  if (trend === 'declining') return '↓'
  return '—'
}

function clean(text?: string): string {
  return (text || '').replace(/\s+/g, ' ').trim()
}

export function ResultsTable({ rows, selectedTrackId, onToggleTrackSelect, onOpenCasePage }: ResultsTableProps) {
  let remixRank = 0
  return (
    <div className="results-table-wrap">
      <table className="results-table">
        <thead>
          <tr>
            <th></th>
            <th>#</th>
            <th>REMIX TITLE</th>
            <th>REMIX ARTIST</th>
            <th>ORIGINAL ARTIST</th>
            <th>GENRE</th>
            <th>STREAMS</th>
            <th>LIKES</th>
            <th>STREAMS/DAY</th>
            <th>HEAT SCORE</th>
            <th>OPP. SCORE</th>
            <th>ACTIONS</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const oppClass =
              row.opportunity_score.overall >= 8
                ? 'opp-strong'
                : row.opportunity_score.overall >= 5
                  ? 'opp-mid'
                  : 'opp-low'
            const isSelected = selectedTrackId === row.track_id
            const isReference = Boolean(row.is_reference_original)
            if (!isReference) remixRank += 1
            return (
              <tr
                key={row.track_id}
                className={`${isSelected ? 'row-selected' : ''} ${isReference ? 'row-reference' : ''}`.trim()}
              >
                <td>
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => onToggleTrackSelect(row)}
                    aria-label={`Select track ${row.title}`}
                  />
                </td>
                <td>{isReference ? '★' : remixRank}</td>
                <td>
                  <div className="title-cell">
                    {row.permalink_url ? (
                      <a
                        className="title-main track-link"
                        href={row.permalink_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {clean(row.title) || 'Untitled'}
                      </a>
                    ) : (
                      <div className="title-main">{clean(row.title) || 'Untitled'}</div>
                    )}
                    <div className="cell-muted title-sub">
                      {isReference ? (
                        <span className="reference-badge">ORIGINAL REFERENCE</span>
                      ) : (
                        <>orig: {clean(row.original_song) || 'Unknown'} - {clean(row.original_artist) || 'Unknown'}</>
                      )}
                    </div>
                  </div>
                </td>
                <td>{row.remix_artist || row.sc_user.username || 'N/A'}</td>
                <td>{row.original_artist || 'N/A'}</td>
                <td>{row.genre || 'Unknown'}</td>
                <td>{compact(row.plays)}</td>
                <td>{compact(row.likes)}</td>
                <td>{Math.round(row.daily_velocity).toLocaleString()}</td>
                <td className={`heat-${row.heat_trend}`}>
                  {trendSymbol(row.heat_trend)} {row.heat_score.toFixed(1)}
                </td>
                <td>
                  <span className={`opp-chip ${oppClass}`}>{row.opportunity_score.overall.toFixed(1)}</span>
                </td>
                <td>
                  <div className="action-row">
                    <button className="btn-opportunity" onClick={() => onToggleTrackSelect(row)} type="button">
                      Opportunity →
                    </button>
                    <button className="btn-action" type="button">
                      Action →
                    </button>
                    <button className="btn-case-page" onClick={() => onOpenCasePage(row)} type="button">
                      Case Page →
                    </button>
                  </div>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
