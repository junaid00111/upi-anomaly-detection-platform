import { useSuspenseQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import {
  IndianRupee,
  ReceiptIndianRupee,
  ScanSearch,
  ShieldAlert,
  WalletCards,
} from "lucide-react";

import {
  CountBarChart,
  DonutChart,
  HorizontalRateChart,
  StackedRiskChart,
  TrendChart,
} from "@/components/dashboard/charts";

import { MetricCard, PageHeader, Panel } from "@/components/dashboard/primitives";

import { monitoringQueryOptions } from "@/lib/monitoring-query";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      {
        title: "Executive Overview — UPI Risk Monitor",
      },
      {
        name: "description",
        content: "Executive view of UPI transaction anomalies, risk levels, and model signals.",
      },
      {
        property: "og:title",
        content: "UPI Risk Monitoring Executive Overview",
      },
      {
        property: "og:description",
        content: "Portfolio dashboard for anomaly detection and investigation prioritization.",
      },
      {
        property: "og:type",
        content: "website",
      },
      {
        name: "twitter:card",
        content: "summary_large_image",
      },
    ],
  }),

  loader: ({ context }) => context.queryClient.ensureQueryData(monitoringQueryOptions),

  component: Overview,

  errorComponent: () => <div role="alert">Overview data could not be loaded.</div>,

  notFoundComponent: () => <div>No overview data found.</div>,
});

function Overview() {
  const { data } = useSuspenseQuery(monitoringQueryOptions);

  const m = data.projectMetrics;

  const highRiskCount = m.highRisk;
  const criticalRiskCount = m.criticalRisk;

  const allThreeAgreement =
    data.modelAgreement.find((item) => item.name === "All 3 agree")?.value ?? 0;

  const totalSignaledRecords = data.signalDistribution
    .filter((item) => item.name !== "0 signals")
    .reduce((total, item) => total + item.value, 0);

  return (
    <>
      <PageHeader
        title="Executive Overview"
        description="Monitor unusual UPI behavior, compare detection signals, and prioritize review without treating anomalies as confirmed fraud."
      />

      <div className="mb-4 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
        <strong>Live data source:</strong> PostgreSQL via FastAPI · UPI anomaly monitoring pipeline
      </div>

      {/* KPI CARDS */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <MetricCard
          label="Total transactions"
          value={m.totalTransactions.toLocaleString("en-IN")}
          note="Transactions loaded into PostgreSQL"
          icon={WalletCards}
        />

        <MetricCard
          label="Transaction value"
          value={`₹${(m.totalValue / 1_000_000).toFixed(2)}M`}
          note="Total transaction value"
          icon={IndianRupee}
          tone="success"
        />

        <MetricCard
          label="Average amount"
          value={`₹${m.averageAmount.toLocaleString("en-IN", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}`}
          note="Mean transaction amount"
          icon={ReceiptIndianRupee}
        />

        <MetricCard
          label="Overall anomaly rate"
          value={`${m.anomalyRate.toFixed(2)}%`}
          note="Unusual behavior signal rate, not confirmed fraud"
          icon={ScanSearch}
          tone="warning"
        />

        <MetricCard
          label="Investigation required"
          value={m.investigationRequired.toLocaleString("en-IN")}
          note={`${highRiskCount} High + ${criticalRiskCount} Critical`}
          icon={ShieldAlert}
          tone="critical"
        />
      </div>

      {/* MAIN ANALYTICS */}
      <div className="mt-4 grid gap-4 xl:grid-cols-3">
        {/* DAILY TRANSACTION VOLUME */}
        <Panel
          title="Daily transaction volume"
          subtitle="Actual transaction and anomaly counts from PostgreSQL"
          className="xl:col-span-2"
        >
          <TrendChart data={data.dailyVolume} />
        </Panel>

        {/* RISK LEVEL */}
        <Panel title="Risk-level distribution" subtitle="Actual risk-level counts">
          <DonutChart
            data={data.riskLevels}
            centerValue={m.totalTransactions.toLocaleString("en-IN")}
            centerLabel="transactions"
          />
        </Panel>

        {/* UPI APP */}
        <Panel
          title="Anomaly rate by UPI app"
          subtitle="Calculated from transaction-level anomaly signals"
        >
          <HorizontalRateChart data={data.appRates} />
        </Panel>

        {/* CATEGORY */}
        <Panel
          title="Anomaly rate by category"
          subtitle="Calculated from transaction-level anomaly signals"
          className="xl:col-span-2"
        >
          <HorizontalRateChart data={data.categoryRates} />
        </Panel>

        {/* DETECTION METHODS */}
        <Panel
          title="Detection method comparison"
          subtitle="Anomaly counts, not model accuracy"
          className="xl:col-span-2"
        >
          <CountBarChart data={data.detectionMethods} />
        </Panel>

        {/* MODEL AGREEMENT */}
        <Panel
          title="ML model agreement"
          subtitle="Agreement across Isolation Forest, LOF, and One-Class SVM"
        >
          <DonutChart
            data={data.modelAgreement}
            centerValue={allThreeAgreement.toLocaleString("en-IN")}
            centerLabel="all 3 agree"
          />
        </Panel>

        {/* SIGNAL DISTRIBUTION */}
        <Panel
          title="Risk signal distribution"
          subtitle="Number of anomaly/risk signals per transaction"
        >
          <DonutChart
            data={data.signalDistribution}
            centerValue={totalSignaledRecords.toLocaleString("en-IN")}
            centerLabel="signaled records"
          />
        </Panel>

        {/* HIGH / CRITICAL */}
        <Panel
          title="High / Critical by category"
          subtitle="Actual high and critical risk transactions"
          className="xl:col-span-2"
        >
          <StackedRiskChart data={data.highRiskCategories} />
        </Panel>
      </div>
    </>
  );
}
