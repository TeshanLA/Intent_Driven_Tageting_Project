# Privacy-Preserving Ad Recommendation Demo

This monorepo contains a final-year-project prototype for a privacy-preserving, session-based ad recommendation system.

## Structure

- `frontend/` Next.js publisher site and dashboard
- `backend/` FastAPI API, SQLite storage, event logging, and ranking logic
- `ml/` exported model drop-in folder and training notebook placeholder
- `data/` demo article and ad inventory data
- `shared/` shared examples
- `docs/` architecture and checklist notes

## What works

- Demo homepage with seeded articles across multiple categories
- Article detail page with an inline sponsored ad slot
- Short-lived first-party session ID in `sessionStorage`
- Tracking for page views, scroll milestones, engagement, ad impressions, and ad clicks
- FastAPI backend with SQLite event logging
- Session summary aggregation for privacy-preserving targeting
- Ad recommendation flow with real-model hooks and mock fallback mode
- Publisher dashboard powered by logged event data

## Exact local run steps

These commands are written for PowerShell on Windows.

### 1. Start the backend

Open terminal 1:

```powershell
cd c:\Users\ULAKRTE\Documents\FYP\Intent_driven_Targeting_Project\Intent_Driven_Tageting_Project\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend URLs:

- API: `http://localhost:8000`
- Health check: `http://localhost:8000/health`

### 2. Start the frontend

Open terminal 2:

```powershell
cd c:\Users\ULAKRTE\Documents\FYP\Intent_driven_Targeting_Project\Intent_Driven_Tageting_Project\frontend
npm install
$env:NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
npm run dev
```

Frontend URL:

- App: `http://localhost:3000`

### 3. Use the system

1. Open `http://localhost:3000`
2. Open an article
3. The article page will request an ad from the backend
4. The ad impression is logged when the ad renders
5. Clicking the ad logs an ad click event
6. Scroll and spend a few seconds on the article page
7. Open `http://localhost:3000/dashboard` to see updated metrics

## Minimal startup commands after first install

Once dependencies are already installed, the exact commands are:

### Backend

```powershell
cd c:\Users\ULAKRTE\Documents\FYP\Intent_driven_Targeting_Project\Intent_Driven_Tageting_Project\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

### Frontend

```powershell
cd c:\Users\ULAKRTE\Documents\FYP\Intent_driven_Targeting_Project\Intent_Driven_Tageting_Project\frontend
$env:NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
npm run dev
```

## Mock mode vs real model mode

The backend starts even if ML artifacts are missing.

Expected exported files and exact placement:

- `ml/exported_models/stage1_vectorizer.joblib`
- `ml/exported_models/stage1_model.joblib`
- `ml/exported_models/stage2_model.joblib`
- `ml/exported_models/category_mapping.json`
- `data/ads_pool.csv`

### Artifact responsibilities

- `stage1_vectorizer.joblib`
  Converts preprocessed article text into the feature representation expected by the stage 1 classifier.
- `stage1_model.joblib`
  Predicts the article category from the vectorized article text.
- `stage2_model.joblib`
  Scores candidate ads from the explicit stage 2 feature vector built in the backend.
- `category_mapping.json`
  Maps raw stage 1 model outputs to readable category names used by the app.
- `ads_pool.csv`
  Supplies the candidate ads that stage 2 ranks.

If those files are not present, the backend runs in `mock` mode:

- stage 1 category prediction uses simple keyword heuristics
- stage 2 ranking uses transparent heuristic scoring
- ad inventory falls back to a built-in generic ad if the CSV is missing or invalid
- ad responses still include debug fields so the choice is explainable

Check the current mode at:

- `GET http://localhost:8000/health`
- `GET http://localhost:8000/debug/inference/status`

## Real ML artifact drop-in later

When real exported assets are ready, drop them into `ml/exported_models/`.

No API contract changes are required. The backend will attempt to load them at startup and switch to `real_model` mode automatically if loading succeeds.

## Inference pipeline

The backend recommendation flow is intentionally explicit:

1. preprocess article text
2. run stage 1 category prediction
3. build stage 2 candidate ad features
4. run stage 2 model scoring if available
5. fallback to heuristic reranking if stage 2 is unavailable or errors

The stage 2 feature contract is defined in:

- [feature_builder.py](c:\Users\ULAKRTE\Documents\FYP\Intent_driven_Targeting_Project\Intent_Driven_Tageting_Project\backend\app\services\feature_builder.py)
- [inference.py](c:\Users\ULAKRTE\Documents\FYP\Intent_driven_Targeting_Project\Intent_Driven_Tageting_Project\backend\app\services\inference.py)

Feature order is kept explicit so it can be matched with notebook training/export logic:

- `stage1_confidence`
- `category_match`
- `text_similarity`
- `behaviour_score`
- `session_page_count`
- `same_category_views`
- `dwell_time_seconds`
- `scroll_depth_ratio`
- `engagement_score`
- `ad_type_targeted`

## Debugging model integration

Useful endpoints while integrating exported artifacts:

- `GET /health`
  Shows overall mode plus artifact and ad inventory load status.
- `GET /debug/inference/status`
  Shows model paths, load status, and the exact stage 2 feature order.
- `POST /debug/inference/inspect`
  Runs the inference pipeline without logging an impression and returns stage 1 output, session features, candidate scores, and the selected ad.

## Main API routes

- `GET /health`
- `GET /debug/inference/status`
- `POST /debug/inference/inspect`
- `GET /articles`
- `GET /articles/{slug}`
- `POST /events`
- `POST /ad/request`
- `POST /ad/click`
- `GET /dashboard/summary`

## Notes

- This is intentionally prototype-scoped, not production ad-tech infrastructure.
- Tracking is first-party and session-level only.
- Dashboard metrics are derived from logged event rows in SQLite.
- If a dev server leaves port `3000` busy, stop the old `node` process before restarting the frontend.

See [architecture](c:\Users\ULAKRTE\Documents\FYP\Intent_driven_Targeting_Project\Intent_Driven_Tageting_Project\docs\architecture.md), [API overview](c:\Users\ULAKRTE\Documents\FYP\Intent_driven_Targeting_Project\Intent_Driven_Tageting_Project\docs\api-overview.md), and [task checklist](c:\Users\ULAKRTE\Documents\FYP\Intent_driven_Targeting_Project\Intent_Driven_Tageting_Project\docs\task-checklist.md) for supporting project notes.
