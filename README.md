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

Expected artifact paths:

- `ml/exported_models/stage1_vectorizer.joblib`
- `ml/exported_models/stage1_model.joblib`
- `ml/exported_models/stage2_model.joblib`
- `ml/exported_models/category_mapping.json`

If those files are not present, the backend runs in `mock` mode:

- stage 1 category prediction uses simple keyword heuristics
- stage 2 ranking uses transparent heuristic scoring
- ad responses still include debug fields so the choice is explainable

Check the current mode at:

- `GET http://localhost:8000/health`

## Real ML artifact drop-in later

When real exported assets are ready, drop them into `ml/exported_models/`.

No API contract changes are required. The backend will attempt to load them at startup and switch to `real_model` mode automatically if loading succeeds.

## Main API routes

- `GET /health`
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
