import { useEffect, useMemo, useState } from 'react'
import './App.css'

import { fetchLicensing, fetchUiMetadata } from './api/client'
import { Header } from './components/Header'
import { ResultsTable } from './components/ResultsTable'
import { ScatterPlotView } from './components/ScatterPlotView'
import { SearchPanel } from './components/SearchPanel'
import { SongCasePage } from './components/SongCasePage'
import { SummaryBar } from './components/SummaryBar'
import { TrackDetail } from './components/TrackDetail'
import { WatchList } from './components/WatchList'
import { useSearch } from './hooks/useSearch'
import type { LicensingPayload, SearchMode, SongCaseData, TrackResult, UiMetadata, WatchListEntry } from './types'
import { downloadResultsAsCsv } from './utils/exportCsv'

const DEFAULT_UI_META: UiMetadata = {
  organization: 'Warner Music Group',
  default_mode: 'artist_search',
  tabs: [
    { group: 'RIGHTSHOLDER', label: 'Catalog Search', key: 'catalog_search', active: false },
    { group: 'RIGHTSHOLDER', label: 'Catalog Graph', key: 'catalog_scatter', active: false },
    { group: 'RIGHTSHOLDER', label: 'Artist Search', key: 'artist_search', active: true },
    { group: 'RIGHTSHOLDER', label: 'Song Search', key: 'song_search', active: false },
    { group: 'DISCOVERY', label: 'Remix Browse', key: 'remix_browse', active: false },
    { group: 'DISCOVERY', label: 'SC Link Lookup', key: 'sc_link_lookup', active: false },
    { group: 'DISCOVERY', label: 'Song Case', key: 'song_case', active: false },
  ],
  filters: {
    genres: ['All', 'Pop', 'Hip-Hop', 'EDM', 'R&B', 'Latin'],
    regions: ['Global'],
    career_stages: ['Developing', 'Mid-level', 'Established'],
    tracks_to_fetch: { min: 1, max: 20, default: 10 },
    account_reach: { min: 0, max: 500000, default_min: 0, default_max: 500000 },
    heat_score: { min: 0, max: 10, default_min: 0, default_max: 10 },
  },
  placeholders: {
    catalog_search: {
      title: 'Catalog Search is coming soon',
      description: 'Bulk CSV/XML upload flow will rank remix opportunities across your catalog.',
      next_steps: [
        'Upload parser integration from scripts/catalog.py',
        'Batch SSE enrichment job orchestration',
        'Progress + resumable processing UI',
      ],
    },
    remix_browse: {
      title: 'Remix Browse is coming soon',
      description: 'Discovery mode for trending remix candidates by genre, region, and velocity.',
      next_steps: [
        'Discovery query presets and saved views',
        'Top charts + trend-signal fusion',
        'Review queue and assignment actions',
      ],
    },
  },
}

function App() {
  const [isDark, setIsDark] = useState(false)
  const [activeMode, setActiveMode] = useState<SearchMode>('artist_search')
  const [catalogFile, setCatalogFile] = useState<File | null>(null)
  const [selectedTrack, setSelectedTrack] = useState<TrackResult | null>(null)
  const [licensing, setLicensing] = useState<LicensingPayload | null>(null)
  const [loadingLicensing, setLoadingLicensing] = useState(false)
  const [uiMeta, setUiMeta] = useState<UiMetadata>(DEFAULT_UI_META)

  const [activeSongCase, setActiveSongCase] = useState<SongCaseData | null>(null)
  const [watchList, setWatchList] = useState<WatchListEntry[]>([])
  const [showWatchList, setShowWatchList] = useState(false)

  const { filters, setFilters, results, rawResults, status, isLoading, error, runSearch, stopSearch } = useSearch()
  const isSongCase = activeMode === 'song_case'
  const isSupportedMode =
    activeMode === 'catalog_search' ||
    activeMode === 'catalog_scatter' ||
    activeMode === 'artist_search' ||
    activeMode === 'song_search' ||
    activeMode === 'sc_link_lookup'
  const placeholder = uiMeta.placeholders?.[activeMode]
  const showDetailPanel = isSupportedMode && selectedTrack !== null

  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark)
  }, [isDark])

  useEffect(() => {
    fetchUiMetadata()
      .then((meta) => {
        setUiMeta(meta)
        const selected =
          meta.default_mode ||
          (meta.tabs.find((tab) => tab.active)?.key as SearchMode | undefined) ||
          'artist_search'
        if (
          selected === 'catalog_search' ||
          selected === 'catalog_scatter' ||
          selected === 'artist_search' ||
          selected === 'song_search' ||
          selected === 'remix_browse' ||
          selected === 'sc_link_lookup'
        ) {
          setActiveMode(selected)
        }
      })
      .catch(() => {
        // Keep fallback metadata if endpoint is unavailable.
      })
  }, [])

  useEffect(() => {
    if (!selectedTrack) return
    setLoadingLicensing(true)
    fetchLicensing(
      selectedTrack.track_id,
      selectedTrack.original_song ?? undefined,
      selectedTrack.original_artist ?? undefined,
    )
      .then(setLicensing)
      .finally(() => setLoadingLicensing(false))
  }, [selectedTrack])

  useEffect(() => {
    setSelectedTrack(null)
    setLicensing(null)
  }, [activeMode])

  const navTabs = useMemo(() => {
    const hasScatter = uiMeta.tabs.some((tab) => tab.key === 'catalog_scatter')
    if (hasScatter) return uiMeta.tabs
    const tabs = [...uiMeta.tabs]
    const catalogIndex = tabs.findIndex((tab) => tab.key === 'catalog_search')
    const scatterTab = {
      group: 'RIGHTSHOLDER',
      label: 'Catalog Graph',
      key: 'catalog_scatter',
      active: false,
    }
    if (catalogIndex >= 0) {
      tabs.splice(catalogIndex + 1, 0, scatterTab)
      return tabs
    }
    return [scatterTab, ...tabs]
  }, [uiMeta.tabs])

  const handleToggleTrackSelect = (track: TrackResult) => {
    setSelectedTrack((prev) => {
      if (prev?.track_id === track.track_id) {
        setLicensing(null)
        return null
      }
      return track
    })
  }

  const handleOpenCasePage = (track: TrackResult) => {
    const originalSong = track.original_song
    const referenceRow = results.find((r) => r.is_reference_original && r.original_song === originalSong)
    const original = referenceRow ?? track
    const unofficialRemixes = results
      .filter((r) => !r.is_reference_original && r.original_song === originalSong)
      .sort((a, b) => b.plays - a.plays)
    setActiveSongCase({ original, unofficialRemixes })
    setActiveMode('song_case')
  }

  const handleAddToWatchList = (entry: WatchListEntry) => {
    setWatchList((prev) => {
      if (prev.some((e) => e.id === entry.id)) return prev
      return [...prev, entry]
    })
  }

  const handleRemoveFromWatchList = (id: string) => {
    setWatchList((prev) => prev.filter((e) => e.id !== id))
  }

  return (
    <div className="app-shell">
      <Header
        isDark={isDark}
        onToggleTheme={() => setIsDark((prev) => !prev)}
        organization={uiMeta.organization}
        tabs={navTabs}
        activeMode={activeMode}
        onSelectMode={setActiveMode}
        watchListCount={watchList.length}
        onOpenWatchList={() => setShowWatchList((prev) => !prev)}
      />
      <div className={`content-grid ${showDetailPanel ? 'with-detail' : 'no-detail'}`}>
        <SearchPanel
          filters={filters}
          onFiltersChange={setFilters}
          onSearch={() => runSearch(activeMode, { catalogFile })}
          isLoading={isLoading}
          activeMode={activeMode}
          catalogFileName={catalogFile?.name}
          onCatalogFileChange={setCatalogFile}
          onStopSearch={stopSearch}
          genreOptions={uiMeta.filters.genres}
          regionOptions={uiMeta.filters.regions}
          careerOptions={uiMeta.filters.career_stages}
          tracksRange={
            activeMode === 'catalog_search' || activeMode === 'catalog_scatter'
              ? { min: 5, max: 100, step: 5 }
              : activeMode === 'artist_search'
                ? { min: 1, max: 200, step: 1 }
              : { min: uiMeta.filters.tracks_to_fetch.min, max: uiMeta.filters.tracks_to_fetch.max, step: 1 }
          }
          accountReachRange={{ min: uiMeta.filters.account_reach.min, max: uiMeta.filters.account_reach.max }}
          heatRange={{ min: uiMeta.filters.heat_score.min, max: uiMeta.filters.heat_score.max }}
          isSupportedMode={isSupportedMode}
          placeholder={placeholder}
        />
        <main className="main-content">
          {isSongCase && activeSongCase ? (
            <SongCasePage
              data={activeSongCase}
              onAddToWatchList={handleAddToWatchList}
              onClose={() => setActiveMode('catalog_search')}
            />
          ) : (
          <>
          <div className="status-row">
            <span>{status}</span>
            {error && <span className="status-error"> · {error}</span>}
            {results.length > 0 && (
              <button
                className="download-btn"
                type="button"
                onClick={() => {
                  const base = catalogFile
                    ? catalogFile.name.replace(/\.[^.]+$/, '')
                    : 'catalog'
                  const plays = filters.catalogMinPlays
                    ? `min${(filters.catalogMinPlays / 1000).toFixed(0)}k`
                    : 'anyplays'
                  const start = `song${filters.catalogOffset + 1}`
                  const max = filters.catalogCount > 0 ? `x${filters.catalogCount}` : 'xall'
                  downloadResultsAsCsv(results, `${base}_${plays}_${start}${max}_remix-radar.csv`)
                }}
              >
                Download CSV ({results.length})
              </button>
            )}
          </div>
          {isSupportedMode ? (
            <>
              <SummaryBar
                tracks={results}
                totalFound={rawResults.filter((row) => !row.is_reference_original).length}
              />
              {activeMode === 'catalog_scatter' && (
                <ScatterPlotView
                  rows={results}
                  selectedTrackId={selectedTrack?.track_id ?? null}
                  onSelectTrack={handleToggleTrackSelect}
                />
              )}
              <ResultsTable
                rows={results}
                selectedTrackId={selectedTrack?.track_id ?? null}
                onToggleTrackSelect={handleToggleTrackSelect}
                onOpenCasePage={handleOpenCasePage}
              />
            </>
          ) : (
            <section className="coming-soon-panel">
              <h3>{placeholder?.title ?? 'Workflow coming soon'}</h3>
              <p>{placeholder?.description ?? 'This workflow is planned for the next iteration.'}</p>
              <ul>
                {(placeholder?.next_steps ?? []).map((step) => (
                  <li key={step}>{step}</li>
                ))}
              </ul>
            </section>
          )}
          </>
          )}
        </main>
        {showDetailPanel && (
          <TrackDetail
            track={isSupportedMode ? selectedTrack : null}
            licensing={licensing}
            loadingLicensing={loadingLicensing}
            onClose={() => {
              setSelectedTrack(null)
              setLicensing(null)
            }}
          />
        )}
        {showWatchList && (
          <WatchList
            entries={watchList}
            onRemove={handleRemoveFromWatchList}
            onClose={() => setShowWatchList(false)}
          />
        )}
      </div>
    </div>
  )
}

export default App
