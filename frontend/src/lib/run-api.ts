export type Platform = "chrome" | "firefox" | "android";

export type BBox = [number, number, number, number]; // x, y, width, height

export interface StepAction {
  type: "click" | "type" | "scroll" | string;
  target_bbox?: BBox;
  value?: string;
  selector?: string;
}

export interface StepElement {
  id?: string;
  label?: string;
  bbox: BBox;
  friction_score?: number;
  role?: string;
}

export interface Step {
  index: number;
  t?: number;
  screenshot_url: string;
  action: StepAction;
  elements?: StepElement[];
  friction_score?: number;
  note?: string;
}

export interface Finding {
  id?: string;
  title: string;
  description?: string;
  severity: "critical" | "high" | "medium" | "low" | "info" | string;
  confidence: number; // 0..1 or 0..100
  step_index?: number;
}

export type RunMessage =
  | ({ type: "step" } & { step: Step })
  | ({ type: "finding" } & { finding: Finding })
  | { type: "done"; summary?: string }
  | { type: "error"; message?: string }
  | { type: string; [key: string]: unknown };

const RAW_BASE =
  (import.meta.env["VITE_API_BASE_URL"] as string | undefined) ?? "http://localhost:8000";

export const API_BASE = RAW_BASE.replace(/\/$/, "");

export function wsUrl(runId: string) {
  const base = API_BASE.replace(/^http/, "ws");
  return `${base}/ws/run/${runId}`;
}

export interface StartRunInput {
  goal: string;
  url: string;
  platform: Platform;
}

export async function startRun(input: StartRunInput): Promise<{ run_id: string }> {
  const res = await fetch(`${API_BASE}/api/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!res.ok) {
    throw new Error(`Backend rejected the run (${res.status})`);
  }
  return (await res.json()) as { run_id: string };
}

/** Normalizes payload shapes: message may nest data under `step`, `finding`, or `data`, or be flat. */
export function normalizeStep(msg: Record<string, unknown>): Step | null {
  const raw = (msg["step"] as Record<string, unknown> | undefined) ??
              (msg["data"] as Record<string, unknown> | undefined) ??
              msg;
  if (!raw || typeof raw !== "object") return null;

  // Derive or extract index
  const index = Number(raw["index"] ?? raw["step_number"] ?? 0);

  // Derive screenshot_url: use existing screenshot_url, or build data URI from screenshot_base64
  let screenshot_url = String(raw["screenshot_url"] ?? "");
  if (!screenshot_url && raw["screenshot_base64"]) {
    screenshot_url = `data:image/png;base64,${raw["screenshot_base64"]}`;
  }
  if (!screenshot_url) return null;

  // Build normalized action
  const rawAction = (raw["action"] as Record<string, unknown> | undefined) ?? {};
  const actionType = String(rawAction["type"] ?? raw["action_type"] ?? "click");

  // Determine target_bbox: check target_bbox, or build from target_coordinates {x, y}
  let target_bbox: BBox | undefined = rawAction["target_bbox"] as BBox | undefined;
  if (!target_bbox && raw["target_coordinates"]) {
    const coords = raw["target_coordinates"] as { x?: number; y?: number };
    const cx = coords.x ?? 0;
    const cy = coords.y ?? 0;
    // synthesize a 32x32 target box centered on coordinate
    target_bbox = [Math.max(0, cx - 16), Math.max(0, cy - 16), 32, 32];
  }

  // Extract elements for friction heatmap
  const elements: StepElement[] = (raw["elements"] as StepElement[] | undefined) ?? [];

  return {
    index,
    t: Number(raw["timestamp"] ?? raw["t"] ?? Date.now()),
    screenshot_url,
    action: {
      type: actionType,
      target_bbox,
      value: String(rawAction["value"] ?? ""),
      selector: String(rawAction["selector"] ?? ""),
    },
    elements,
    friction_score: Number(raw["instant_friction"] ?? raw["friction_score"] ?? 0),
    note: String(raw["note"] ?? raw["state_classification"] ?? ""),
  };
}

export function normalizeFinding(msg: Record<string, unknown>): Finding | null {
  const raw = (msg["finding"] as Record<string, unknown> | undefined) ??
              (msg["data"] as Record<string, unknown> | undefined) ??
              msg;
  if (!raw || typeof raw !== "object") return null;

  // Map severity score or severity string
  let severity = String(raw["severity"] ?? raw["finding_type"] ?? "medium").toLowerCase();
  if (!["critical", "high", "medium", "low", "info"].includes(severity)) {
    const score = Number(raw["severity_score"] ?? 0.5);
    if (score >= 0.8) severity = "critical";
    else if (score >= 0.6) severity = "high";
    else if (score >= 0.35) severity = "medium";
    else severity = "low";
  }

  const confidence = Number(raw["confidence_score"] ?? raw["confidence"] ?? 0.85);

  return {
    id: String(raw["id"] ?? `f_${Date.now()}`),
    title: String(raw["title"] ?? "UX Friction Detected"),
    description: String(raw["explanation"] ?? raw["description"] ?? ""),
    severity,
    confidence,
    step_index: raw["step_number"] !== undefined ? Number(raw["step_number"]) : (raw["step_index"] !== undefined ? Number(raw["step_index"]) : undefined),
  };
}

export function confidencePct(confidence: number) {
  const pct = confidence <= 1 ? confidence * 100 : confidence;
  return Math.round(pct);
}

/** Maps a 0..1 friction score onto a crisp green→amber→red hue. */
export function frictionColor(score = 0) {
  const s = Math.max(0, Math.min(1, score));
  const hue = 140 - s * 140; // 140 green -> 0 red
  return `hsl(${hue.toFixed(0)} 85% 55%)`;
}
