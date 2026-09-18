# P8 — Autonomous Agentic Black-Box UI/UX & Accessibility Testing Framework
### Frontend Observability Console (`frontend`)

High-performance developer observatory built with React 19, Vite, TanStack Router, and Tailwind CSS. Directly connects to the Python FastAPI black-box testing engine via REST and WebSockets.

---

## Key Features

1. **Goal & Target Dispatcher**
   - Natural language goal input, black-box target URL, and platform selector (`Chrome`, `Firefox`, `Android`).
   - Quick 1-click demo presets for judging:
     - `✅ Baseline (ApexGear v1)` — Clean checkout baseline.
     - `⚠️ Injected Regression (ApexGear v2)` — Injected layout shifts, circular loops, and occluded targets.

2. **Visual Trajectory Replay Player**
   - Scrub and play through the autonomous agent's visual exploration frame by frame.
   - SVG vector cursor overlays indicating coordinate clicks, typing events, and view scrolls.
   - Dynamic perceptual friction heatmap overlay color-graded from low friction (green) to critical friction (red).

3. **Live Signal Findings Sidebar**
   - Real-time WebSocket streaming of detected friction events, loop traps, and layout drifts.
   - Interactive jump-to-step on finding selection.
   - Grounded explanations narrated strictly from model scores.

4. **Comprehensive Diagnostic Scorecard (`/report/{run_id}`)**
   - Model 4 flow regression detection breakdown (anomaly distance, backtrack delta, duration inflation).
   - FAISS failure memory speedup curve & recall metrics.
   - Root-cause cluster categorization.
   - Standard accessibility tree violation breakdown.

---

## Getting Started

### Prerequisites
- Node.js (v18+) or Bun

### Running Locally

```bash
cd frontend
npm install    # or bun install
npm run dev    # or bun dev
```

The web console will start on `http://localhost:5173` and automatically connect to the backend server running at `http://localhost:8000`.
