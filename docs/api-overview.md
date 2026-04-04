# API Overview

- `GET /health`
- `GET /articles`
- `GET /articles/{slug}`
- `POST /events`
- `POST /ad/request`
- `POST /ad/click`
- `GET /dashboard/summary`

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
