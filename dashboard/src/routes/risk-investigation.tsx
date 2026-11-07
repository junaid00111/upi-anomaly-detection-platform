import { useState } from "react";
import { useQuery, useSuspenseQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { AlertTriangle, ScanSearch, ShieldAlert, Siren } from "lucide-react";
import { DemoNotice, MetricCard, PageHeader, Panel } from "@/components/dashboard/primitives";
import { TransactionFilters, TransactionTable } from "@/components/dashboard/transaction-table";
import { getInvestigations } from "@/lib/monitoring-api";
import { monitoringQueryOptions } from "@/lib/monitoring-query";

export const Route = createFileRoute("/risk-investigation")({
  head: () => ({
    meta: [
      { title: "Risk & Investigation — UPI Risk Monitor" },
      {
        name: "description",
        content: "Prioritized review workspace for High and Critical anomaly candidates.",
      },
      { property: "og:title", content: "UPI Risk & Investigation" },
      {
        property: "og:description",
        content: "Prioritize unusual transactions using risk levels and signal agreement.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  loader: ({ context }) => context.queryClient.ensureQueryData(monitoringQueryOptions),
  component: Investigation,
  errorComponent: () => <div role="alert">Investigation data could not be loaded.</div>,
  notFoundComponent: () => <div>No investigation candidates found.</div>,
});

function Investigation() {
  const [risk, setRisk] = useState("High / Critical");
  const [query, setQuery] = useState("");
  const { data: snapshot } = useSuspenseQuery(monitoringQueryOptions);
  const {
    data: transactions = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ["investigations"],
    queryFn: () => getInvestigations(100),
  });

  const rows = transactions.filter(
    (r) =>
      (risk === "High / Critical"
        ? ["High", "Critical"].includes(r.riskLevel)
        : risk === "All risks" || r.riskLevel === risk) &&
      r.transactionId.toLowerCase().includes(query.toLowerCase()),
  );

  if (error)
    return (
      <div role="alert" className="p-6">
        Investigation data could not be loaded.
      </div>
    );

  return (
    <>
      <PageHeader
        title="Risk & Investigation"
        description="Prioritize unusual behavior for analyst review. High and Critical candidates are shown first by default."
      />
      <DemoNotice />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Investigation required"
          value={snapshot.projectMetrics.investigationRequired.toLocaleString("en-IN")}
          note={`${snapshot.projectMetrics.highRisk} High + ${snapshot.projectMetrics.criticalRisk} Critical candidates`}
          icon={ScanSearch}
        />
        <MetricCard
          label="High risk"
          value={snapshot.projectMetrics.highRisk.toLocaleString("en-IN")}
          note="High-priority anomaly candidates"
          icon={ShieldAlert}
          tone="warning"
        />
        <MetricCard
          label="Critical risk"
          value={snapshot.projectMetrics.criticalRisk.toLocaleString("en-IN")}
          note="Highest-priority anomaly candidates"
          icon={Siren}
          tone="critical"
        />
        <MetricCard
          label="Average risk score"
          value={snapshot.projectMetrics.averageRiskScore.toFixed(2)}
          note="Project average; not a fraud probability"
          icon={AlertTriangle}
        />
      </div>
      <Panel
        title="Investigation queue"
        subtitle={
          isLoading
            ? "Loading live investigation candidates..."
            : `${rows.length} visible candidates`
        }
        className="mt-4"
      >
        <div className="mb-4">
          <TransactionFilters risk={risk} onRisk={setRisk} query={query} onQuery={setQuery} />
        </div>
        <TransactionTable rows={rows} investigation />
      </Panel>
    </>
  );
}
