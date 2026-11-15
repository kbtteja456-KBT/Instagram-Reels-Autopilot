# 🚀 Deploying Instagram Reels Autopilot to Render.com

This guide provides the complete walkthrough to deploy your **AI Instagram Reels Autopilot** to **Render.com** in under 5 minutes.

---

## 🏗️ Architecture Overview on Render

Render will host the entire system autonomously:

1. **Backend Web Service (`instagram-autopilot-backend`)**:
   - Containerized Docker runtime with **Python 3.11**, **FFmpeg**, and system fonts.
   - Runs FastAPI on a public HTTPS domain.
   - Built-in **24/7 Autonomous Slot Scheduler** (`ENABLE_INTERNAL_SCHEDULER=true`) that generates and publishes Reels at **07:00 & 18:00 (Asia/Kolkata)** without needing your PC on.
   - Auto-detects its own public URL (`RENDER_EXTERNAL_URL`) so Instagram Graph API can download your rendered MP4 reels.

2. **Frontend Dashboard (`instagram-autopilot-frontend`)**:
   - Hosted as a **100% Free Static Site** on Render's global CDN.
   - Automatically connected to your Render backend API.
   - Full 3D Cybernetic dashboard, live Server-Sent Events (SSE) feed, and 9:16 video player.

3. **Database (MongoDB Atlas)**:
   - Already configured in cloud via MongoDB Atlas (`mongodb+srv://...`).

---

## 📋 Step-by-Step Deployment Instructions

### Step 1: Push your latest code to GitHub

Make sure all changes are committed and pushed to your GitHub repository:
```bash
git add .
git commit -m "Configure Render Blueprint and cloud-ready endpoints"
git push origin main
```

---

### Step 2: Open Render.com & Create New Blueprint

1. Go to [dashboard.render.com](https://dashboard.render.com).
2. Click **New +** in the top right and select **Blueprint**.
3. Connect your GitHub repository (`kbtteja456-KBT/Instagram-Reels-Autopilot` or your repo name).
4. Render will automatically detect the [`render.yaml`](./render.yaml) file in the root.

---

### Step 3: Fill in Secret Environment Variables

Render will prompt you for the secret environment variables defined in `render.yaml`. Copy these from your local [`.env`](./.env) file:

| Variable | Description / Value |
|---|---|
| `MONGODB_URI` | Your MongoDB Atlas connection string (`mongodb+srv://...`) |
| `META_APP_ID` | Your Meta Developer App ID |
| `META_APP_SECRET` | Your Meta App Secret |
| `INSTAGRAM_ACCOUNT_ID` | Your Instagram Business / Creator Account ID |
| `INSTAGRAM_ACCESS_TOKEN` | Your 60-day or System User Long-Lived Token |
| `ENCRYPTION_KEY` | Your AES-256 Fernet key (from `.env`) |
| `JWT_SECRET` | Your JWT secret key (from `.env`) |
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `PEXELS_API_KEY` | Your Pexels API key (for stock video footage) |
| `PIXABAY_API_KEY` | (Optional) Pixabay API key |

> **Note**: The following non-secret settings are already pre-configured in `render.yaml`:
> - `ENABLE_INTERNAL_SCHEDULER`: `true`
> - `TIMEZONE`: `Asia/Kolkata`
> - `SLOT1_TIME`: `07:00`
> - `SLOT2_TIME`: `18:00`
> - `DAILY_REEL_LIMIT`: `2`
> - `ZERO_COST_MODE`: `true`
> - `OPENROUTER_MODEL`: `nvidia/nemotron-3.5-lightning:free`

---

### Step 4: Click "Apply"

1. Click **Apply Blueprint**.
2. Render will build both services:
   - **Backend**: Pulls Docker container, installs FFmpeg, starts FastAPI backend and autonomous scheduler.
   - **Frontend**: Compiles React + Vite + Three.js and deploys to the global CDN.
3. Once finished, you will receive two public URLs:
   - Frontend URL: `https://instagram-autopilot-frontend.onrender.com`
   - Backend URL: `https://instagram-autopilot-backend.onrender.com`

---

### Step 5: Verification & Testing

1. Open your **Frontend URL** in your browser.
2. Verify that:
   - System status shows **HEALTHY**.
   - Database shows **CONNECTED**.
   - The Activity Feed connects via SSE without errors.
3. Test a generation:
   - Click **Generate Reel** to test the entire 14-agent AI pipeline in the cloud.
   - You can watch the real-time progress in the Activity Feed and preview the generated video in the 9:16 player.
4. Your cloud server is now running 24/7 on autopilot! Even when your local PC is turned off, reels will automatically generate and publish at **07:00** and **18:00**.
