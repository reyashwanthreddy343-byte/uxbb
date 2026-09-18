import { useEffect, useMemo, useRef, useState } from "react";
import {
  Boxes,
  ChevronLeft,
  ChevronRight,
  MousePointerClick,
  Pause,
  Play,
  Keyboard,
  MoveVertical,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { frictionColor, type BBox, type Step } from "@/lib/run-api";

const FRAME_MS = 1400;
const FALLBACK_SIZE = { width: 1280, height: 800 };

function bboxCenter(bbox: BBox) {
  return { x: bbox[0] + bbox[2] / 2, y: bbox[1] + bbox[3] / 2 };
}

function ActionIcon({ type }: { type: string }) {
  if (type === "type") return <Keyboard className="size-3.5" />;
  if (type === "scroll") return <MoveVertical className="size-3.5" />;
  return <MousePointerClick className="size-3.5" />;
}

interface TrajectoryPlayerProps {
  steps: Step[];
  index: number;
  onIndexChange: (index: number) => void;
  follow: boolean;
  onFollowChange: (follow: boolean) => void;
}

export function TrajectoryPlayer({
  steps,
  index,
  onIndexChange,
  follow,
  onFollowChange,
}: TrajectoryPlayerProps) {
  const [playing, setPlaying] = useState(false);
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [frame, setFrame] = useState(FALLBACK_SIZE);
  const sizeCache = useRef(new Map<string, { width: number; height: number }>());

  const step = steps[index];
  const last = Math.max(0, steps.length - 1);

  useEffect(() => {
    if (!playing || steps.length === 0) return;
    const id = window.setInterval(() => {
      onIndexChange(index >= last ? 0 : index + 1);
    }, FRAME_MS);
    return () => window.clearInterval(id);
  }, [playing, index, last, steps.length, onIndexChange]);

  useEffect(() => {
    if (!step) return;
    const cached = sizeCache.current.get(step.screenshot_url);
    if (cached) setFrame(cached);
  }, [step]);

  const cursor = useMemo(() => {
    const bbox = step?.action?.target_bbox;
    if (!bbox) return null;
    return bboxCenter(bbox);
  }, [step]);

  const goto = (next: number) => {
    setPlaying(false);
    onFollowChange(false);
    onIndexChange(Math.max(0, Math.min(last, next)));
  };

  return (
    <section className="glass-panel flex min-h-[520px] flex-col overflow-hidden rounded-lg border border-background/90">
      <header className="flex min-h-14 flex-wrap items-center gap-3 border-b border-border px-4 py-2.5">
        <div className="flex items-center gap-2">
          <Boxes className="size-4 text-primary" />
          <h2 className="text-xs font-semibold uppercase">Trajectory replay</h2>
        </div>
        <span className="num text-xs text-muted-foreground">
          step {steps.length ? index + 1 : 0}/{steps.length}
        </span>
        <div className="ml-auto flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Switch id="heatmap" checked={showHeatmap} onCheckedChange={setShowHeatmap} />
            <Label htmlFor="heatmap" className="text-xs text-muted-foreground">
              Friction heatmap
            </Label>
          </div>
          <div className="flex items-center gap-2">
            <Switch id="follow" checked={follow} onCheckedChange={onFollowChange} />
            <Label htmlFor="follow" className="text-xs text-muted-foreground">
              Follow live
            </Label>
          </div>
        </div>
      </header>

      <div className="trace-grid relative flex min-h-[320px] flex-1 items-center justify-center overflow-hidden bg-background/55 p-4">
        <div className="scan-sweep pointer-events-none absolute inset-x-0 top-0 z-10 h-px bg-primary/45 shadow-[0_0_18px_var(--primary)]" />
        {step ? (
          <div
            className="float-in relative max-h-full w-full max-w-4xl overflow-hidden rounded-md border border-border-strong shadow-[0_24px_60px_-32px_color-mix(in_oklab,var(--foreground)_34%,transparent)]"
            style={{ aspectRatio: `${frame.width} / ${frame.height}` }}
          >
            <img
              key={step.screenshot_url}
              src={step.screenshot_url}
              alt={`Step ${step.index} screenshot`}
              className="absolute inset-0 size-full object-contain"
              onLoad={(e) => {
                const img = e.currentTarget;
                if (img.naturalWidth && img.naturalHeight) {
                  const size = { width: img.naturalWidth, height: img.naturalHeight };
                  sizeCache.current.set(step.screenshot_url, size);
                  setFrame(size);
                }
              }}
            />

            <svg
              viewBox={`0 0 ${frame.width} ${frame.height}`}
              preserveAspectRatio="none"
              className="absolute inset-0 size-full"
              shapeRendering="crispEdges"
            >
              {showHeatmap &&
                (step.elements ?? []).map((el, i) => {
                  const color = frictionColor(el.friction_score ?? step.friction_score ?? 0);
                  return (
                    <g key={el.id ?? i}>
                      <rect
                        x={el.bbox[0]}
                        y={el.bbox[1]}
                        width={el.bbox[2]}
                        height={el.bbox[3]}
                        fill={color}
                        fillOpacity={0.14}
                        stroke={color}
                        strokeWidth={2}
                      />
                      {el.label && (
                        <text
                          x={el.bbox[0] + 4}
                          y={Math.max(12, el.bbox[1] - 5)}
                          fill={color}
                          fontSize={Math.max(11, frame.width / 110)}
                          fontFamily="ui-monospace, monospace"
                        >
                          {el.label}
                          {el.friction_score !== undefined
                            ? ` ${el.friction_score.toFixed(2)}`
                            : ""}
                        </text>
                      )}
                    </g>
                  );
                })}

              {step.action?.target_bbox && (
                <rect
                  x={step.action.target_bbox[0]}
                  y={step.action.target_bbox[1]}
                  width={step.action.target_bbox[2]}
                  height={step.action.target_bbox[3]}
                  fill="none"
                  stroke="var(--primary)"
                  strokeWidth={3}
                  strokeDasharray="8 6"
                />
              )}

              {cursor && (
                <g
                  style={{
                    transform: `translate(${cursor.x}px, ${cursor.y}px)`,
                    transition: "transform 600ms cubic-bezier(0.22,1,0.36,1)",
                  }}
                >
                  <circle
                    className="cursor-pulse"
                    r={Math.max(18, frame.width / 60)}
                    fill="var(--primary)"
                    style={{ transformOrigin: "center" }}
                  />
                  <circle r={7} fill="var(--primary)" stroke="var(--primary-foreground)" strokeWidth={2} />
                </g>
              )}
            </svg>

            <div className="absolute left-2 top-2 flex items-center gap-2 border border-border-strong bg-background/85 px-2 py-1 backdrop-blur">
              <ActionIcon type={step.action?.type ?? "click"} />
              <span className="num text-[11px] uppercase tracking-wider text-foreground">
                {step.action?.type ?? "click"}
              </span>
              {step.action?.value && (
                <span className="num max-w-[220px] truncate text-[11px] text-muted-foreground">
                  "{step.action.value}"
                </span>
              )}
            </div>
          </div>
        ) : (
          <div className="relative text-center">
            <div className="mx-auto mb-5 grid size-20 place-items-center rounded-full border border-primary/20 bg-coral-soft/55">
              <div className="grid size-11 place-items-center rounded-full border border-primary/35 bg-background shadow-lg shadow-primary/10"><Play className="size-4 text-primary" /></div>
            </div>
            <p className="font-display text-2xl text-foreground">The canvas is listening.</p>
            <p className="mt-1 text-xs text-muted-foreground">Frames, cursor paths, and friction signals will surface here.</p>
          </div>
        )}
      </div>

      <div className="flex items-center gap-4 border-t border-border bg-background/45 px-4 py-3">
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => goto(index - 1)}
            disabled={!steps.length || index === 0}
          >
            <ChevronLeft className="size-4" />
          </Button>
          <Button
            variant="secondary"
            size="icon"
            onClick={() => {
              onFollowChange(false);
              setPlaying((p) => !p);
            }}
            disabled={steps.length < 2}
          >
            {playing ? <Pause className="size-4" /> : <Play className="size-4" />}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => goto(index + 1)}
            disabled={!steps.length || index >= last}
          >
            <ChevronRight className="size-4" />
          </Button>
        </div>

        <Slider
          value={[index]}
          min={0}
          max={last}
          step={1}
          disabled={steps.length < 2}
          onValueChange={([v]) => goto(v ?? 0)}
          className="flex-1"
        />

        <span className="num w-20 text-right text-xs text-muted-foreground">
          {step?.t !== undefined ? `${step.t.toFixed(1)}s` : `${(index * 1.4).toFixed(1)}s`}
        </span>
      </div>
    </section>
  );
}
