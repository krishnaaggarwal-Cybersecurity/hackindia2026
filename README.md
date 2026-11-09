# Deploy AeroTwin to Vercel

This repository is pre‑configured for a one‑click Vercel deployment.

## Prerequisites
- Node.js (>= 18)
- Python 3.10+
- Git
- Vercel account (free tier works)
- A remote Git host (GitHub, GitLab, Bitbucket)

## One‑click deployment (recommended)
1. Push the repo to a remote (see instructions below).
2. Open <https://vercel.com/import> and import the repository.
3. Vercel will detect `vercel.json`, install the Python deps, run `npm install && npm run build`,
   and deploy.
4. When the build finishes you’ll receive a public URL like `https://your‑project.vercel.app`.

## Manual deployment (Vercel CLI)
```bash
npm i -g vercel           # install CLI (once)
vercel login              # authenticate
cd aerotwin                # project root
vercel --prod             # deploy
```

## Environment variables (optional)
- `AI_PROVIDER` – e.g. `openai` or `gemini`
- `AI_PROVIDER_KEY` – your API key for the chosen provider
- `TELEMETRY_INTERVAL` – controls telemetry emission speed (default 1.0)

## Local development
```bash
# Backend
uvicorn backend/app/main:app --reload

# Frontend (separate terminal)
cd frontend && npm install && npm run dev
```
