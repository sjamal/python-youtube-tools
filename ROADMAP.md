# Roadmap

Planned extensions to the YouTube data collection and analysis pipeline.

---

## In Progress

_Nothing currently active._

---

## Planned

### Data Collection

- [ ] **channel_stats_collector.py** — Collect subscriber count, view count, and video count for a list of channels over time. Stores snapshots to CSV for trend tracking.
- [ ] **playlist_harvester.py** — Retrieve all videos in a playlist with metadata: title, duration, view count, like count, published date. Supports pagination.
- [ ] **comment_sampler.py** — Pull a random sample of top-level comments from target videos for sentiment analysis. Strips PII before saving.

### Analysis

- [ ] **engagement_scorer.py** — Compute an engagement score per video (likes + comments normalised by views). Rank videos within a genre query and output a sorted report.
- [ ] **trend_tracker.py** — Run `survey_pipeline.py` on a schedule and diff consecutive snapshots to identify rising and falling content. Outputs a delta report.
- [ ] **regional_comparator.py** — Compare view counts and engagement scores for the same query across configured regions. Outputs a grouped bar chart per region.
- [ ] **genre_classifier.py** — Train a simple text classifier on video titles to categorise content (e.g. lo-fi, ambient, deep house) without relying on manual tags.

### Output & Reporting

- [ ] **survey_report_builder.py** — Generate a Markdown or HTML report from survey pipeline output: top videos, genre breakdown, regional summary, and engagement leaders.
- [ ] **results_to_sqlite.py** — Persist survey results to a local SQLite database for querying across multiple runs. Schema includes run timestamp as a dimension.

---

## Ideas / Backlog

- YouTube Data API quota manager: track daily quota usage and pause collection when approaching limits
- Thumbnail similarity clustering using image embeddings
- Export to Google Sheets for collaborative analysis

---

## Notes

- `API_KEY` is always sourced from an environment variable — never hardcoded.
- All data collection scripts should support a `--dry-run` flag to validate query parameters without consuming quota.
- Raw API responses should be cached locally to avoid re-fetching during development.
