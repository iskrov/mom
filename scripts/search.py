import os, sys, json, time, requests
import pandas as pd
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# ── Load env + Chartmetric client ─────────────────────────────────────────────
ROOT = Path("/Users/adamguerin/Documents/Sifted App")
load_dotenv(ROOT / ".env", override=True)
sys.path.insert(0, str(ROOT))
from scripts.platforms.chartmetric import ChartmetricClient

import musicbrainzngs
musicbrainzngs.set_useragent("SiftedApp", "0.1", "hello@sifted.com")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sifted · Track Radar",
    page_icon="🎵",
    layout="wide",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #f5f5f5;
    color: #1a1a1a;
}
h1, h2, h3 { font-family: 'Space Mono', monospace; }

.stApp { background-color: #f5f5f5; }

.radar-header {
    border-bottom: 2px solid #6b2fff;
    padding-bottom: 1rem;
    margin-bottom: 2rem;
}
.radar-header h1 {
    font-size: 2.4rem;
    color: #6b2fff;
    letter-spacing: -1px;
    margin: 0;
}
.radar-header p {
    color: #888;
    font-size: 0.9rem;
    margin: 0.3rem 0 0;
}

.stTextInput > div > div > input {
    background: #ffffff !important;
    border: 1px solid #ddd !important;
    border-radius: 6px !important;
    color: #1a1a1a !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #6b2fff !important;
    box-shadow: 0 0 0 2px rgba(107,47,255,0.15) !important;
}

.stSlider > div { color: #555; }

.stButton > button {
    background: #6b2fff !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.6rem 2rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

.metric-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
}
.metric-card {
    background: #ffffff;
    border: 1px solid #e8e8e8;
    border-radius: 8px;
    padding: 1rem 1.4rem;
    flex: 1;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.metric-card .label {
    font-size: 0.7rem;
    color: #999;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family: 'Space Mono', monospace;
}
.metric-card .value {
    font-size: 1.6rem;
    font-family: 'Space Mono', monospace;
    color: #6b2fff;
    font-weight: 700;
}

.stDataFrame {
    border: 1px solid #e8e8e8 !important;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

.stSelectbox > div > div {
    background: #ffffff !important;
    border-color: #ddd !important;
    color: #1a1a1a !important;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
CLIENT_ID     = os.getenv("SOUNDCLOUD_CLIENT_ID")
CLIENT_SECRET = os.getenv("SOUNDCLOUD_CLIENT_SECRET")
API_BASE      = "https://api.soundcloud.com"
TOKEN_URL     = "https://api.soundcloud.com/oauth2/token"
TOKEN_PATH    = ROOT / "token.json"

# ── SoundCloud helpers ────────────────────────────────────────────────────────
def like_count(t):
    return t.get("likes_count") if t.get("likes_count") is not None else t.get("favoritings_count")

def play_count(t):
    return t.get("playback_count") or t.get("play_count")

def api_get(url, access_token):
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    return requests.get(url, headers=headers, timeout=30)

def load_token():
    if not TOKEN_PATH.exists():
        return None
    return json.loads(TOKEN_PATH.read_text(encoding="utf-8"))

def refresh_access_token(refresh_token):
    data = {
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type":    "refresh_token",
        "refresh_token": refresh_token,
    }
    r = requests.post(TOKEN_URL, data=data, timeout=20)
    r.raise_for_status()
    return r.json()

def ensure_access_token():
    tok = load_token()
    if not tok or not tok.get("access_token"):
        raise RuntimeError("No token.json found. Run your OAuth flow first.")
    probe = api_get(f"{API_BASE}/me", tok["access_token"])
    if probe.status_code == 401 and tok.get("refresh_token"):
        new_tok = refresh_access_token(tok["refresh_token"])
        if "refresh_token" not in new_tok:
            new_tok["refresh_token"] = tok["refresh_token"]
        TOKEN_PATH.write_text(json.dumps(new_tok, indent=2), encoding="utf-8")
        tok = new_tok
    return tok["access_token"]

def fetch_user_followers(user_id, access_token):
    r = api_get(f"{API_BASE}/users/{user_id}", access_token)
    if r.status_code == 200:
        return r.json().get("followers_count", 0)
    return 0

def enrich_with_followers(tracks, access_token):
    user_ids = list({t["user"]["id"] for t in tracks if t.get("user")})
    follower_map = {}
    for uid in user_ids:
        follower_map[uid] = fetch_user_followers(uid, access_token)
        time.sleep(0.2)
    return follower_map

def search_tracks(query, access_token, limit=50):
    tracks = []
    url    = f"{API_BASE}/tracks"
    params = {"q": query, "limit": min(limit, 50), "offset": 0, "linked_partitioning": 1}

    progress = st.progress(0, text="Fetching tracks...")
    while url and len(tracks) < limit:
        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
        r = requests.get(url, headers=headers, params=params, timeout=30)
        if r.status_code == 429:
            st.warning("Rate limited — waiting 10s...")
            time.sleep(10)
            continue
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list):
            tracks.extend(data)
            break
        else:
            tracks.extend(data.get("collection", []))
            url    = data.get("next_href")
            params = {}
        pct = min(len(tracks) / limit, 1.0)
        progress.progress(pct, text=f"Fetched {len(tracks)} of {limit} tracks...")
        time.sleep(0.3)

    progress.empty()
    return tracks[:limit]

def build_dataframe(tracks, sort_by="like_count"):
    rows = []
    now  = pd.Timestamp.utcnow()

    for t in tracks:
        plays    = play_count(t) or 0
        likes    = like_count(t) or 0
        reposts  = t.get("reposts_count") or 0
        comments = t.get("comment_count") or 0

        duration_ms  = t.get("duration") or 0
        duration_min = round(duration_ms / 60000, 2)

        created_at = pd.to_datetime(t.get("created_at"), errors="coerce")
        age_days   = max((now - created_at).days, 1) if pd.notnull(created_at) else None

        like_to_stream_ratio = (likes / plays)   if plays > 0  else None
        repost_to_like_ratio = (reposts / likes) if likes > 0  else None

        genre = t.get("genre", "") or ""

        rows.append({
            "track_id":             t.get("id"),
            "title":                t.get("title"),
            "artist_name":          t.get("user", {}).get("username"),
            "genre":                genre.strip() if genre else "Unknown",
            "permalink_url":        t.get("permalink_url"),
            "created_at":           created_at,
            "track_age_days":       age_days,
            "duration_min":         duration_min,
            "play_count":           plays,
            "like_count":           likes,
            "comment_count":        comments,
            "reposts_count":        reposts,
            "plays_per_day":        round(plays    / age_days, 2) if age_days else None,
            "likes_per_day":        round(likes    / age_days, 2) if age_days else None,
            "reposts_per_day":      round(reposts  / age_days, 2) if age_days else None,
            "comments_per_day":     round(comments / age_days, 2) if age_days else None,
            "like_to_stream_pct":   round(like_to_stream_ratio * 100, 2) if like_to_stream_ratio is not None else None,
            "repost_to_like_pct":   round(repost_to_like_ratio * 100, 2) if repost_to_like_ratio is not None else None,
            "like_to_stream_ratio": like_to_stream_ratio,
            "repost_to_like_ratio": repost_to_like_ratio,
        })

    df = pd.DataFrame(rows).drop_duplicates(subset=["track_id"])
    df = df.sort_values(sort_by, ascending=False).reset_index(drop=True)
    df.index += 1
    return df

# ── Chartmetric enrichment ────────────────────────────────────────────────────
def enrich_with_chartmetric(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each unique artist in df, look them up on Chartmetric and fetch
    combined audience size (Spotify + Instagram + YouTube + TikTok followers).
    Results are cached per artist so we only hit the API once per unique name.
    """
    cm = ChartmetricClient()
    audience_cache = {}  # artist_name → combined_audience int or None

    unique_artists = df["artist_name"].dropna().unique().tolist()
    progress = st.progress(0, text="Fetching Chartmetric audience data...")

    for i, artist in enumerate(unique_artists):
        try:
            results = cm.find_artist(artist)
            if not results:
                audience_cache[artist] = None
                continue

            cm_id = results[0].get("id")
            if not cm_id:
                audience_cache[artist] = None
                continue

            # Fetch follower stats for each platform
            sp_followers = ig_followers = yt_subs = tt_followers = 0

            def latest(stats_list):
                if stats_list:
                    return stats_list[-1].get("value") or 0
                return 0

            try:
                sp = cm.get_artist_stats(cm_id, "spotify")
                sp_followers = latest(sp.get("followers", []))
            except Exception:
                pass
            time.sleep(0.3)

            try:
                ig = cm.get_artist_stats(cm_id, "instagram")
                ig_followers = latest(ig.get("followers", []))
            except Exception:
                pass
            time.sleep(0.3)

            try:
                yt = cm.get_artist_stats(cm_id, "youtube_channel")
                yt_subs = latest(yt.get("followers", []))
            except Exception:
                pass
            time.sleep(0.3)

            try:
                tt = cm.get_artist_stats(cm_id, "tiktok")
                tt_followers = latest(tt.get("followers", []))
            except Exception:
                pass
            time.sleep(0.3)

            combined = sp_followers + ig_followers + yt_subs + tt_followers
            audience_cache[artist] = combined if combined > 0 else None

        except Exception as e:
            audience_cache[artist] = None

        progress.progress((i + 1) / len(unique_artists), text=f"Chartmetric: {i+1}/{len(unique_artists)} artists")

    progress.empty()

    df["cm_combined_audience"] = df["artist_name"].map(audience_cache)
    return df

# ── MusicBrainz enrichment ────────────────────────────────────────────────────
def parse_original_artist_and_title(full_title: str):
    """
    Many SoundCloud remix titles follow the pattern:
      "Original Artist - Song Name (Remixer Remix)"
    Extract the original artist and clean song name for MusicBrainz lookup.
    Returns (original_artist, song_name) or (None, full_title) if no dash found.
    """
    import re
    # Split on first ' - ' to get "Artist" and "Song (Remix)"
    if " - " in full_title:
        parts = full_title.split(" - ", 1)
        original_artist = parts[0].strip()
        song_part = parts[1].strip()
    else:
        return None, full_title

    # Remove remix tags in parentheses: "(AVELLO REMIX)", "(Whethan Remix)" etc.
    song_name = re.sub(r'\([^)]*remix[^)]*\)', '', song_part, flags=re.IGNORECASE)
    song_name = re.sub(r'\([^)]*edit[^)]*\)', '', song_name, flags=re.IGNORECASE)
    song_name = re.sub(r'\([^)]*flip[^)]*\)', '', song_name, flags=re.IGNORECASE)
    song_name = re.sub(r'\([^)]*redo[^)]*\)', '', song_name, flags=re.IGNORECASE)
    song_name = song_name.strip()

    return original_artist, song_name


def check_official_release(title: str, score_threshold: int = 85) -> bool:
    """
    Parse the original artist + song name out of the SoundCloud title,
    then search MusicBrainz with both to avoid false positives.
    Only flags as Official if the original song has an official release —
    not the remix itself.
    """
    try:
        original_artist, song_name = parse_original_artist_and_title(title)

        if not song_name:
            return False

        kwargs = {"recording": song_name, "limit": 5}
        if original_artist:
            kwargs["artist"] = original_artist

        result = musicbrainzngs.search_recordings(**kwargs)

        for rec in result["recording-list"]:
            score = int(rec.get("ext:score", 0))
            if score < score_threshold:
                continue
            # If we have an original artist, verify it appears in the credit
            if original_artist:
                credited = rec.get("artist-credit-phrase", "").lower()
                # Accept if any word from original artist appears in credit
                artist_words = [w for w in original_artist.lower().split() if len(w) > 2]
                if not any(w in credited for w in artist_words):
                    continue
            for release in rec.get("release-list", []):
                if release.get("status") == "Official":
                    return True
        return False
    except Exception:
        return False

def enrich_with_musicbrainz(df: pd.DataFrame) -> pd.DataFrame:
    """
    Check each track title against MusicBrainz to see if it has
    an official release. Adds is_official (bool) column.
    """
    results = []
    progress = st.progress(0, text="Checking official releases...")
    total = len(df)

    for i, (_, row) in enumerate(df.iterrows()):
        is_official = check_official_release(title=row.get("title", ""))
        results.append(is_official)
        time.sleep(1.1)  # MusicBrainz rate limit: 1 req/sec
        progress.progress((i + 1) / max(total, 1), text=f"MusicBrainz: {i+1}/{total} tracks")

    progress.empty()
    df["is_official"] = results
    return df

# ── Viability score ───────────────────────────────────────────────────────────
def compute_viability_score(row) -> float:
    """
    0–10 score representing how worth it is to officially release this remix.
    Calibrated for SoundCloud scale: 1M streams / 50K likes = 10/10.
    """
    plays     = row.get("play_count") or 0
    likes     = row.get("like_count") or 0
    reposts   = row.get("reposts_count") or 0
    ppd       = row.get("plays_per_day") or 0
    audience  = row.get("cm_combined_audience") or 0
    lts_pct   = row.get("like_to_stream_pct") or 0   # engagement quality signal

    stream_score   = min(plays    / 100_000,  10)   # 1M streams = 10
    like_score     = min(likes    / 5_000,    10)   # 50K likes = 10
    repost_score   = min(reposts  / 1_000,    10)   # 10K reposts = 10
    velocity_score = min(ppd      / 500,      10)   # 5K plays/day = 10
    audience_score = min(audience / 500_000,  10)   # 5M combined audience = 10
    engagement_score = min(lts_pct / 5.0,    10)   # 5% like-to-stream = 10

    score = (
        stream_score     * 0.25 +
        like_score       * 0.20 +
        repost_score     * 0.10 +
        velocity_score   * 0.10 +
        audience_score   * 0.20 +
        engagement_score * 0.15
    )
    return round(min(score, 10), 2)

def apply_filters(df, genre_filter, repost_to_like_min, repost_to_like_max, like_stream_min, like_stream_max):
    filtered = df.copy()

    if genre_filter and "All" not in genre_filter:
        filtered = filtered[filtered["genre"].isin(genre_filter)]

    filtered = filtered[
        filtered["repost_to_like_pct"].isna() |
        (
            (filtered["repost_to_like_pct"] >= repost_to_like_min) &
            (filtered["repost_to_like_pct"] <= repost_to_like_max)
        )
    ]

    filtered = filtered[
        filtered["like_to_stream_pct"].isna() |
        (
            (filtered["like_to_stream_pct"] >= like_stream_min) &
            (filtered["like_to_stream_pct"] <= like_stream_max)
        )
    ]

    return filtered.reset_index(drop=True)

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="radar-header">
    <h1>// TRACK RADAR</h1>
    <p>Search SoundCloud · Rank by signal</p>
</div>
""", unsafe_allow_html=True)

col_query, col_limit, col_sort = st.columns([3, 1, 1])

with col_query:
    query = st.text_input("", placeholder="Enter a song title, artist, or keyword...", label_visibility="collapsed")

with col_limit:
    limit = st.slider("Tracks to fetch", min_value=10, max_value=100, value=50, step=10)

with col_sort:
    sort_options = {
        "Likes":              "like_count",
        "Streams":            "play_count",
        "Reposts":            "reposts_count",
        "Streams / Day":      "plays_per_day",
        "Like→Stream %":      "like_to_stream_pct",
        "Repost→Like %":      "repost_to_like_pct",
        "Viability Score":    "viability_score",
    }
    sort_label = st.selectbox("Sort by", list(sort_options.keys()))
    sort_by    = sort_options[sort_label]

# Enrichment toggles
col_enrich1, col_enrich2 = st.columns(2)
with col_enrich1:
    run_chartmetric = st.checkbox("Enrich with Chartmetric audience data", value=True)
with col_enrich2:
    run_musicbrainz = st.checkbox("Check official release (MusicBrainz)", value=True)

search_btn = st.button("⌕  SEARCH")

# ── Run search ────────────────────────────────────────────────────────────────
if search_btn and query.strip():
    try:
        access_token = ensure_access_token()
    except RuntimeError as e:
        st.error(str(e))
        st.stop()

    with st.spinner(f'Searching for "{query}"...'):
        tracks = search_tracks(query, access_token, limit=limit)

    if not tracks:
        st.warning("No tracks found. Try a different query.")
        st.stop()

    df = build_dataframe(tracks, sort_by="like_count")  # initial sort by likes before enrichment

    # Chartmetric enrichment
    if run_chartmetric:
        df = enrich_with_chartmetric(df)
    else:
        df["cm_combined_audience"] = None

    # MusicBrainz enrichment
    if run_musicbrainz:
        df = enrich_with_musicbrainz(df)
    else:
        df["is_official"] = False

    # Compute viability score
    df["viability_score"] = df.apply(compute_viability_score, axis=1)

    # Re-sort by user's chosen sort column if it exists
    if sort_by in df.columns:
        df = df.sort_values(sort_by, ascending=False).reset_index(drop=True)
        df.index += 1

    st.session_state["df"]    = df
    st.session_state["query"] = query

# ── Filters + display ─────────────────────────────────────────────────────────
if "df" in st.session_state:
    df    = st.session_state["df"]
    query = st.session_state.get("query", "results")

    fcol1, fcol2, fcol3 = st.columns(3)

    with fcol1:
        genres = sorted([g for g in df["genre"].unique() if g and g != "Unknown"])
        genres = ["All"] + genres
        genre_filter = st.multiselect("Genre", genres, default=["All"])

    with fcol2:
        rtl_max = float(df["repost_to_like_pct"].max()) if df["repost_to_like_pct"].notna().any() else 100.0
        rtl_max = max(round(rtl_max, 1), 0.1)
        repost_to_like_range = st.slider(
            "Repost→Like % range",
            min_value=0.0,
            max_value=rtl_max,
            value=(0.0, rtl_max),
            step=0.1,
        )

    with fcol3:
        lts_max = float(df["like_to_stream_pct"].max()) if df["like_to_stream_pct"].notna().any() else 100.0
        lts_max = min(round(lts_max, 1), 100.0)
        like_stream_range = st.slider(
            "Like→Stream % range",
            min_value=0.0,
            max_value=lts_max,
            value=(0.0, lts_max),
            step=0.1,
        )

    filtered_df = apply_filters(
        df,
        genre_filter=genre_filter,
        repost_to_like_min=repost_to_like_range[0],
        repost_to_like_max=repost_to_like_range[1],
        like_stream_min=like_stream_range[0],
        like_stream_max=like_stream_range[1],
    )

    # Summary metrics
    avg_like_stream = filtered_df["like_to_stream_pct"].mean()
    avg_viability   = filtered_df["viability_score"].mean() if "viability_score" in filtered_df else 0
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card"><div class="label">Tracks (filtered)</div><div class="value">{len(filtered_df)}</div></div>
        <div class="metric-card"><div class="label">Total Streams</div><div class="value">{filtered_df['play_count'].sum():,.0f}</div></div>
        <div class="metric-card"><div class="label">Total Likes</div><div class="value">{filtered_df['like_count'].sum():,.0f}</div></div>
        <div class="metric-card"><div class="label">Avg Like→Stream %</div><div class="value">{avg_like_stream:.1f}%</div></div>
        <div class="metric-card"><div class="label">Avg Viability</div><div class="value">{avg_viability:.2f}</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Build display table
    display_df = filtered_df[[
        "title", "artist_name", "genre", "play_count", "like_count",
        "like_to_stream_pct", "repost_to_like_pct", "plays_per_day",
        "cm_combined_audience", "is_official", "viability_score",
    ]].copy()

    # Format audience size
    display_df["cm_combined_audience"] = display_df["cm_combined_audience"].apply(
        lambda x: f"{int(x):,}" if pd.notna(x) and x > 0 else "—"
    )

    # Official release badge
    display_df["is_official"] = display_df["is_official"].apply(
        lambda x: "🏷 Official" if x else ""
    )

    display_df = display_df.rename(columns={
        "play_count":           "stream_count",
        "plays_per_day":        "streams_per_day",
        "repost_to_like_pct":   "repost_to_like_%",
        "like_to_stream_pct":   "like_to_stream_%",
        "cm_combined_audience": "audience",
        "is_official":          "released?",
        "viability_score":      "viability",
    })

    display_df["stream_count"] = display_df["stream_count"].apply(
        lambda x: f"{x/1_000_000:.1f}M" if pd.notna(x) else ""
    )
    display_df["like_count"] = display_df["like_count"].apply(
        lambda x: f"{x/1_000:.1f}K" if pd.notna(x) else ""
    )

    st.dataframe(display_df, use_container_width=True, height=600)

    # Download
    csv = filtered_df.to_csv(index_label="rank")
    st.download_button(
        label="⬇  Download CSV",
        data=csv,
        file_name=f"sifted_{query.replace(' ', '_')}.csv",
        mime="text/csv",
    )

elif search_btn and not query.strip():
    st.warning("Please enter a search query.")