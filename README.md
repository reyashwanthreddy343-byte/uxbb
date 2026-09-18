# P8 Autonomous Agentic Black-Box UI/UX & Accessibility Testing Framework

## Overview
Autonomous, human-like agent navigation for friction mapping, flow regression detection, multi-path discovery, and accessibility auditing using specialized trained vision and sequence models.

## API Contracts for Frontend Team

### REST Endpoints
- `POST /api/runs`
  - Body: `{"goal": string, "target_url": string, "platform": "chrome"|"firefox"|"android"}`
  - Response: `{"run_id": string}`
- `GET /api/runs/{run_id}`
  - Response: `{ "run_id": string, "status": string, "goal": string, "steps": [...], "findings": [...], "regression": {...}, "failure_memory": {...} }`
- `GET /api/benchmarks`
  - Response: `{"model1_map50": float, "model2_auc": float, "model3_spearman": float, "model4_regression_detection_rate": float}`
- `GET /api/targets`
  - Preset test target apps (including the built-in mock regression e-commerce app).
- `GET /api/memory/stats`
  - Failure Memory indexed runs, speed improvement curves, and recall statistics.

### WebSocket Stream
- `WS /ws/runs/{run_id}`
  - Emits real-time messages:
    - `{"type": "step", "data": { ... }}`
    - `{"type": "finding", "data": { ... }}`
    - `{"type": "done", "data": { "run_id": string }}`

## Out of Scope for v1
- Persona-conditioned exploration and cross-platform consistency scoring are deliberately deferred to prioritize the 4-model core, Failure Memory, and live regression detection demo.
