import type { TrackResult } from '../types'

function escapeCsv(value: string | number | null | undefined): string {
  if (value === null || value === undefined) return ''
  const str = String(value)
  if (str.includes(',') || str.includes('"') || str.includes('\n')) {
    return `"${str.replace(/"/g, '""')}"`
  }
  return str
}

const HEADERS = [
  'Remix Title',
  'Remix Artist',
  'Original Song',
  'Original Artist',
  'Genre',
  'Streams',
  'Likes',
  'Reposts',
  'Daily Velocity',
  'Days Live',
  'Heat Score',
  'Heat Trend',
  'Opp Score',
  'Opp Label',
  'ISRC',
  'Record Label',
  'Release Date',
  'Songwriters',
  'Mid Revenue',
  'Remix Artist SC Followers',
  'Remix Artist Spotify Monthly Listeners',
  'Remix Artist Career Stage',
  'Remix Artist Momentum',
  'Original Artist Spotify Monthly Listeners',
  'SoundCloud URL',
]

function rowToCsv(track: TrackResult): string {
  const midRevenue = track.viability?.mid_revenue ?? track.revenue?.projections?.mid?.revenue?.['total'] ?? ''

  const fields = [
    track.title,
    track.remix_artist,
    track.original_song,
    track.original_artist,
    track.genre,
    track.plays,
    track.likes,
    track.reposts,
    Math.round(track.daily_velocity),
    track.days_live,
    track.heat_score,
    track.heat_trend,
    track.opportunity_score?.overall,
    track.opportunity_score?.label,
    track.original_track_enriched?.isrc,
    track.original_artist_enriched?.record_label,
    track.original_track_enriched?.release_date,
    (track.original_track_enriched?.songwriters ?? []).join('; '),
    midRevenue,
    track.remix_artist_enriched?.sp_followers,
    track.remix_artist_enriched?.sp_monthly_listeners,
    track.remix_artist_enriched?.career_stage,
    track.remix_artist_enriched?.momentum,
    track.original_artist_enriched?.sp_monthly_listeners,
    track.permalink_url,
  ]

  return fields.map(escapeCsv).join(',')
}

export function downloadResultsAsCsv(rows: TrackResult[], filename = 'remix-radar-results.csv'): void {
  const lines = [HEADERS.join(','), ...rows.map(rowToCsv)]
  const csv = lines.join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
