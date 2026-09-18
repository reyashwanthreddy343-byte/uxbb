# P8 — Autonomous Agentic Black-Box UI/UX & Accessibility Testing Framework
## Scope Boundary & Architectural Lock (v1)

This document locks the scope boundaries for v1 of the P8 testing engine to prevent scope creep or re-litigation during hackathon development.

### 1. In Scope for v1
- **True Black-Box Perception & Action**: Coordinate-based clicking, typing, and scrolling without selector/DOM injection.
- **Model 1 (Element Detector)**: YOLOv8-nano UI bounding-box detection (RICO dataset format).
- **Model 2 (Visual Drift / Siamese)**: Image feature extraction & contrastive classifier for functional UI state drift.
- **Model 3 (Friction & Sequence Scorer)**: Sequence representation over trajectory steps with dual heads (Friction regression + Backtrack classifier + Severity/Confidence).
- **Model 4 (Anomaly & Regression Detector)**: FAISS-backed trajectory vector distance against baseline runs + Isolation Forest tabular features.
- **Stand-out Features**:
  1. Failure Memory Engine (FAISS index for trajectory recall & self-improving speed curve).
  2. Root-Cause Clustering (HDBSCAN / Agglomerative clustering of findings).
  3. Grounded NL explanations & calibrated severity/confidence scores.
- **Strictly Limited LLM Role**:
  - LLM call site 1: `resolve_tie(candidates, goal) -> int` (only when Model 1/3 confidences are within 0.05).
  - LLM call site 2: `explain_finding(finding_data) -> str` (strictly narrating real model outputs).

### 2. Out of Scope for v1 (Deliberate Deferrals — Not Oversights)
- **Backend/API/Database Testing**: This system evaluates rendered frontend UX & accessibility only.
- **Time/Space Code Complexity Analysis**: Requires static code instrumentation, which violates the zero-instrumentation black-box rule.
- **Persona-Conditioned Exploration**: Deferred to v2 to focus all execution bandwidth on the 4-model core.
- **Cross-Platform Multi-Browser Consistency Engine**: Deferred to v2 to keep browser execution harness focused and reliable.
