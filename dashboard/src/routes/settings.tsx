import { useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { SlidersHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { PageHeader, Panel } from "@/components/dashboard/primitives";
export const Route = createFileRoute("/settings")({
  head: () => ({
    meta: [
      { title: "Settings — UPI Risk Monitor" },
      {
        name: "description",
        content: "Configure project-defined UPI risk sensitivity thresholds.",
      },
      { property: "og:title", content: "UPI Risk Monitor Settings" },
      {
        property: "og:description",
        content: "Project-defined sensitivity controls for anomaly review prioritization.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Settings,
});
function Settings() {
  const [low, setLow] = useState([80]),
    [medium, setMedium] = useState([60]),
    [high, setHigh] = useState([30]),
    [saved, setSaved] = useState(false);
  return (
    <>
      <PageHeader
        title="Settings"
        description="Configure local portfolio-demo preferences and project-defined risk sensitivity thresholds."
      />
      <div className="grid gap-4 xl:grid-cols-3">
        <Panel
          title="Sensitivity thresholds"
          subtitle="Project-defined controls · not calibrated probabilities"
          className="xl:col-span-2"
        >
          <div className="space-y-7">
            {[
              ["Low sensitivity", low, setLow, "Broader anomaly capture"],
              ["Medium sensitivity", medium, setMedium, "Balanced review volume"],
              ["High sensitivity", high, setHigh, "More selective escalation"],
            ].map(([label, value, setter, note]) => (
              <div key={String(label)}>
                <div className="mb-3 grid grid-cols-[minmax(0,1fr)_auto] items-center">
                  <div>
                    <div className="text-sm font-semibold">{label as string}</div>
                    <div className="text-xs text-muted-foreground">{note as string}</div>
                  </div>
                  <div className="grid size-10 place-items-center rounded-md bg-secondary font-display font-bold text-primary">
                    {(value as number[])[0]}
                  </div>
                </div>
                <Slider
                  value={value as number[]}
                  onValueChange={setter as (v: number[]) => void}
                  min={0}
                  max={100}
                  step={1}
                />
              </div>
            ))}
          </div>
          <div className="mt-7 flex items-center gap-3">
            <Button onClick={() => setSaved(true)}>Save thresholds</Button>
            {saved && (
              <span className="text-xs font-semibold text-success">Saved for this session</span>
            )}
          </div>
        </Panel>
        <Panel title="Responsible interpretation">
          <div className="grid size-11 place-items-center rounded-md bg-primary/10 text-primary">
            <SlidersHorizontal />
          </div>
          <p className="mt-4 text-sm leading-6 text-muted-foreground">
            These values tune project review sensitivity. They are not calibrated fraud
            probabilities, confidence scores, or evidence of confirmed fraud.
          </p>
          <div className="mt-4 rounded-md border border-warning/35 bg-warning/10 p-3 text-xs">
            Validate thresholds against reviewed outcomes before operational use.
          </div>
        </Panel>
      </div>
    </>
  );
}
