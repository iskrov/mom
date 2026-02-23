import type { SearchMode, UiTab } from '../types'
import { ThemeToggle } from './ThemeToggle'

interface HeaderProps {
  isDark: boolean
  onToggleTheme: () => void
  organization: string
  tabs: UiTab[]
  activeMode: SearchMode
  onSelectMode: (mode: SearchMode) => void
}

const MODE_KEYS: SearchMode[] = [
  'catalog_search',
  'artist_search',
  'song_search',
  'remix_browse',
  'sc_link_lookup',
]

export function Header({
  isDark,
  onToggleTheme,
  organization,
  tabs,
  activeMode,
  onSelectMode,
}: HeaderProps) {
  const normalizeGroup = (value: string) => value.trim().replace(/\s+/g, ' ').toUpperCase()
  let prevGroup = ''

  return (
    <header className="app-header">
      <div className="brand">
        <div className="brand-title">// REMIX RADAR</div>
        <div className="brand-subtitle">Search SoundCloud · Rank by signal</div>
      </div>

      <nav className="nav-tabs">
        {tabs.map((tab) => {
          const group = normalizeGroup(tab.group)
          const showGroup = group !== prevGroup
          prevGroup = group
          return (
            <div key={tab.key} className="tab-item">
              {showGroup ? <span className="nav-group">{group}</span> : <span className="nav-group-spacer" />}
              <button
                className={`tab ${activeMode === tab.key ? 'active' : ''}`}
                type="button"
                onClick={() => {
                  if (MODE_KEYS.includes(tab.key as SearchMode)) {
                    onSelectMode(tab.key as SearchMode)
                  }
                }}
              >
                {tab.label}
              </button>
            </div>
          )
        })}
      </nav>

      <div className="header-right">
        <span className="org-name">{organization}</span>
        <div className="avatar">JL</div>
        <ThemeToggle isDark={isDark} onToggle={onToggleTheme} />
      </div>
    </header>
  )
}
