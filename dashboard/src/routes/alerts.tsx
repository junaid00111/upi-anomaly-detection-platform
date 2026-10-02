import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { BellRing, Clock3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DemoNotice,
  formatINR,
  PageHeader,
  Panel,
  RiskBadge,
} from "@/components/dashboard/primitives";
import { getInvestigations } from "@/lib/monitoring-api";

export const Route = createFileRoute("/alerts")({
  head: () => ({
    meta: [
      { title: "Risk & Anomaly Alerts — UPI Risk Monitor" },
      { name: "description", content: "Review High and Critical UPI risk and anomaly alerts." },
      { property: "og:title", content: "UPI Risk & Anomaly Alerts" },
      {
        property: "og:description",
        content: "Prioritized unusual transaction alerts for investigation.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Alerts,
  errorComponent: () => <div role="alert">Alerts could not be loaded.</div>,
  notFoundComponent: () => <div>No alerts found.</div>,
});

function Alerts() {
  const [severity, setSeverity] = useState("All");
  const {
    data: investigations = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ["investigations"],
    queryFn: () => getInvestigations(100),
  });

  const alerts = investigations.filter((r) => severity === "All" || r.riskLevel === severity);

  if (error)
    return (
      <div role="alert" className="p-6">
        Alerts could not be loaded.
      </div>
    );

  return (
    <>
      <PageHeader
        title="Risk & Anomaly Alerts"
        description="Review High and Critical investigation candidates. Alerts indicate unusual behavior and are not confirmed fraud events."
      />
      <DemoNotice />
      <Panel
        title="Investigation candidates"
        subtitle={isLoading ? "Loading live alerts..." : `${alerts.length} visible alerts`}
      >
        <div className="mb-4 flex gap-2">
          {["All", "Critical", "High"].map((s) => (
            <Button
              key={s}
              size="sm"
              variant={severity === s ? "default" : "outline"}
              onClick={() => setSeverity(s)}
            >
              {s}
            </Button>
          ))}
        </div>
        <div className="space-y-3">
          {alerts.map((a) => (
            <div
              key={a.transactionId}
              className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3 rounded-lg border bg-card p-4 transition-colors hover:bg-muted/30"
            >
              <div className="grid size-10 shrink-0 place-items-center rounded-md bg-critical/10 text-critical">
                <BellRing className="size-5" />
              </div>
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="truncate font-mono text-xs font-bold text-primary">
                    {a.transactionId}
                  </span>
                  <RiskBadge level={a.riskLevel} />
                </div>
                <p className="mt-1 text-sm">
                  <span className="font-semibold">{a.anomalyType}</span> · {a.category} ·{" "}
                  {a.signalCount} anomaly signals
                </p>
                <div className="mt-1 flex items-center gap-1 text-xs text-muted-foreground">
                  <Clock3 className="size-3" />
                  {a.timestamp}
                </div>
              </div>
              <div className="shrink-0 text-right">
                <div className="font-display text-lg font-bold">{formatINR(a.amount)}</div>
                <div className="text-xs text-muted-foreground">Risk score {a.riskScore}</div>
              </div>
            </div>
          ))}
        </div>
      </Panel>
    </>
  );
}
