"""Reporting helpers for Remix Radar TrackReport objects."""


def _num(n):
    if n is None:
        return "N/A"
    if isinstance(n, float):
        return f"{n:,.2f}"
    return f"{n:,}"


def _usd(n):
    return f"${n:,.0f}"


def format_track_report(report):
    """Render a readable single-track report."""
    lines = []
    score = report.get("opportunity_score", {})
    metrics = report.get("sc_metrics", {})
    parsed = report.get("parsed_title", {})
    revenue = report.get("revenue", {})
    viability = report.get("viability", {})

    lines.append("=" * 72)
    lines.append(f"Track: {report.get('track_title', 'N/A')}")
    lines.append(f"URL:   {report.get('sc_url', 'N/A')}")
    lines.append("-" * 72)
    lines.append(
        f"Opportunity Score: {score.get('overall', 'N/A')} / 100 [{score.get('label', 'N/A')}]"
    )
    lines.append(
        f"  Demand: {score.get('demand', 'N/A')}  Conversion: {score.get('conversion', 'N/A')}  Momentum: {score.get('momentum', 'N/A')}"
    )
    lines.append("")
    lines.append("Parsed Title")
    lines.append(f"  Original artist: {parsed.get('original_artist') or '(not detected)'}")
    lines.append(f"  Original song:   {parsed.get('original_song') or '(not detected)'}")
    lines.append(f"  Remix artist:    {parsed.get('remix_artist') or '(not detected)'}")
    lines.append("")
    lines.append("SoundCloud Metrics")
    lines.append(f"  Plays:            {_num(metrics.get('plays'))}")
    lines.append(f"  Likes:            {_num(metrics.get('likes'))}")
    lines.append(f"  Reposts:          {_num(metrics.get('reposts'))}")
    lines.append(f"  Comments:         {_num(metrics.get('comments'))}")
    lines.append(f"  Engagement rate:  {metrics.get('engagement_rate', 0):.2%}")
    lines.append(f"  Daily velocity:   {_num(metrics.get('daily_velocity'))} plays/day")
    lines.append("")

    if revenue:
        lines.append("Revenue Projection")
        for tier, data in revenue.get("projections", {}).items():
            lines.append(
                f"  {tier:<12} streams={_num(data.get('estimated_streams')):>10}  all_dsps={_usd(data.get('revenue', {}).get('all_dsps_avg', 0))}"
            )
        lines.append(f"  Recommendation: {viability.get('recommendation', 'N/A')}")
    return "\n".join(lines)


def format_summary_table(reports):
    """Render ranked summary for multiple tracks."""
    header = (
        f"{'Rank':<5} {'Score':<8} {'Label':<10} {'Plays':>12} {'DailyVel':>10}  Title"
    )
    rows = [header, "-" * len(header)]
    for idx, report in enumerate(reports, start=1):
        score = report.get("opportunity_score", {})
        metrics = report.get("sc_metrics", {})
        rows.append(
            f"{idx:<5} {score.get('overall', 0):<8} {score.get('label', 'N/A'):<10} "
            f"{_num(metrics.get('plays')):>12} {_num(metrics.get('daily_velocity')):>10}  "
            f"{report.get('track_title', 'N/A')}"
        )
    return "\n".join(rows)
