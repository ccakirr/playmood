# PlayMood

PlayMood is a full‑stack AI playlist generator. It takes a short prompt (mood, artists, era) and returns a curated playlist in JSON.

## Tech Stack

- Frontend: React + Vite + Tailwind CSS + DaisyUI
- Backend: FastAPI
- AI: Hugging Face Inference (via OpenAI-compatible client)

## Project Structure

- frontend/ — React UI
- backend/ — FastAPI API

## Prerequisites

- Node.js 18+
- Python 3.11+

## Environment Variables

Backend (`backend/.env`):

- HG_TOKEN=your_huggingface_token

Frontend (`frontend/.env`):

- VITE_API_URL=http://localhost:8000

## Local Development

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the app at http://localhost:5173

## API

- POST /playlist/generate

Request:

```json
{ "prompt": "dark late-night R&B like The Weeknd" }
```

Response:

```json
{
  "playlist_name": "Night Drive",
  "tracks": [{ "artist": "The Weeknd", "title": "After Hours" }]
}
```

## Notes

- If the AI returns invalid JSON or non‑music prompts, the API responds with a clear error message that is shown in the UI.
