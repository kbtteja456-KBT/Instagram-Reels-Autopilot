# AI Instagram Reels Autopilot — Architecture & Technical Specification

## 1. System Overview

**AI Instagram Reels Autopilot** is a fully automated, local-first, zero-cost-by-default video publishing engine designed to run 24/7 on a workstation or cloud container. It creates and publishes two original, high-retention 1080x1920 vertical Reels daily (07:00 and 18:00 Asia/Kolkata), pre-generating them in designated overnight and midday windows.

The system uses **only official Meta Graph APIs & Instagram Content Publishing APIs (v19.0+)**, strictly prohibiting web scraping or unofficial endpoints.

```
                                  +-----------------------+
                                  |   React + TS Frontend |
                                  |   (Port 3000 / Vite)  |
                                  +-----------+-----------+
                                              | HTTP / SSE
                                              v
+-----------------------------------------------------------------------------------------+
|                               FASTAPI BACKEND (Port 8000)                               |
|                                                                                         |
|  - REST API (/api/videos, /api/autopilot, /api/auth/instagram, /api/media, /api/vault)  |
|  - Meta Graph API OAuth 2.0 Flow & AES-256 Encrypted Long-Lived Token Storage           |
|  - Real-Time Event Stream (Server-Sent Events /api/activity/stream)                     |
|  - Public Media Server (/api/media/download/{file}) for Meta Container Ingestion        |
|  - System Resource Guard (CPU, RAM, Disk safeguard)                                     |
+-----------------------------+-----------------------------------+-----------------------+
                              |                                   |
                              v                                   v
                   +---------------------+             +--------------------+
                   |   REDIS (Port 6379) |             |  MONGODB (27017)   |
                   |   Broker & Locks    |             |  State & Metadata  |
                   +----------+----------+             +---------+----------+
                                                 |
                                                 v
+-----------------------------------------------------------------------------------------+
|                              CELERY WORKER & LOCAL SCHEDULER                            |
|                                                                                         |
|  Operational Schedule: 07:00 & 18:00 (Asia/Kolkata)                                     |
|                                                                                         |
|  Full 14-Agent State Machine Pipeline:                                                  |
|    IDEA -> RESEARCH -> FACT CHECK -> HOOK -> SCRIPT -> STORYBOARD ->                    |
|    MEDIA COLLECTION (9:16) -> VOICE (Edge-TTS) -> CAPTIONS (ASS/Whisper) ->             |
|    EDITING (FFmpeg 1080x1920) -> QUALITY CONTROL (>=90) -> CAPTION WRITER ->            |
|    INSTAGRAM PUBLISH (2-Step Container Flow) -> ANALYTICS                               |
+-----------------------------------------------------------------------------------------+
```

## 2. Meta Graph API & Instagram Content Publishing Specification

### A. Authentication & Permissions
The system connects to an Instagram Creator or Business account linked to a Facebook Page via official Meta OAuth 2.0:
- Dialog: `https://www.facebook.com/v19.0/dialog/oauth`
- Scopes:
  - `instagram_basic`: Profile and media access
  - `instagram_content_publish`: Publishing Reels and posts
  - `instagram_manage_insights`: Fetching reel views, plays, interactions
  - `pages_show_list`: Discovering linked Facebook Pages
  - `pages_read_engagement`: Page engagement inspection
  - `business_management`: Account structure resolution
- Token Exchange:
  1. Code -> Short-lived user token (expires in 1-2 hours)
  2. Short-lived -> 60-day Long-Lived User Access Token via `grant_type=fb_exchange_token`
  3. Tokens are encrypted at rest with AES-256 (Fernet)

### B. 2-Step Asynchronous Reels Publishing Pipeline
1. **Container Creation**:
   - `POST https://graph.facebook.com/v19.0/{ig_user_id}/media`
   - Parameters:
     - `media_type`: `REELS`
     - `video_url`: `{PUBLIC_MEDIA_BASE_URL}/api/media/download/{filename}`
     - `caption`: Formatted text with high-retention hook, value summary, and viral hashtags
     - `share_to_feed`: `true`
     - `cover_url`: Optional thumbnail frame
   - Output: `{ "id": "{creation_id}" }`
2. **Container Status Polling**:
   - `GET https://graph.facebook.com/v19.0/{creation_id}?fields=status_code`
   - Polled every 5 seconds (timeout 180s):
     - `FINISHED`: Video transcoded and ready for publish
     - `IN_PROGRESS`: Transcoding
     - `ERROR` / `EXPIRED`: Terminate with diagnostics
3. **Container Publication**:
   - `POST https://graph.facebook.com/v19.0/{ig_user_id}/media_publish`
   - Parameters: `creation_id={creation_id}`
   - Output: `{ "id": "{media_id}" }`
4. **Verification & Permalink**:
   - `GET https://graph.facebook.com/v19.0/{media_id}?fields=id,permalink,timestamp`
   - Yields live permalink (e.g., `https://www.instagram.com/reel/C12345/`)

## 3. Strict Quality Control Gate (QC >= 90/100)

Every rendered video must pass the automated QC Gate before upload:
- **Resolution**: Exactly 1080x1920 (9:16 vertical orientation).
- **Frame Rate**: Exactly 30 fps (or 60 fps).
- **Pacing**: Scene cuts every 2.5 to 3.5 seconds to sustain attention.
- **Audio Ducking**: Voiceover normalized to -18 dB LUFS, background music ducked to -26 dB.
- **Subtitle Safe Zone**: Word-level kinetic ASS subtitles strictly placed at 65%-75% screen height to avoid Instagram UI overlays (top header, bottom caption/audio, right action rail).

## 4. Multi-Tenant Workspace & Security

- **Encryption**: AES-256 Fernet encryption for all Meta access tokens and user API keys stored in MongoDB.
- **CSRF Protection**: HMAC-SHA256 signed `state` parameter bound to `{workspace_id}:{user_id}:{timestamp}:{signature}`.
- **Password Hashing**: PBKDF2 with SHA-256 / bcrypt.
- **JWT Authentication**: Bearer tokens with configurable expiration.
