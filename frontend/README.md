# Alpha Arena Frontend

Modern Next.js dashboard for visualising the AI Trading Agent benchmark. It
mimics the Alpha Arena Season 1 chart experience with multi-agent equity curves,
USD / percentage toggles, and a live countdown to Season 1.5.

## 🚀 Getting Started

```bash
npm install

# optional – set the FastAPI API base (defaults to http://localhost:8000)
export API_BASE_URL="http://localhost:8000"

npm run dev
```

Open http://localhost:3000 to view the dashboard. The page auto-refreshes via
client state for the countdown ticker.

## 🔌 Data Source

- Tries to read `GET /api/portfolio/multi-asset-performance` from the FastAPI
  backend.
- If the request fails or returns an empty payload, the UI falls back to a
  bundled mock dataset that reflects the Season 1 chart.
- Configure the API endpoint with either `API_BASE_URL` or
  `NEXT_PUBLIC_API_BASE_URL` environment variables.

## 🧩 Key Components

- `src/components/dashboard.tsx` – client component with chart controls,
  responsive Recharts line chart, and the countdown card.
- `src/lib/mockData.ts` – sample data used as a graceful fallback.
- `src/app/page.tsx` – server component that loads API data and hydrates the
  dashboard.

## 📊 Features

- Toggle between absolute account value (`$`) and relative performance (`%`).
- Switch timeframe between full season and rolling 72-hour view.
- Color-coded legend with live values for each agent/series.
- Countdown panel with copy mirroring the Alpha Arena Season 1.5 teaser.

## 🛠️ Tech Stack

- Next.js 16 App Router with React 19 and the React Compiler
- Tailwind CSS v4 for styling
- Recharts for responsive SVG charting
- TypeScript for type-safe data handling

## ✅ Linting & Builds

```bash
npm run lint
npm run build
```

The build is static-friendly; all dynamic data is fetched at request time with a
mock fallback.
