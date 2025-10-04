# Smart Stadium Dashboard

React + TypeScript single-page dashboard that visualizes the Smart Stadium backend. It surfaces live games, celebration controls, device status, event history, and a websocket-powered activity feed.

## Prerequisites

- Node.js 20+
- Smart Stadium backend running locally (defaults to `http://localhost:8000`)

## Getting started

```powershell
# Install dependencies
npm install

# Start the development server (http://localhost:5173)


# Type-check and build for production
npm run build

# Preview the production bundle locally
npm run preview
```

The app reads the backend base URL and websocket endpoint from optional env vars:

```powershell
# .env.local
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/api/ws
```

## Feature map

- **Status bar** – live uptime, environment, device summary, and websocket connection state.
- **Live games** – scoreboard for NFL or college football with red-zone callouts.
- **Manual celebrations** – trigger lighting events and record manual celebrations.
- **Smart lights** – enable/disable devices, run diagnostics, reset default scenes.
- **History** – recent celebration log with timestamps and context.
- **Live feed** – websocket stream of celebration and victory events in real time.

## Testing & linting

- `npm run lint` – ESLint across the dashboard
- `npm run build` – TypeScript build + production bundle (fails on type errors)

