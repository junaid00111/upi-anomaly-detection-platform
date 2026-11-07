import { createFileRoute } from "@tanstack/react-router";
import { ArrowDown, ArrowRight, Database, FileSearch, Gauge, Layers3, Server, type LucideIcon } from "lucide-react";
import { PageHeader, Panel } from "@/components/dashboard/primitives";

export const Route = createFileRoute("/methodology")({ head: () => ({ meta: [{ title: "Methodology — UPI Risk Monitor" }] }), component: Methodology });

const steps: { icon: LucideIcon; label: string }[] = [
  { icon: Database, label: "Raw data" },
  { icon: FileSearch, label: "Validation" },
  { icon: Layers3, label: "Detection" },
  { icon: Gauge, label: "Risk scoring" },
  { icon: Server, label: "Dashboard" },
];

function Methodology() {
  return (
    <>
      <PageHeader title="Methodology" description="A transparent view of how raw UPI transactions become reviewable anomaly signals." />
      <Panel title="End-to-end monitoring pipeline" subtitle="Each stage is independently inspectable">
        <div className="flex flex-col items-stretch gap-2 md:flex-row md:items-center md:gap-1">
          {steps.map(({ icon: Icon, label }, i) => (
            <div className="flex items-center gap-2" key={label}>
              <div className="flex flex-1 items-center gap-3 rounded-lg border bg-muted/40 p-4">
                <Icon className="size-5 shrink-0 text-primary" />
                <span className="text-sm font-semibold">{label}</span>
              </div>
              {i < 4 && <ArrowRight className="hidden size-4 text-muted-foreground md:block" />}
              {i < 4 && <ArrowDown className="mx-auto size-4 text-muted-foreground md:hidden" />}
            </div>
          ))}
        </div>
      </Panel>
      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <Panel title="Detection methods">
          <div className="space-y-3 text-sm">
            <Method name="IQR" text="Flags unusually large transaction amounts using quartiles and an upper bound." />
            <Method name="Isolation Forest" text="Identifies observations that are easier to isolate from the learned normal population." />
            <Method name="LOF" text="Finds records whose local density differs substantially from nearby records." />
            <Method name="One-Class SVM" text="Learns a boundary around normal behaviour and flags observations outside it." />
            <Method name="Time series" text="Identifies unusual activity periods; this is a period-level signal, not automatic proof about one transaction." />
          </div>
        </Panel>
        <Panel title="Responsible interpretation">
          <div className="space-y-3 text-sm leading-6 text-muted-foreground">
            <p>Signals are combined into a project-defined monitoring score and review priority.</p>
            <p>The score is not a calibrated fraud probability. A flagged record is an unusual observation that may deserve investigation.</p>
            <p>Because the supplied data has no verified fraud label, accuracy metrics such as precision and recall should not be claimed without reviewed outcomes.</p>
          </div>
        </Panel>
      </div>
    </>
  );
}

function Method({ name, text }: { name: string; text: string }) {
  return (
    <div className="rounded-md border bg-muted/30 p-3">
      <div className="font-semibold">{name}</div>
      <div className="mt-1 text-xs leading-5 text-muted-foreground">{text}</div>
    </div>
  );
}
