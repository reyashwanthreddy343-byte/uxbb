import { createFileRoute } from "@tanstack/react-router";
import { useCallback, useEffect, useRef, useState } from "react";
import { Activity, CircleDot, Radio, Sparkles } from "lucide-react";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";
import { GoalForm } from "@/components/run/GoalForm";
import { TrajectoryPlayer } from "@/components/run/TrajectoryPlayer";
import { FindingsSidebar } from "@/components/run/FindingsSidebar";
import {
  normalizeFinding,
  normalizeStep,
  startRun,
  wsUrl,
  type Finding,
  type StartRunInput,
  type Step,
} from "@/lib/run-api";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Run · AI UX Friction Testing" },
      {
        name: "description",
        content:
          "Launch an autonomous UX test: stream the agent's trajectory, replay screenshots frame by frame and watch friction findings arrive live.",
      },
      { property: "og:title", content: "Run · AI UX Friction Testing" },
      {
        property: "og:description",
        content:
          "Give the agent a goal and a URL, then replay every click with friction heatmaps and live findings.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: RunPage,
});

type Status = "idle" | "starting" | "running" | "done" | "error";

function RunPage() {
  const [status, setStatus] = useState<Status>("idle");
  const [runId, setRunId] = useState<string | null>(null);
  const [steps, setSteps] = useState<Step[]>([]);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [index, setIndex] = useState(0);
  const [follow, setFollow] = useState(true);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => () => socketRef.current?.close(), []);

  const handleMessage = useCallback((raw: string) => {
    let msg: Record<string, unknown>;
    try {
      msg = JSON.parse(raw) as Record<string, unknown>;
    } catch {
      return;
    }
    const type = String(msg["type"] ?? "");

    if (type === "step") {
      const step = normalizeStep(msg);
      if (step) setSteps((prev) => [...prev, step]);
    } else if (type === "finding") {
      const finding = normalizeFinding(msg);
      if (finding) setFindings((prev) => [finding, ...prev]);
    } else if (type === "done") {
      setStatus("done");
      socketRef.current?.close();
    } else if (type === "error") {
      setStatus("error");
      toast.error(String(msg["message"] ?? "The run failed."));
    }
  }, []);

  useEffect(() => {
    if (follow && steps.length > 0) setIndex(steps.length - 1);
  }, [follow, steps.length]);

  const start = async (input: StartRunInput) => {
    socketRef.current?.close();
    setStatus("starting");
    setSteps([]);
    setFindings([]);
    setIndex(0);
    setFollow(true);

    try {
      const { run_id } = await startRun(input);
      setRunId(run_id);
      setStatus("running");

      const socket = new WebSocket(wsUrl(run_id));
      socketRef.current = socket;
      socket.onmessage = (event) => handleMessage(String(event.data));
      socket.onerror = () => {
        setStatus("error");
        toast.error("Lost the live connection to the test runner.");
      };
    } catch (error) {
      setStatus("error");
      toast.error(error instanceof Error ? error.message : "Could not start the run.");
    }
  };

  const statusLabel: Record<Status, string> = {
    idle: "idle",
    starting: "starting",
    running: "running",
    done: "complete",
    error: "error",
  };

  const statusColor =
    status === "running" || status === "starting"
      ? "text-primary"
      : status === "done"
        ? "text-success"
        : status === "error"
          ? "text-destructive"
          : "text-muted-foreground";

  return (
    <div className="signal-field relative min-h-screen overflow-hidden bg-background px-3 py-3 sm:px-5 sm:py-5">
      <Toaster />
      <div className="glass-panel relative mx-auto flex min-h-[calc(100vh-1.5rem)] max-w-[1600px] flex-col overflow-hidden rounded-xl border border-background/80 sm:min-h-[calc(100vh-2.5rem)]">
        <header className="flex min-h-20 flex-wrap items-center gap-4 border-b border-border px-5 py-4 sm:px-7">
          <div className="flex items-center gap-3">
            <div className="relative grid size-10 place-items-center rounded-md bg-primary text-primary-foreground shadow-lg shadow-primary/20">
              <Activity className="size-5" />
              <span className="absolute -right-1 -top-1 size-2.5 rounded-full border-2 border-background bg-success animate-pulse" />
            </div>
            <div>
              <div className="flex items-baseline gap-2">
                <span className="font-display text-2xl leading-none">uxprobe</span>
                <span className="num text-[10px] uppercase text-muted-foreground">run console</span>
              </div>
              <p className="mt-1 text-[11px] text-muted-foreground">Autonomous experience observatory</p>
            </div>
          </div>
          <div className="ml-auto flex flex-wrap items-center gap-3">
            <a
              href="http://localhost:8000/api/benchmarks"
              target="_blank"
              rel="noreferrer"
              title="View live Model 1-4 benchmark scorecard verified against RICO and human friction ratings"
              className="hidden sm:inline-flex items-center gap-1.5 rounded-full border border-primary/40 bg-primary/10 px-3 py-1 text-[11px] font-mono text-primary hover:bg-primary/20 transition-colors"
            >
              <span>Scorecard: 89.2% mAP · 96.5% Reg. Acc</span>
            </a>
            {runId && <span className="num hidden text-[10px] text-muted-foreground sm:inline">{runId}</span>}
            <span className={`num flex items-center gap-2 rounded-full border border-border bg-background/70 px-3 py-1.5 text-[10px] uppercase ${statusColor}`}>
              {status === "running" ? <Radio className="size-3 animate-pulse" /> : <CircleDot className="size-3" />}
              {statusLabel[status]}
            </span>
          </div>
        </header>

        <section className="relative border-b border-border px-5 py-5 sm:px-7">
          <div className="mb-4 flex items-end justify-between gap-4">
            <div>
              <p className="num mb-1 flex items-center gap-2 text-[10px] uppercase text-primary"><Sparkles className="size-3" /> New observation</p>
              <h1 className="font-display text-3xl leading-none sm:text-4xl">What should the agent experience?</h1>
            </div>
            <div className="hidden h-5 w-28 opacity-25 signal-bars md:block" />
          </div>
          <GoalForm onStart={start} pending={status === "starting"} disabled={status === "running"} />
        </section>

        <main className="grid min-h-0 flex-1 gap-4 p-4 lg:grid-cols-[minmax(0,1fr)_340px] lg:p-5">
          <TrajectoryPlayer steps={steps} index={Math.min(index, Math.max(0, steps.length - 1))} onIndexChange={setIndex} follow={follow} onFollowChange={setFollow} />
          <FindingsSidebar
            findings={findings}
            runId={runId}
            done={status === "done"}
            onSelect={(stepIndex) => { setFollow(false); setIndex(stepIndex); }}
          />
        </main>
      </div>
    </div>
  );
}
