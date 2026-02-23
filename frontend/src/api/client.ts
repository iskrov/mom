import type { LicensingPayload, SearchFilters, TrackResult, UiMetadata } from '../types'

const API_BASE = '/api'

type EventHandlers = {
  onStatus?: (message: { message: string; count?: number }) => void
  onTrack?: (track: TrackResult) => void
  onComplete?: (results: TrackResult[]) => void
}

function parseBlock(block: string): { event: string; data: unknown } | null {
  const lines = block.split('\n')
  let event = 'message'
  let data = ''
  for (const line of lines) {
    if (line.startsWith('event:')) {
      event = line.slice(6).trim()
    }
    if (line.startsWith('data:')) {
      data += line.slice(5).trim()
    }
  }
  if (!data) return null
  return { event, data: JSON.parse(data) }
}

export async function streamArtistSearch(
  filters: SearchFilters,
  handlers: EventHandlers,
  signal: AbortSignal,
): Promise<void> {
  const response = await fetch(`${API_BASE}/search/artist`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      artist_name: filters.artistName,
      tracks_to_fetch: filters.tracksToFetch,
      sort_by: filters.sortBy === 'opportunity_score' ? 'heat_score' : filters.sortBy,
      sort_desc: true,
      genre_filter: filters.genre === 'All' ? [] : [filters.genre],
      region: filters.region,
      career_stages: filters.careerStages,
      min_account_reach: filters.minAccountReach,
      max_account_reach: filters.maxAccountReach,
      min_heat_score: filters.heatMin,
      max_heat_score: filters.heatMax,
      enrich_chartmetric: filters.enrichChartmetric,
      check_official_release: filters.checkOfficialRelease,
    }),
    signal,
  })

  if (!response.ok || !response.body) {
    throw new Error(`Search request failed: ${response.status}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    const blocks = buffer.split('\n\n')
    buffer = blocks.pop() ?? ''

    for (const block of blocks) {
      const parsed = parseBlock(block)
      if (!parsed) continue

      if (parsed.event === 'status' && handlers.onStatus) {
        handlers.onStatus(parsed.data as { message: string; count?: number })
      }
      if (parsed.event === 'track' && handlers.onTrack) {
        handlers.onTrack((parsed.data as { track: TrackResult }).track)
      }
      if (parsed.event === 'complete' && handlers.onComplete) {
        handlers.onComplete((parsed.data as { results: TrackResult[] }).results)
      }
    }
  }
}

export async function streamSongSearch(
  filters: SearchFilters,
  handlers: EventHandlers,
  signal: AbortSignal,
): Promise<void> {
  const response = await fetch(`${API_BASE}/search/song`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      song_name: filters.songName,
      artist_name: filters.songArtistName || undefined,
      tracks_to_fetch: filters.tracksToFetch,
      enrich_chartmetric: filters.enrichChartmetric,
      check_official_release: filters.checkOfficialRelease,
    }),
    signal,
  })

  if (!response.ok || !response.body) {
    throw new Error(`Song search request failed: ${response.status}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    const blocks = buffer.split('\n\n')
    buffer = blocks.pop() ?? ''

    for (const block of blocks) {
      const parsed = parseBlock(block)
      if (!parsed) continue

      if (parsed.event === 'status' && handlers.onStatus) {
        handlers.onStatus(parsed.data as { message: string; count?: number })
      }
      if (parsed.event === 'track' && handlers.onTrack) {
        handlers.onTrack((parsed.data as { track: TrackResult }).track)
      }
      if (parsed.event === 'complete' && handlers.onComplete) {
        handlers.onComplete((parsed.data as { results: TrackResult[] }).results)
      }
    }
  }
}

export async function analyzeScUrl(scUrl: string): Promise<TrackResult> {
  const response = await fetch(`${API_BASE}/analyze/url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sc_url: scUrl }),
  })
  if (!response.ok) {
    throw new Error(`SC Link analysis failed: ${response.status}`)
  }
  return response.json() as Promise<TrackResult>
}

export async function runCatalogSearch(
  file: File,
  limitRemixes: number,
  signal: AbortSignal,
): Promise<TrackResult[]> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('limit_remixes', String(limitRemixes))

  const response = await fetch(`${API_BASE}/search/catalog`, {
    method: 'POST',
    body: formData,
    signal,
  })
  if (!response.ok) {
    throw new Error(`Catalog search failed: ${response.status}`)
  }
  const payload = (await response.json()) as { results: TrackResult[] }
  return payload.results || []
}

export async function fetchLicensing(trackId: number): Promise<LicensingPayload> {
  const response = await fetch(`${API_BASE}/tracks/${trackId}/licensing`)
  if (!response.ok) {
    throw new Error('Failed to fetch licensing mock data.')
  }
  return response.json() as Promise<LicensingPayload>
}

export async function fetchUiMetadata(): Promise<UiMetadata> {
  const response = await fetch(`${API_BASE}/meta/ui`)
  if (!response.ok) {
    throw new Error('Failed to fetch UI metadata.')
  }
  return response.json() as Promise<UiMetadata>
}
