# Build a Next

Build a Next.js (TypeScript) + Tailwind CSS + shadcn/ui page for an AI UX-testing tool.

Use .tsx components throughout, no vanilla JS files. This is the "Run" page — the primary

demo screen. This page talks ONLY to a Python/FastAPI backend over plain REST + WebSocket

JSON (given below) — don't assume any server-side Python code runs inside this Next.js

project, just fetch()/WebSocket() calls against the URLs below.




FEATURES:

1. A goal input form: natural-language goal textbox, target URL field, platform selector

   (Chrome/Firefox/Android). Submitting POSTs to /api/run and receives { run_id }.

2. On submit, open a WebSocket to ws://.../ws/run/{run_id}. As "step" messages arrive,

   push each into a live-updating trajectory.

3. VISUAL TRAJECTORY REPLAY: a video-scrubber-style player showing the sequence of

   screenshots (step.screenshot_url) with an animated cursor dot that moves to

   step.action.target_bbox and shows a click/type/scroll indicator at each step. Play,

   pause, scrub, and step-forward/back controls, like a screen-recording player.

4. DETECTION & FRICTION HEATMAP: overlay step.elements as bounding boxes on the current

   screenshot frame, color-graded from green (low step.friction_score) to red (high). A

   toggle to show/hide this overlay layer independent of playback.

5. A live sidebar log listing each "finding" WebSocket message as it arrives, with

   severity badge and confidence %, updating in real time during the run.

6. When a "done" message arrives, show a "View Full Report →" button linking to

   /report/{run_id}.




Design: dark-mode-first, monospace accents for technical numbers, feels like a

professional dev-tools / observability dashboard (think Playwright Trace Viewer or

Sentry), not a consumer app. Make bounding box overlays crisp SVG, not blurry CSS boxes.

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/7a13f5e0-410e-4a97-b3f8-27e345ef9c99).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
