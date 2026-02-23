export type HeatTrend = 'rising' | 'steady' | 'declining'

export type OpportunityLabel = 'STRONG' | 'MODERATE' | 'MARGINAL' | 'WEAK'

export interface ArtistEnriched {
  name?: string
  sp_followers?: number
  sp_monthly_listeners?: number
  career_stage?: string
  momentum?: string
  geo_cities: Array<{ name: string; code2?: string; listeners?: number; affinity?: number }>
}

export interface OpportunityScore {
  overall: number
  label: OpportunityLabel
  demand: number
  conversion: number
  momentum: number
}

export interface RevenueTier {
  estimated_streams: number
  revenue: Record<string, number>
}

export interface TrackResult {
  track_id: number
  title: string
  original_song?: string
  permalink_url: string
  genre?: string
  created_at?: string
  remix_artist?: string
  original_artist?: string
  sc_user: {
    username?: string
    followers_count: number
    track_count: number
    avatar_url?: string
  }
  plays: number
  likes: number
  reposts: number
  comments: number
  engagement_rate: number
  daily_velocity: number
  days_live: number
  heat_score: number
  heat_trend: HeatTrend
  opportunity_score: OpportunityScore
  remix_artist_enriched: ArtistEnriched
  original_artist_enriched: ArtistEnriched
  revenue: {
    projections: {
      conservative: RevenueTier
      mid: RevenueTier
      optimistic: RevenueTier
    }
  }
  viability: {
    clears_threshold: boolean
    recommendation: string
    mid_revenue?: number
    threshold?: number
  }
}

export interface LicensingEntry {
  party: string
  publisher: string
  role: string
  share_pct: number
}

export interface LicensingPayload {
  track_id: number
  split_set: string
  updated_at: string
  entries: LicensingEntry[]
}

export interface SearchFilters {
  artistName: string
  songName: string
  songArtistName: string
  scLink: string
  catalogLimitRemixes: number
  tracksToFetch: number
  sortBy: 'heat_score' | 'opportunity_score' | 'daily_velocity'
  genre: string
  region: string
  careerStages: string[]
  minAccountReach: number
  maxAccountReach: number
  heatMin: number
  heatMax: number
  enrichChartmetric: boolean
  checkOfficialRelease: boolean
}

export type SearchMode =
  | 'catalog_search'
  | 'artist_search'
  | 'song_search'
  | 'remix_browse'
  | 'sc_link_lookup'

export interface UiTab {
  group: string
  label: string
  key: string
  active: boolean
}

export interface UiMetadata {
  organization: string
  tabs: UiTab[]
  default_mode?: SearchMode
  placeholders?: Partial<
    Record<
      SearchMode,
      {
        title: string
        description: string
        next_steps: string[]
      }
    >
  >
  filters: {
    genres: string[]
    regions: string[]
    career_stages: string[]
    tracks_to_fetch: { min: number; max: number; default: number }
    account_reach: { min: number; max: number; default_min: number; default_max: number }
    heat_score: { min: number; max: number; default_min: number; default_max: number }
  }
}
