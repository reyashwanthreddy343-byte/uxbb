import { ArrowRight, ShieldAlert } from "lucide-react";
import { Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { confidencePct, type Finding } from "@/lib/run-api";

function severityStyles(severity: string) {
  switch (severity.toLowerCase()) {
    case "critical":
      return "border-destructive/60 text-destructive bg-destructive/10";
    case "high":
      return "border-warning/60 text-warning bg-warning/10";
    case "medium":
      return "border-accent/60 text-accent bg-accent/10";
    case "low":
      return "border-success/50 text-success bg-success/10";
    default:
      return "border-border-strong text-muted-foreground bg-muted/40";
  }
}

interface FindingsSidebarProps {
  findings: Finding[];
  runId: string | null;
  done: boolean;
  onSelect?: (stepIndex: number) => void;
}

export function FindingsSidebar({ findings, runId, done, onSelect }: FindingsSidebarProps) {
  return (
    <aside className="glass-panel flex min-h-[360px] flex-col overflow-hidden rounded-lg border border-background/90 lg:h-full lg:min-h-0">
      <header className="flex min-h-14 items-center justify-between border-b border-border px-4 py-3">
        <div className="flex items-center gap-2">
          <ShieldAlert className="size-4 text-primary" />
          <div><h2 className="text-xs font-semibold uppercase">Live findings</h2><p className="mt-0.5 text-[10px] text-muted-foreground">Signal intelligence</p></div>
        </div>
        <span className="num rounded border border-border px-1.5 py-0.5 text-xs text-muted-foreground">
          {findings.length.toString().padStart(2, "0")}
        </span>
      </header>

      <ScrollArea className="min-h-0 flex-1">
        <ul className="divide-y divide-border">
          {findings.map((finding, i) => (
            <li key={finding.id ?? i}>
              <button
                type="button"
                onClick={() =>
                  finding.step_index !== undefined && onSelect?.(finding.step_index)
                }
                className="float-in w-full px-4 py-4 text-left transition-all hover:bg-sidebar-accent hover:pl-5"
              >
                <div className="flex items-center gap-2">
                  <span
                    className={`num rounded border px-1.5 py-0.5 text-[10px] uppercase tracking-wider ${severityStyles(finding.severity)}`}
                  >
                    {finding.severity}
                  </span>
                  <span className="num text-[11px] text-muted-foreground">
                    {confidencePct(finding.confidence)}% conf
                  </span>
                  {finding.step_index !== undefined && (
                    <span className="num ml-auto text-[11px] text-muted-foreground">
                      #{finding.step_index}
                    </span>
                  )}
                </div>
                <p className="mt-2 text-sm leading-snug text-foreground">{finding.title}</p>
                {finding.description && (
                  <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
                    {finding.description}
                  </p>
                )}
              </button>
            </li>
          ))}
          {findings.length === 0 && (
            <li className="px-5 py-10 text-center">
              <div className="mx-auto mb-4 flex h-9 w-16 items-center justify-center gap-1 rounded-full border border-border bg-background/55">
                <span className="h-3 w-0.5 bg-primary/35 animate-pulse" /><span className="h-5 w-0.5 bg-primary/60 animate-pulse" /><span className="h-2 w-0.5 bg-primary/30 animate-pulse" /><span className="h-4 w-0.5 bg-primary/50 animate-pulse" />
              </div>
              <p className="font-display text-lg text-foreground">Waiting for signal</p>
              <p className="mt-1 text-xs text-muted-foreground">Findings appear as the agent explores.</p>
            </li>
          )}
        </ul>
      </ScrollArea>

      {done && runId && (
        <div className="border-t border-border p-3">
          <Button asChild className="w-full gap-2">
            <Link to="/report/$runId" params={{ runId }}>
              View Full Report <ArrowRight className="size-4" />
            </Link>
          </Button>
        </div>
      )}
    </aside>
  );
}
