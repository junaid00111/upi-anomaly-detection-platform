import { useSuspenseQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { BrainCircuit, Layers3, Scale, ScanLine, Waypoints } from "lucide-react";
import { CountBarChart, DonutChart } from "@/components/dashboard/charts";
import { MetricCard, PageHeader, Panel } from "@/components/dashboard/primitives";
import { monitoringQueryOptions } from "@/lib/monitoring-query";
export const Route = createFileRoute("/ml-models")({
  head: () => ({
    meta: [
      { title: "ML Models — UPI Risk Monitor" },
      {
        name: "description",
        content: "Compare anomaly counts and agreement across unsupervised detection methods.",
      },
      { property: "og:title", content: "UPI Anomaly Detection Models" },
      {
        property: "og:description",
        content: "Model anomaly counts and agreement without unsupported accuracy claims.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  loader: ({ context }) => context.queryClient.ensureQueryData(monitoringQueryOptions),
  component: Models,
  errorComponent: () => <div role="alert">Model data could not be loaded.</div>,
  notFoundComponent: () => <div>No model data found.</div>,
});
function Models() {
  const { data } = useSuspenseQuery(monitoringQueryOptions);
  return (
    <>
      <PageHeader
        title="ML Models"
        description="Compare detection output volumes and agreement. Counts describe anomaly flags, not model accuracy or fraud probability."
      />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <MetricCard
          label="IQR anomalies"
          value="1,004"
          note="Threshold-based amount outliers"
          icon={Scale}
        />
        <MetricCard
          label="Isolation Forest"
          value="500"
          note="Original and new runs each flag 500"
          icon={BrainCircuit}
        />
        <MetricCard
          label="Time-series anomalies"
          value="659"
          note="Temporal deviation signals"
          icon={ScanLine}
        />
        <MetricCard
          label="LOF anomalies"
          value="500"
          note="Local density outliers"
          icon={Waypoints}
        />
        <MetricCard
          label="One-Class SVM"
          value="504"
          note="Boundary-based anomaly flags"
          icon={Layers3}
        />
      </div>
      <div className="mt-4 grid gap-4 xl:grid-cols-3">
        <Panel
          title="Detection method comparison"
          subtitle="Anomaly counts — not accuracy"
          className="xl:col-span-2"
        >
          <CountBarChart data={data.detectionMethods} />
        </Panel>
        <Panel title="Model agreement" subtitle="146 all-three · 409 two-or-more">
          <DonutChart data={data.modelAgreement} centerValue="409" centerLabel="2+ models agree" />
        </Panel>
      </div>
      <Panel
        title="Assumptions & interpretation"
        subtitle="How to read these unsupervised outputs"
        className="mt-4"
      >
        <div className="grid gap-4 md:grid-cols-3">
          <Info
            title="Contamination"
            text="Isolation Forest and related methods can be configured with an expected anomaly proportion. A flagged count reflects that assumption, not known fraud prevalence."
          />
          <Info
            title="Thresholds"
            text="IQR and time-series rules depend on project-defined statistical boundaries. Crossing a boundary indicates unusual behavior for review."
          />
          <Info
            title="Agreement"
            text="Multiple models flagging the same record can strengthen review priority, but does not establish fraud or a calibrated probability."
          />
        </div>
      </Panel>
    </>
  );
}
function Info({ title, text }: { title: string; text: string }) {
  return (
    <div className="rounded-md border bg-muted/40 p-4">
      <h3 className="text-sm font-bold">{title}</h3>
      <p className="mt-2 text-xs leading-5 text-muted-foreground">{text}</p>
    </div>
  );
}
