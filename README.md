# AI Instagram Reels Autopilot 🚀

> **Production-grade, local-first, 24/7 autonomous Instagram Reels publishing engine powered by FastAPI, Celery, FFmpeg, and Meta Graph API.**

---

## Features

- **Official Meta Graph API (v19.0+)**: Zero scraping. Uses official Instagram Content Publishing API with 2-step containerized async publishing.
- **24/7 Autopilot Schedule**: Pre-generates and publishes vertical Reels twice daily (07:00 and 18:00 Asia/Kolkata).
- **14-Agent State Machine Pipeline**:
  - `IdeaAgent`, `ResearchAgent`, `FactCheckAgent`, `HookAgent`, `ScriptAgent`, `StoryboardAgent`
  - `MediaAgent` (Pexels 9:16 + canvas fallbacks)
  - `VoiceAgent` (Microsoft Edge-TTS zero-cost neural audio)
  - `CaptionAgent` (Word-level kinetic ASS subtitles in 65%-75% safe zone)
  - `EditorAgent` (FFmpeg 1080x1920 compositor with Ken Burns & audio ducking)
  - `QCAgent` (Strict Quality Gate >= 90/100)
  - `CaptionWriterAgent` (Instagram caption + hashtags + CTA)
  - `InstagramAgent` (Container upload, polling, publishing, permalink verification)
  - `AnalyticsAgent` (Followers, Reel plays, reach)
- **Cybernetic Frontend**: React 18 + TypeScript + Vite with Three.js 3D hero graphics (`RobotCanvas`, `CircuitStormCanvas`), live SSE activity feed, and 9:16 smartphone player.
- **AES-256 Vault**: Fernet encryption for all Meta tokens and BYOK API keys.

---

## Quickstart

### 1. Prerequisites
- Python 3.11+
- Node.js 18+
- FFmpeg installed and in PATH
- Docker & Docker Compose (optional for containerized run)

### 2. Environment Setup
```bash
cp .env.example .env
# Edit .env and configure META_APP_ID, META_APP_SECRET, etc.
```

### 3. Running with Docker Compose
```bash
docker compose up -d
```
Access:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### 4. Running Locally

#### Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

#### Frontend:
```bash
cd frontend
npm install
npm run dev
```

---

## Operational Schedule
- **Slot 1**: 07:00 AM
- **Slot 2**: 06:00 PM
- **Safe Subtitle Zone**: Centered horizontally, vertically situated between 65% - 75% height.
