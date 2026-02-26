import { useMemo, useRef, useState } from 'react'

import { analyzeScUrl, streamArtistSearch, streamCatalogSearch, streamSongSearch } from '../api/client'
import type { SearchFilters, SearchMode, TrackResult } from '../types'

const DEFAULT_FILTERS: SearchFilters = {
  artistName: 'Ed Sheeran',
  songName: 'Shape of You',
  songArtistName: 'Ed Sheeran',
  isrcOverride: '',
  scLink: '',
  catalogLimitRemixes: 5,
  catalogMinPlays: 0,
  tracksToFetch: 10,
  sortBy: 'heat_score',
  genre: 'All',
  region: 'Global',
  careerStages: [],
  minAccountReach: 0,
  maxAccountReach: 500_000,
  heatMin: 0,
  heatMax: 10,
  enrichChartmetric: true,
  checkOfficialRelease: false,
}

export function useSearch() {
  const [filters, setFilters] = useState<SearchFilters>(DEFAULT_FILTERS)
  const [results, setResults] = useState<TrackResult[]>([])
  const [status, setStatus] = useState('Idle')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  const runSearch = async (mode: SearchMode, options?: { catalogFile?: File | null }) => {
    abortRef.current?.abort()
    const abortController = new AbortController()
    abortRef.current = abortController
    setResults([])
    setError(null)
    setIsLoading(true)
    setStatus('Searching SoundCloud...')

    try {
      if (mode === 'artist_search') {
        await streamArtistSearch(
          filters,
          {
            onStatus: (payload) => {
              if (payload.message === 'tracks_found') {
                setStatus(`Found ${payload.count ?? 0} tracks. Enriching...`)
              }
            },
            onTrack: (track) => {
              setResults((prev) => [...prev, track])
              setStatus('Streaming enriched tracks...')
            },
            onComplete: (all) => {
              setResults(all)
              setStatus(`Complete: ${all.length} tracks`)
            },
          },
          abortController.signal,
        )
      } else if (mode === 'song_search') {
        await streamSongSearch(
          filters,
          {
            onStatus: (payload) => {
              if (payload.message === 'tracks_found') {
                setStatus(`Found ${payload.count ?? 0} song remixes. Enriching...`)
              }
            },
            onTrack: (track) => {
              setResults((prev) => [...prev, track])
              setStatus('Streaming song results...')
            },
            onComplete: (all) => {
              setResults(all)
              setStatus(`Complete: ${all.length} tracks`)
            },
          },
          abortController.signal,
        )
      } else if (mode === 'sc_link_lookup') {
        setStatus('Analyzing SoundCloud link...')
        const report = await analyzeScUrl(filters.scLink)
        setResults([report])
        setStatus('Complete: 1 track')
      } else if (mode === 'catalog_search') {
        if (!options?.catalogFile) {
          setError('Please select a .csv or .xml catalog file first.')
          setStatus('Catalog file required.')
          return
        }
        setStatus('Reading catalog...')
        await streamCatalogSearch(
          options.catalogFile,
          filters.catalogLimitRemixes,
          filters.catalogMinPlays,
          {
            onStatus: (payload) => {
              const p = payload as { message: string; count?: number; song?: string; index?: number; total?: number }
              if (p.message === 'catalog_loaded') {
                setStatus(`${p.count ?? 0} songs loaded. Starting search...`)
              } else if (p.message === 'processing_song') {
                setStatus(`Song ${p.index ?? '?'} / ${p.total ?? '?'}: ${p.song ?? ''} — finding remixes...`)
              }
            },
            onTrack: (track) => {
              setResults((prev) => [...prev, track])
            },
            onComplete: (all) => {
              setResults(all)
              setStatus(`Complete: ${all.length} remixes found`)
            },
          },
          abortController.signal,
        )
      } else {
        setStatus('This workflow is coming soon.')
        setResults([])
      }
    } catch (err) {
      if (!abortController.signal.aborted) {
        setError(err instanceof Error ? err.message : 'Search failed.')
      }
    } finally {
      if (!abortController.signal.aborted) {
        setIsLoading(false)
      }
    }
  }

  const filteredResults = useMemo(() => {
    let filtered = [...results]

    if (filters.genre !== 'All') {
      filtered = filtered.filter((row) => (row.genre || 'Unknown') === filters.genre)
    }
    if (filters.careerStages.length > 0) {
      const allowed = new Set(filters.careerStages.map((stage) => stage.toLowerCase()))
      filtered = filtered.filter((row) =>
        allowed.has((row.remix_artist_enriched.career_stage || '').toLowerCase()),
      )
    }
    filtered = filtered.filter(
      (row) =>
        row.sc_user.followers_count >= filters.minAccountReach &&
        row.sc_user.followers_count <= filters.maxAccountReach,
    )
    filtered = filtered.filter(
      (row) => row.heat_score >= filters.heatMin && row.heat_score <= filters.heatMax,
    )

    filtered.sort((a, b) => {
      if (filters.sortBy === 'opportunity_score') {
        return b.opportunity_score.overall - a.opportunity_score.overall
      }
      return (b[filters.sortBy] as number) - (a[filters.sortBy] as number)
    })
    return filtered
  }, [filters, results])

  const stopSearch = () => {
    abortRef.current?.abort()
    setIsLoading(false)
    setStatus('Search stopped.')
  }

  return {
    filters,
    setFilters,
    results: filteredResults,
    rawResults: results,
    status,
    isLoading,
    error,
    runSearch,
    stopSearch,
  }
}
