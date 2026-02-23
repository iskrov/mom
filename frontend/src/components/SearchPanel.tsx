import type { SearchFilters, SearchMode } from '../types'

interface SearchPanelProps {
  filters: SearchFilters
  onFiltersChange: (next: SearchFilters) => void
  onSearch: () => void
  isLoading: boolean
  activeMode: SearchMode
  catalogFileName?: string
  onCatalogFileChange: (file: File | null) => void
  genreOptions: string[]
  regionOptions: string[]
  careerOptions: string[]
  tracksRange: { min: number; max: number }
  accountReachRange: { min: number; max: number }
  heatRange: { min: number; max: number }
  isSupportedMode: boolean
  placeholder?: {
    title: string
    description: string
    next_steps: string[]
  }
}

export function SearchPanel({
  filters,
  onFiltersChange,
  onSearch,
  isLoading,
  activeMode,
  catalogFileName,
  onCatalogFileChange,
  genreOptions,
  regionOptions,
  careerOptions,
  tracksRange,
  accountReachRange,
  heatRange,
  isSupportedMode,
  placeholder,
}: SearchPanelProps) {
  const update = <K extends keyof SearchFilters>(key: K, value: SearchFilters[K]) => {
    onFiltersChange({ ...filters, [key]: value })
  }

  return (
    <aside className="search-panel">
      <section className="panel-section">
        <div className="section-title">
          {activeMode === 'artist_search'
            ? 'ARTIST SEARCH'
            : activeMode === 'song_search'
              ? 'SONG SEARCH'
              : activeMode === 'sc_link_lookup'
                ? 'SC LINK LOOKUP'
                : 'WORKFLOW'}
        </div>
        {activeMode === 'artist_search' && (
          <>
            <input
              className="text-input"
              value={filters.artistName}
              onChange={(e) => update('artistName', e.target.value)}
              placeholder="Miley Cyrus"
            />
            <div className="helper-text">IPI / IPN / ISNI</div>
          </>
        )}
        {activeMode === 'song_search' && (
          <>
            <input
              className="text-input"
              value={filters.songName}
              onChange={(e) => update('songName', e.target.value)}
              placeholder="Song title"
            />
            <input
              className="text-input stacked-input"
              value={filters.songArtistName}
              onChange={(e) => update('songArtistName', e.target.value)}
              placeholder="Original artist (optional)"
            />
          </>
        )}
        {activeMode === 'sc_link_lookup' && (
          <input
            className="text-input"
            value={filters.scLink}
            onChange={(e) => update('scLink', e.target.value)}
            placeholder="https://soundcloud.com/artist/track"
          />
        )}
        {activeMode === 'catalog_search' && (
          <>
            <input
              className="text-input"
              type="file"
              accept=".csv,.xml"
              onChange={(e) => onCatalogFileChange(e.target.files?.[0] ?? null)}
            />
            <div className="helper-text">{catalogFileName || 'Upload a .csv or .xml catalog file'}</div>
            <label className="checkbox-row">
              <span>Remixes per song</span>
              <input
                className="compact-number"
                type="number"
                min={1}
                max={20}
                value={filters.catalogLimitRemixes}
                onChange={(e) => update('catalogLimitRemixes', Number(e.target.value) || 1)}
              />
            </label>
          </>
        )}
        {!isSupportedMode && placeholder && (
          <div className="coming-soon-note">
            <strong>{placeholder.title}</strong>
            <p>{placeholder.description}</p>
          </div>
        )}
        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={filters.enrichChartmetric}
            onChange={(e) => update('enrichChartmetric', e.target.checked)}
          />
          Enrich with Chartmetric data
        </label>
        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={filters.checkOfficialRelease}
            onChange={(e) => update('checkOfficialRelease', e.target.checked)}
          />
          Check official release (MusicBrainz)
        </label>
        <button className="search-btn" type="button" onClick={onSearch} disabled={isLoading || !isSupportedMode}>
          {isLoading ? 'SEARCHING...' : 'SEARCH'}
        </button>
      </section>

      {isSupportedMode && (
        <>
          {activeMode !== 'sc_link_lookup' && (
            <section className="panel-section">
              <div className="section-title">TRACKS TO FETCH</div>
              <input
                type="range"
                min={tracksRange.min}
                max={tracksRange.max}
                value={filters.tracksToFetch}
                onChange={(e) => update('tracksToFetch', Number(e.target.value))}
              />
              <div className="value-row">{filters.tracksToFetch}</div>
            </section>
          )}

          {activeMode !== 'sc_link_lookup' && (
            <section className="panel-section">
              <div className="section-title">SORT BY</div>
              <select
                className="select-input"
                value={filters.sortBy}
                onChange={(e) => update('sortBy', e.target.value as SearchFilters['sortBy'])}
              >
                <option value="heat_score">Heat Score ↓</option>
                <option value="opportunity_score">Opportunity Score ↓</option>
                <option value="daily_velocity">Velocity ↓</option>
              </select>
            </section>
          )}

          <section className="panel-section">
            <div className="section-title">GENRE</div>
            <div className="pill-row">
              {genreOptions.map((option) => (
                <button
                  key={option}
                  className={`pill ${filters.genre === option ? 'active' : ''}`}
                  type="button"
                  onClick={() => update('genre', option)}
                >
                  {option}
                </button>
              ))}
            </div>
          </section>

          <section className="panel-section">
            <div className="section-title">REGION</div>
            <select
              className="select-input"
              value={filters.region}
              onChange={(e) => update('region', e.target.value)}
            >
              {regionOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </section>

          <section className="panel-section">
            <div className="section-title">REMIX ARTIST CAREER STAGE</div>
            <div className="pill-row">
              <button
                className={`pill ${filters.careerStages.length === 0 ? 'active' : ''}`}
                type="button"
                onClick={() => update('careerStages', [])}
              >
                All
              </button>
              {careerOptions.map((option) => {
                const selected = filters.careerStages.includes(option)
                return (
                  <button
                    key={option}
                    className={`pill ${selected ? 'active' : ''}`}
                    type="button"
                    onClick={() =>
                      update(
                        'careerStages',
                        selected
                          ? filters.careerStages.filter((item) => item !== option)
                          : [...filters.careerStages, option],
                      )
                    }
                  >
                    {option}
                  </button>
                )
              })}
            </div>
          </section>

          <section className="panel-section">
            <div className="section-title">REMIX ARTIST ACCOUNT REACH</div>
            <div className="range-labels">
              <span>{filters.minAccountReach.toLocaleString()}</span>
              <span>{filters.maxAccountReach.toLocaleString()}</span>
            </div>
            <input
              type="range"
              min={accountReachRange.min}
              max={accountReachRange.max}
              step={10000}
              value={filters.maxAccountReach}
              onChange={(e) => update('maxAccountReach', Number(e.target.value))}
            />
          </section>

          <section className="panel-section">
            <div className="section-title">HEAT SCORE RANGE</div>
            <div className="range-labels">
              <span>{filters.heatMin.toFixed(1)}</span>
              <span>{filters.heatMax.toFixed(1)}</span>
            </div>
            <input
              type="range"
              min={heatRange.min}
              max={heatRange.max}
              step={0.1}
              value={filters.heatMax}
              onChange={(e) => update('heatMax', Number(e.target.value))}
            />
          </section>
        </>
      )}
    </aside>
  )
}
