import { useState } from "react";
import { Loader2, Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { Platform, StartRunInput } from "@/lib/run-api";

interface GoalFormProps {
  onStart: (input: StartRunInput) => void;
  pending: boolean;
  disabled?: boolean;
}

export function GoalForm({ onStart, pending, disabled }: GoalFormProps) {
  const [goal, setGoal] = useState("");
  const [url, setUrl] = useState("");
  const [platform, setPlatform] = useState<Platform>("chrome");

  return (
    <form
      className="grid gap-3 md:grid-cols-[minmax(0,1.5fr)_minmax(0,1fr)_180px]"
      onSubmit={(e) => {
        e.preventDefault();
        if (!goal.trim() || !url.trim()) return;
        onStart({ goal: goal.trim(), url: url.trim(), platform });
      }}
    >
      <div className="space-y-1.5">
        <Label htmlFor="goal" className="num text-[10px] uppercase text-muted-foreground">
          01 / Goal
        </Label>
        <Textarea
          id="goal"
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          rows={2}
          placeholder="Sign up for a free account and invite a teammate"
          className="min-h-20 resize-none border-background bg-background/70 font-mono text-sm shadow-sm transition-shadow focus-visible:shadow-md"
        />
      </div>

      <div className="space-y-1.5">
          <Label htmlFor="url" className="num text-[10px] uppercase text-muted-foreground">
            02 / Target URL
          </Label>
          <Input
            id="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://app.example.com"
            className="h-12 border-background bg-background/70 font-mono text-sm shadow-sm"
          />
          <div className="mt-2 flex items-center gap-2 text-[10px] text-muted-foreground"><span className="size-1.5 rounded-full bg-success animate-pulse" /> Endpoint ready</div>
      </div>

      <div className="flex flex-col gap-1.5">
          <Label className="num text-[10px] uppercase text-muted-foreground">03 / Platform</Label>
          <Select value={platform} onValueChange={(v) => setPlatform(v as Platform)}>
            <SelectTrigger className="h-12 border-background bg-background/70 font-mono text-sm shadow-sm"><SelectValue /></SelectTrigger>
            <SelectContent><SelectItem value="chrome">Chrome</SelectItem><SelectItem value="firefox">Firefox</SelectItem><SelectItem value="android">Android</SelectItem></SelectContent>
          </Select>
          <Button type="submit" disabled={pending || disabled} className="mt-2 h-10 gap-2 font-semibold shadow-lg shadow-primary/20">
            {pending ? <Loader2 className="size-4 animate-spin" /> : <Play className="size-4" />}
            {pending ? "Starting" : "Run test"}
          </Button>
      </div>

      {/* Preset Targets Bar */}
      <div className="col-span-full mt-1 flex flex-wrap items-center gap-2 pt-1 border-t border-border/50 text-[11px]">
        <span className="font-mono text-[10px] uppercase text-muted-foreground">Quick Demos:</span>
        <button
          type="button"
          onClick={() => {
            setGoal("Complete checkout for Apex Runner blue sneakers");
            setUrl("http://localhost:8000/mock_apps/sample_ecommerce/v1_good.html");
          }}
          className="rounded border border-border bg-background/60 px-2 py-1 text-xs font-mono transition-colors hover:border-primary hover:text-primary"
        >
          ✅ Baseline (ApexGear v1)
        </button>
        <button
          type="button"
          onClick={() => {
            setGoal("Apply promo code and proceed to checkout");
            setUrl("http://localhost:8000/mock_apps/sample_ecommerce/v2_regression.html");
          }}
          className="rounded border border-border bg-background/60 px-2 py-1 text-xs font-mono transition-colors hover:border-destructive hover:text-destructive"
        >
          ⚠️ Injected Regression (ApexGear v2)
        </button>
      </div>
    </form>
  );
}
