# Song Case Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Song Case Page that shows all remixes of an original song in a visual bar chart, with remix artist profiles, an auto-generated insight callout, and a session-scoped Watch List.

**Architecture:** Pure frontend — no new backend endpoints required. The page groups existing `TrackResult` data from the current search results by original song. `App.tsx` passes the original track + its remixes down to a new `SongCasePage` component. Watch List is React state in `App.tsx`, shared via props.

**Tech Stack:** React 18, TypeScript, existing CSS custom properties (no new libraries)

---

## File Map

| Action | File | Responsibility |
|--------|------|----------------|
| Modify | `frontend/src/types/index.ts` | Add `'song_case'` to `SearchMode`; add `SongCaseData` interface |
| Modify | `frontend/src/App.tsx` | Add `activeSongCase`, `watchList` state; compute case from results; render `SongCasePage` |
| Modify | `frontend/src/components/Header.tsx` | Add `'song_case'` to `MODE_KEYS`; render Watch List badge |
| Modify | `frontend/src/components/ResultsTable.tsx` | Add "Case Page →" button to actions column |
| Create | `frontend/src/components/SongCasePage.tsx` | Full song case page: header, chart, artist profiles, insight |
| Create | `frontend/src/components/WatchList.tsx` | Watch List panel: cards, remove, export |
| Modify | `frontend/src/App.css` | Styles for new components |

---

## Task 1: Add types and data shape

**Files:**
- Modify: `frontend/src/types/index.ts`

- [ ] **Step 1: Add `'song_case'` to `SearchMode`**

Open `frontend/src/types/index.ts`. Change:
```ts
export type SearchMode =
  | 'catalog_search'
  | 'catalog_scatter'
  | 'artist_search'
  | 'song_search'
  | 'remix_browse'
  | 'sc_link_lookup'
```
to:
```ts
export type SearchMode =
  | 'catalog_search'
  | 'catalog_scatter'
  | 'artist_search'
  | 'song_search'
  | 'remix_browse'
  | 'sc_link_lookup'
  | 'song_case'
```

- [ ] **Step 2: Add `SongCaseData` and `WatchListEntry` interfaces**

Append to `frontend/src/types/index.ts`:
```ts
export interface SongCaseData {
  original: TrackResult          // row where is_reference_original === true
  unofficialRemixes: TrackResult[] // SC-sourced remixes, sorted by plays desc
}

export interface WatchListEntry {
  id: string                     // `${original.track_id}` — unique per case
  songTitle: string
  artist: string
  topRemixArtist: string
  topRemixPlays: number
  insight: string
}
```

- [ ] **Step 3: Verify TypeScript is happy**

Run: `cd /Users/adamguerin/Documents/Hackathon/mom/frontend && npx tsc --noEmit`
Expected: No errors related to the new types (existing errors, if any, are pre-existing)

- [ ] **Step 4: Commit**

```bash
cd /Users/adamguerin/Documents/Hackathon/mom
git add frontend/src/types/index.ts
git commit -m "feat: add song_case mode and SongCaseData types"
```

---

## Task 2: "Case Page →" button in ResultsTable

**Files:**
- Modify: `frontend/src/components/ResultsTable.tsx`

Context: The existing actions column has "Opportunity →" and "Action →" buttons. We add a third: "Case Page →" that calls a new `onOpenCasePage` prop.

- [ ] **Step 1: Add `onOpenCasePage` prop**

Change the `ResultsTableProps` interface from:
```ts
interface ResultsTableProps {
  rows: TrackResult[]
  selectedTrackId: number | null
  onToggleTrackSelect: (track: TrackResult) => void
}
```
to:
```ts
interface ResultsTableProps {
  rows: TrackResult[]
  selectedTrackId: number | null
  onToggleTrackSelect: (track: TrackResult) => void
  onOpenCasePage: (track: TrackResult) => void
}
```

- [ ] **Step 2: Destructure and wire the prop**

Update the function signature:
```ts
export function ResultsTable({ rows, selectedTrackId, onToggleTrackSelect, onOpenCasePage }: ResultsTableProps) {
```

- [ ] **Step 3: Add the button in the actions cell**

Find the actions `<td>` block (around line 104):
```tsx
<div className="action-row">
  <button className="btn-opportunity" onClick={() => onToggleTrackSelect(row)} type="button">
    Opportunity →
  </button>
  <button className="btn-action" type="button">
    Action →
  </button>
</div>
```
Replace with:
```tsx
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
```

- [ ] **Step 4: Fix the call site in App.tsx**

`App.tsx` passes props to `<ResultsTable>`. TypeScript will now error because `onOpenCasePage` is missing. Add a placeholder for now:
```tsx
<ResultsTable
  rows={results}
  selectedTrackId={selectedTrack?.track_id ?? null}
  onToggleTrackSelect={handleToggleTrackSelect}
  onOpenCasePage={() => {}}   // wired up in Task 4
/>
```

- [ ] **Step 5: Verify no TypeScript errors**

Run: `cd /Users/adamguerin/Documents/Hackathon/mom/frontend && npx tsc --noEmit`
Expected: Clean

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/ResultsTable.tsx frontend/src/App.tsx
git commit -m "feat: add Case Page button to results table actions"
```

---

## Task 3: Build SongCasePage component

**Files:**
- Create: `frontend/src/components/SongCasePage.tsx`

This component receives a `SongCaseData` and renders the full case page. It also receives `onAddToWatchList` and `onClose` callbacks.

Key rendering logic:
- The bar chart scales all bars relative to the original song's `plays` count (= 100% width).
- For unofficial remixes with `plays > 10% of original`, show highlight border.
- Insight is composed client-side: find the top unofficial remix, compare its `plays` to the sum of all official remix Spotify streams (not available in current data — compare to other unofficial remixes instead), note DSP absence.
- "Not on DSPs" is always true for unofficial remixes found on SoundCloud (they wouldn't be in the pipeline if already released).

- [ ] **Step 1: Create the file with scaffold**

```tsx
// frontend/src/components/SongCasePage.tsx
import type { SongCaseData, TrackResult, WatchListEntry } from '../types'

// Define compact once here. Do NOT redefine it in Step 2.
function compact(n: number): string {
  return Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(n)
}

interface SongCasePageProps {
  data: SongCaseData
  onAddToWatchList: (entry: WatchListEntry) => void
  onClose: () => void
}

function compact(n: number): string {
  return Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(n)
}

function buildInsight(data: SongCaseData): string {
  const { original, unofficialRemixes } = data
  if (unofficialRemixes.length === 0) return 'No unofficial remixes found for this track.'
  const top = unofficialRemixes[0]
  const artistName = top.remix_artist || top.sc_user.username || 'An artist'
  const streams = compact(top.plays)
  return `${artistName}'s unofficial remix has ${streams} SoundCloud streams and has never been released on any DSP.`
}

export function SongCasePage({ data, onAddToWatchList, onClose }: SongCasePageProps) {
  const { original, unofficialRemixes } = data
  const maxPlays = Math.max(original.plays, ...unofficialRemixes.map((r) => r.plays), 1)
  const insight = buildInsight(data)
  const topRemix = unofficialRemixes[0] ?? null

  const songTitle = original.original_song || original.title
  const artistName = original.original_artist || original.original_artist_enriched?.name || 'Unknown'
  const label = original.original_artist_enriched?.record_label || 'Unknown'
  const isrc = original.original_track_enriched?.isrc || 'N/A'
  const releaseDate = original.original_track_enriched?.release_date
    ? new Date(original.original_track_enriched.release_date).getFullYear()
    : 'N/A'

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
            {label !== 'Unknown' && <> &nbsp;·&nbsp; {label}</>}
            {releaseDate !== 'N/A' && <> &nbsp;·&nbsp; {releaseDate}</>}
            {isrc !== 'N/A' && <> &nbsp;·&nbsp; <span className="scp-isrc">{isrc}</span></>}
          </div>
        </div>
        <div className="scp-header-actions">
          <button className="scp-close-btn" type="button" onClick={onClose}>← Back</button>
        </div>
      </div>

      {/* Legend */}
      <div className="scp-legend">
        <span className="scp-legend-item"><span className="scp-dot scp-dot-sc" />SoundCloud</span>
        <span className="scp-legend-item"><span className="scp-dot scp-dot-sp" />Spotify</span>
        <span className="scp-legend-item scp-legend-muted"><span className="scp-dot scp-dot-none" />Not on DSPs</span>
      </div>

      {/* Chart */}
      <div className="scp-chart">
        {/* Original Song */}
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

        {/* Unofficial Remixes */}
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
            <button className="btn-primary" type="button">Recommend Release</button>
            <button className="btn-ghost" type="button" onClick={handleAddToWatchList}>
              Add to Watch List
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Add the `TrackRow` sub-component in the same file**

Add above `SongCasePage`. **Do NOT redeclare `compact` here** — it was defined in Step 1.

Note: `ArtistEnriched` has `sp_monthly_listeners`, `sp_followers`, `tiktok_followers`, `career_stage`, `momentum` — but no Instagram field. Show TikTok followers in place of Instagram where available.

```tsx
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
```

- [ ] **Step 3: Verify TypeScript**

Run: `cd /Users/adamguerin/Documents/Hackathon/mom/frontend && npx tsc --noEmit`
Expected: Clean (fix any type errors before continuing)

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/SongCasePage.tsx
git commit -m "feat: add SongCasePage component with bar chart and insight callout"
```

---

## Task 4: Build WatchList component

**Files:**
- Create: `frontend/src/components/WatchList.tsx`

The Watch List is a panel that overlays the page (or slides in from the right). It receives its entries and callbacks from App.tsx (session state lives in App).

- [ ] **Step 1: Create `WatchList.tsx`**

```tsx
// frontend/src/components/WatchList.tsx
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
        <button className="watchlist-close" type="button" onClick={onClose}>×</button>
      </div>

      {entries.length === 0 && (
        <p className="watchlist-empty">No cases saved yet. Click "Add to Watch List" on a Song Case Page.</p>
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
```

- [ ] **Step 2: Verify TypeScript**

Run: `cd /Users/adamguerin/Documents/Hackathon/mom/frontend && npx tsc --noEmit`
Expected: Clean

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/WatchList.tsx
git commit -m "feat: add WatchList panel component"
```

---

## Task 5: Wire everything into App.tsx

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/components/Header.tsx`

- [ ] **Step 1: Add imports to App.tsx**

At the top of `App.tsx`, add:
```tsx
import { SongCasePage } from './components/SongCasePage'
import { WatchList } from './components/WatchList'
import type { SongCaseData, WatchListEntry } from './types'
```

- [ ] **Step 2: Add new state variables to App.tsx**

Inside `function App()`, after the existing state declarations, add:
```tsx
const [activeSongCase, setActiveSongCase] = useState<SongCaseData | null>(null)
const [watchList, setWatchList] = useState<WatchListEntry[]>([])
const [showWatchList, setShowWatchList] = useState(false)
```

- [ ] **Step 3: Add `handleOpenCasePage` function to App.tsx**

After `handleToggleTrackSelect`, add:
```tsx
const handleOpenCasePage = (track: TrackResult) => {
  // Find the reference original for this track's original song
  const originalSong = track.original_song
  const original = results.find(
    (r) => r.is_reference_original && r.original_song === originalSong
  ) ?? track  // fallback: use the track itself if no reference found

  const unofficialRemixes = results
    .filter((r) => !r.is_reference_original && r.original_song === originalSong)
    .sort((a, b) => b.plays - a.plays)

  setActiveSongCase({ original, unofficialRemixes })
  setActiveMode('song_case')
}
```

- [ ] **Step 4: Add Watch List handlers to App.tsx**

```tsx
const handleAddToWatchList = (entry: WatchListEntry) => {
  setWatchList((prev) => {
    if (prev.some((e) => e.id === entry.id)) return prev  // no duplicates
    return [...prev, entry]
  })
}

const handleRemoveFromWatchList = (id: string) => {
  setWatchList((prev) => prev.filter((e) => e.id !== id))
}
```

- [ ] **Step 5: Update `isSupportedMode` to exclude `song_case`**

Change:
```tsx
const isSupportedMode =
  activeMode === 'catalog_search' ||
  activeMode === 'catalog_scatter' ||
  activeMode === 'artist_search' ||
  activeMode === 'song_search' ||
  activeMode === 'sc_link_lookup'
```
to:
```tsx
const isSupportedMode =
  activeMode === 'catalog_search' ||
  activeMode === 'catalog_scatter' ||
  activeMode === 'artist_search' ||
  activeMode === 'song_search' ||
  activeMode === 'sc_link_lookup'

const isSongCase = activeMode === 'song_case'
```

- [ ] **Step 6: Wire `onOpenCasePage` to ResultsTable in JSX**

Change the placeholder `() => {}` from Task 2 to:
```tsx
onOpenCasePage={handleOpenCasePage}
```

- [ ] **Step 7: Render SongCasePage and WatchList in JSX**

In `App.tsx`, find the opening `<main className="main-content">` tag. Immediately after it, insert:
```tsx
{isSongCase && activeSongCase ? (
  <SongCasePage
    data={activeSongCase}
    onAddToWatchList={handleAddToWatchList}
    onClose={() => setActiveMode('catalog_search')}
  />
) : (
```
Then scroll to the closing `</main>` tag and before it insert the closing paren + brace:
```tsx
)}
```
Also add the WatchList just before `</main>`:
```tsx
  {showWatchList && (
    <WatchList
      entries={watchList}
      onRemove={handleRemoveFromWatchList}
      onClose={() => setShowWatchList(false)}
    />
  )}
```
Do NOT delete any existing JSX inside `<main>` — just wrap the existing content in the `else` branch of the conditional.

- [ ] **Step 8: Add Watch List badge to Header**

Pass two new props to `<Header>`:
```tsx
<Header
  ...existing props...
  watchListCount={watchList.length}
  onOpenWatchList={() => setShowWatchList((prev) => !prev)}
/>
```

Update `Header.tsx`:

Add to `HeaderProps`:
```tsx
watchListCount: number
onOpenWatchList: () => void
```

Add to `MODE_KEYS`:
```tsx
const MODE_KEYS: SearchMode[] = [
  'catalog_search',
  'catalog_scatter',
  'artist_search',
  'song_search',
  'remix_browse',
  'sc_link_lookup',
  'song_case',
]
```

Add Watch List badge in the `header-right` div, before `<span className="build-stamp">`:
```tsx
{watchListCount > 0 && (
  <button className="watchlist-badge" type="button" onClick={onOpenWatchList}>
    Watch List ({watchListCount})
  </button>
)}
```

- [ ] **Step 9: Verify TypeScript**

Run: `cd /Users/adamguerin/Documents/Hackathon/mom/frontend && npx tsc --noEmit`
Expected: Clean — fix any errors before continuing

- [ ] **Step 10: Commit**

```bash
git add frontend/src/App.tsx frontend/src/components/Header.tsx
git commit -m "feat: wire SongCasePage and WatchList into App"
```

---

## Task 6: Add CSS styles

**Files:**
- Modify: `frontend/src/App.css`

- [ ] **Step 1: Read the bottom of App.css first**

Run: `tail -30 /Users/adamguerin/Documents/Hackathon/mom/frontend/src/App.css`

Note the existing CSS variable names (e.g. `--color-bg`, `--color-text`, `--accent`) — use these in new rules.

- [ ] **Step 2: Append Song Case Page styles**

Append to `App.css`:
```css
/* ── Song Case Page ─────────────────────────────────────── */
.song-case-page {
  padding: 20px 24px;
  max-width: 900px;
}

.scp-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.scp-title { font-size: 20px; font-weight: 700; margin: 0 0 4px; }
.scp-meta { font-size: 12px; opacity: 0.6; }
.scp-isrc { font-size: 11px; opacity: 0.5; }

.scp-close-btn {
  background: transparent;
  border: 1px solid rgba(255,255,255,0.2);
  color: inherit;
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.scp-legend {
  display: flex;
  gap: 16px;
  font-size: 11px;
  margin-bottom: 16px;
  opacity: 0.8;
}
.scp-legend-item { display: flex; align-items: center; gap: 5px; }
.scp-legend-muted { opacity: 0.5; }
.scp-dot {
  width: 10px; height: 10px; border-radius: 2px; display: inline-block;
}
.scp-dot-sc { background: #ff8800; }
.scp-dot-sp { background: #1DB954; }
.scp-dot-none { border: 1px dashed rgba(255,255,255,0.4); }

.scp-section-label {
  font-size: 10px;
  letter-spacing: 0.5px;
  opacity: 0.4;
  margin-bottom: 6px;
  margin-top: 4px;
}
.scp-section-divider {
  border-top: 1px solid rgba(255,255,255,0.07);
  padding-top: 10px;
  margin-top: 8px;
}

.scp-track-row {
  margin-bottom: 10px;
  border-radius: 6px;
  padding: 4px 0;
}
.scp-track-highlight {
  border: 1px solid rgba(255,136,0,0.33);
  background: rgba(255,136,0,0.04);
  padding: 8px;
}

.scp-track-bars { display: flex; align-items: flex-start; gap: 8px; }
.scp-track-label {
  width: 140px;
  flex-shrink: 0;
  font-size: 11px;
  text-align: right;
  padding-top: 2px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
  flex-wrap: wrap;
}
.scp-bars { flex: 1; display: flex; flex-direction: column; gap: 4px; }

.scp-bar-row { display: flex; align-items: center; gap: 6px; }
.scp-bar-platform { width: 18px; font-size: 10px; opacity: 0.4; flex-shrink: 0; }
.scp-bar-track {
  flex: 1;
  background: rgba(255,255,255,0.06);
  border-radius: 3px;
  height: 15px;
  position: relative;
  overflow: hidden;
}
.scp-bar-fill {
  height: 100%;
  border-radius: 3px;
  display: flex;
  align-items: center;
  min-width: 3px;
  transition: width 0.3s ease;
}
.scp-bar-label { padding-left: 6px; font-size: 10px; color: rgba(0,0,0,0.8); white-space: nowrap; }
.scp-bar-empty {
  height: 100%;
  border: 1px dashed rgba(255,255,255,0.15);
  border-radius: 3px;
  display: flex;
  align-items: center;
}
.scp-bar-none { padding-left: 8px; font-size: 10px; opacity: 0.35; font-style: italic; }

.scp-badge {
  font-size: 9px;
  padding: 1px 4px;
  border-radius: 3px;
  white-space: nowrap;
}
.scp-badge-official { background: rgba(76,175,80,0.15); color: #4caf50; }
.scp-badge-unofficial { background: rgba(255,136,0,0.15); color: #ff8800; }

.scp-artist-profile {
  display: flex;
  gap: 10px;
  padding: 6px 8px;
  background: rgba(255,255,255,0.05);
  border-radius: 5px;
  font-size: 10px;
  margin-top: 6px;
  margin-left: 148px;
  flex-wrap: wrap;
  align-items: center;
}
.scp-artist-label { opacity: 0.4; font-size: 9px; letter-spacing: 0.5px; }
.scp-artist-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
}
.scp-artist-stat strong { font-size: 11px; }
.scp-artist-stat span { opacity: 0.45; font-size: 9px; }

.scp-insight {
  margin-top: 16px;
  background: rgba(107,47,255,0.1);
  border: 1px solid rgba(107,47,255,0.33);
  border-radius: 8px;
  padding: 14px;
}
.scp-insight-label {
  font-size: 10px;
  letter-spacing: 0.5px;
  opacity: 0.6;
  margin-bottom: 8px;
}
.scp-insight-text { font-size: 13px; line-height: 1.6; margin: 0 0 10px; }
.scp-insight-actions { display: flex; gap: 8px; flex-wrap: wrap; }

/* ── Watch List Panel ───────────────────────────────────── */
.watchlist-panel {
  position: fixed;
  top: 0; right: 0;
  width: 360px;
  height: 100vh;
  background: var(--color-surface, #1a1a2e);
  border-left: 1px solid rgba(255,255,255,0.1);
  z-index: 100;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow-y: auto;
  box-shadow: -4px 0 20px rgba(0,0,0,0.4);
}
.watchlist-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.watchlist-title { font-size: 16px; font-weight: 600; margin: 0; }
.watchlist-close {
  background: transparent; border: none; color: inherit;
  font-size: 20px; cursor: pointer; opacity: 0.6; padding: 0 4px;
}
.watchlist-empty { font-size: 12px; opacity: 0.5; line-height: 1.6; }
.watchlist-cards { display: flex; flex-direction: column; gap: 10px; }
.watchlist-card {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  padding: 12px;
}
.watchlist-card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 4px; }
.watchlist-card-title { font-size: 13px; font-weight: 600; }
.watchlist-card-artist { font-size: 11px; opacity: 0.6; }
.watchlist-remove { background: transparent; border: none; color: inherit; cursor: pointer; opacity: 0.4; font-size: 16px; }
.watchlist-card-remix { font-size: 11px; opacity: 0.7; margin-bottom: 4px; }
.watchlist-card-insight { font-size: 11px; opacity: 0.5; line-height: 1.5; margin: 0; }

/* Watch List badge in header */
.watchlist-badge {
  background: #6b2fff;
  color: white;
  border: none;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
  white-space: nowrap;
}

/* Case Page button in table */
.btn-case-page {
  background: rgba(107,47,255,0.15);
  color: #a78bfa;
  border: 1px solid rgba(107,47,255,0.3);
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
  white-space: nowrap;
}
.btn-case-page:hover { background: rgba(107,47,255,0.25); }
```

- [ ] **Step 3: Verify the app builds and renders without errors**

Run: `cd /Users/adamguerin/Documents/Hackathon/mom/frontend && npm run build`
Expected: Build succeeds with no errors

- [ ] **Step 4: Smoke-test in browser**

Start dev server (`npm run dev`), run a search, click "Case Page →" on any result row. Verify:
- Song Case tab appears in nav
- Chart renders with correct bars
- Unofficial remix rows show artist profile strip
- "Add to Watch List" adds a badge to the header
- Clicking the badge opens the Watch List panel
- "× Back" closes the case page

- [ ] **Step 5: Commit**

```bash
git add frontend/src/App.css
git commit -m "feat: add Song Case Page and Watch List styles"
```

---

## Notes for Implementer

**Data gaps to expect:**
- `remix_artist_enriched.sp_followers` may be `undefined` in some rows — the artist profile strip gracefully skips missing fields.
- `original_track_enriched.isrc` may be absent — shows "N/A".
- Official Spotify remix data is not in the current `TrackResult` shape. The "OFFICIAL REMIXES ON DSPS" section from the mockup is not implemented in this plan — only the original song + unofficial SoundCloud remixes are shown. Add an official remixes section as a follow-up if needed.

**`handleOpenCasePage` grouping assumption:**
- Results from catalog_search group rows by `original_song` string. If `original_song` is `undefined` on some rows, those rows fall back to using themselves as the original. This is fine for demo purposes.
