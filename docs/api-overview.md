# API Overview

- `GET /health`
- `GET /debug/inference/status`
- `POST /debug/inference/inspect`
- `GET /articles`
- `GET /articles/{slug}`
- `POST /events`
- `POST /ad/request`
- `POST /ad/click`
- `GET /dashboard/summary`

## ML integration and debug routes

### `GET /health`

Returns:

- overall API status
- resolved inference mode
- load status for `stage1_vectorizer`, `stage1_model`, `stage2_model`, and `category_mapping`
- load status for the ads inventory CSV

### `GET /debug/inference/status`

Returns:

- model directory
- stage 2 feature column order
- artifact load status
- ads inventory load status

### `POST /debug/inference/inspect`

Runs the full inference pipeline without logging an impression.

Example payload:

```json
{
  "session_id": "debug-session-001",
  "article_slug": "market-rally-energy-stocks",
  "article_title": "Energy Stocks Lead Broad Market Rally",
  "article_category": "Business",
  "article_text": "Trading desks reported steady buying pressure through the afternoon..."
}
```

The response includes:

- preprocessed article summary
- stage 1 category output
- session feature snapshot
- top candidate ads with feature vectors and scores
- selected ad and ranking mode

## Example event payload

```json
{
  "session_id": "demo-session-123",
  "event_type": "page_view",
  "article_slug": "market-rally-energy-stocks",
  "article_category": "Business",
  "metadata": {
    "scroll_depth_ratio": 0.5,
    "dwell_time_seconds": 18
  }
}
```
