import { useSuspenseQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { BrainCircuit, CheckCircle2, Info, Scale } from "lucide-react";
import { CountBarChart, DonutChart } from "@/components/dashboard/charts";
import { DemoNotice, MetricCard, PageHeader, Panel } from "@/components/dashboard/primitives";
import { monitoringQueryOptions } from "@/lib/monitoring-query";

export const Route = createFileRoute("/model-evaluation")({
  head: () => ({ meta: [{ title: "Model Evaluation — UPI Risk Monitor" }] }),
  loader: ({ context }) => context.queryClient.ensureQueryData(monitoringQueryOptions),
  component: ModelEvaluation,
});

function ModelEvaluation() {
  const { data } = useSuspenseQuery(monitoringQueryOptions);
  const flagged = data.detectionMethods.reduce((sum, item) => sum + item.count, 0);
  const agreement = data.modelAgreement.find((item) => item.name.includes("2+"))?.value ?? 0;
  return (
    <>
      <PageHeader title="Model Evaluation" description="Compare unsupervised detection methods, stability, and agreement without making unsupported accuracy claims." />
      <DemoNotice />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Methods evaluated" value="5" note="IQR, time series, Isolation Forest, LOF, and One-Class SVM" icon={BrainCircuit} />
        <MetricCard label="Total model flags" value={flagged.toLocaleString("en-IN")} note="Flags can overlap across methods" icon={Scale} />
        <MetricCard label="2+ model agreement" value={agreement.toLocaleString("en-IN")} note="Records flagged by at least two methods" icon={CheckCircle2} tone="success" />
        <MetricCard label="Ground-truth labels" value="Unavailable" note="The supplied dataset has no confirmed fraud label" icon={Info} tone="warning" />
      </div>
      <div className="mt-4 grid gap-4 xl:grid-cols-3">
        <Panel title="Detection output comparison" subtitle="Anomaly flags by method — not accuracy" className="xl:col-span-2"><CountBarChart data={data.detectionMethods} /></Panel>
        <Panel title="Agreement distribution" subtitle="Overlap supports review prioritization"><DonutChart data={data.modelAgreement} centerValue={agreement.toLocaleString("en-IN")} centerLabel="2+ agree" /></Panel>
      </div>
      <Panel title="Evaluation interpretation" subtitle="What this page can and cannot prove" className="mt-4">
        <div className="grid gap-4 md:grid-cols-3"><InfoCard title="Agreement" text="Records flagged by multiple independent methods are useful candidates for review, but agreement is not proof of fraud." /><InfoCard title="Stability" text="Sensitivity analysis should be used to compare queue volume across thresholds and contamination assumptions." /><InfoCard title="Next research step" text="Add reviewed or synthetic labelled cases before reporting precision, recall, F1, or ROC-AUC." /></div>
      </Panel>
    </>
  );
}
function InfoCard({ title, text }: { title: string; text: string }) { return <div className="rounded-md border bg-muted/40 p-4"><h3 className="text-sm font-bold">{title}</h3><p className="mt-2 text-xs leading-5 text-muted-foreground">{text}</p></div>; }
