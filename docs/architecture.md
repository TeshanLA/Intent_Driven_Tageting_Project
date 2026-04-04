# Architecture Overview

## Goal

Build a simple end-to-end prototype where a publisher page requests a context-aware ad recommendation using only short-lived first-party session behaviour.

## Flow

1. Frontend creates a short-lived session ID in `sessionStorage`.
2. Frontend logs lightweight article and ad interaction events.
3. Backend stores events in SQLite and updates a session summary.
4. Article pages request an ad from `POST /ad/request`.
5. Backend performs stage 1 category prediction, builds stage 2 features, ranks ads, and returns the best candidate.
6. Dashboard aggregates the logged data into transparent publisher metrics.
7. Candidate ads are loaded from `data/ads_pool.csv` and normalized into the internal ad format used by the API.

## Backend modules

- `app/main.py` startup and router registration
- `app/core/` config and database
- `app/models/` SQLAlchemy models
- `app/schemas/` request and response schemas
- `app/routers/` API endpoints
- `app/services/inference.py` model loading and inference mode
- `app/services/feature_builder.py` stage 2 feature generation
- `app/services/session_features.py` session aggregation
- `app/services/ad_selector.py` candidate ranking

## Privacy choices

- No third-party cookies
- No persistent identity
- Session-level aggregate behaviour only
- Short-lived first-party session storage
- Intended for demo targeting, not long-term profiling
