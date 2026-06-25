# Privacy-Preserving Ad Recommendation Demo

This project is a final-year-project prototype for a privacy-preserving, session-based ad recommendation system.

## Project Structure

- `frontend/` - Next.js user interface
- `backend/` - FastAPI backend API
- `ml/` - exported model files
- `data/` - demo articles and ads

## How to Start the Applications

Open 2 terminals.

### 1. Start the Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend will run at:

- `http://localhost:8000`

### 2. Start the Frontend

```powershell
cd frontend
npm install
$env:NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
npm run dev
```

Frontend will run at:

- `http://localhost:3000`

## After First-Time Setup

If dependencies are already installed, next time you only need:

### Backend

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

### Frontend

If setup for the first time need to install dependencies vianpm install

```powershell
cd frontend
$env:NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
npm run dev
```

## How to Use

1. Open `http://localhost:3000`
2. Open any article
3. The system will request and display a recommended ad
4. Open `http://localhost:3000/dashboard` to view dashboard metrics

## Notes

- Make sure the backend is started before using the frontend.
- The frontend uses port `3000` and the backend uses port `8000`.
- If the frontend does not load data, check whether the backend is running.
