import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { CheckCircle2, Database, FileCheck2, RefreshCw, ShieldAlert } from "lucide-react";
import { MetricCard, PageHeader, Panel } from "@/components/dashboard/primitives";
import { getDataQuality } from "@/lib/monitoring-api";

export const Route = createFileRoute("/data-quality")({
  head: () => ({ meta: [{ title: "Data Quality — UPI Risk Monitor" }] }),
  component: DataQuality,
});

function DataQuality() {
  const { data, isLoading, error, refetch } = useQuery({ queryKey: ["data-quality"], queryFn: getDataQuality, staleTime: 30_000 });
  const healthy = Boolean(data && data.quality_percent >= 95);
  return <>
    <PageHeader title="Data Quality" description="Monitor database connectivity, pipeline readiness, and the reliability of the transaction data powering this dashboard." actions={<button className="inline-flex items-center gap-2 rounded-md border bg-card px-3 py-2 text-xs font-semibold hover:bg-accent" onClick={() => void refetch()}><RefreshCw className="size-3.5" /> Refresh</button>} />
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <MetricCard label="API status" value={isLoading ? "Checking" : healthy ? "Healthy" : "Attention"} note="FastAPI health endpoint" icon={healthy ? CheckCircle2 : ShieldAlert} tone={healthy ? "success" : "warning"} />
      <MetricCard label="Quality score" value={data ? `${data.quality_percent}%` : "Unknown"} note="Database quality score based on validation defects" icon={Database} />
      <MetricCard label="Rows available" value={data?.rows?.toLocaleString("en-IN") ?? "—"} note="Records currently loaded in PostgreSQL" icon={FileCheck2} />
      <MetricCard label="Data labels" value="Unlabelled" note="No verified fraud ground truth is available" icon={ShieldAlert} tone="warning" />
    </div>
    {error ? <div role="alert" className="mt-4 rounded-lg border border-warning/40 bg-warning/10 p-4 text-sm">The API health check could not be completed. Confirm that FastAPI and PostgreSQL are running, then retry.</div> : null}
    <Panel title="Validation results" subtitle="Live checks calculated from PostgreSQL" className="mt-4"><div className="mb-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">{data && [["Duplicate IDs", data.duplicate_ids], ["Invalid amounts", data.invalid_amounts], ["Invalid timestamps", data.invalid_timestamps], ["Invalid statuses", data.invalid_statuses], ["Invalid scores", data.invalid_scores]].map(([label, value]) => <div className="rounded-md border bg-muted/30 p-3" key={String(label)}><div className="text-xs text-muted-foreground">{label as string}</div><div className="mt-1 text-lg font-bold">{String(value)}</div></div>)}</div><div className="grid gap-3 md:grid-cols-2"><Quality title="Schema validation" text="Confirm required identifiers, timestamps, amount, category, application, and status fields are present." /><Quality title="Duplicate detection" text="Check transaction IDs and sender/receiver pairs for duplicate records before modelling." /><Quality title="Missing-value review" text="Report missing values explicitly rather than silently imputing operational fields." /><Quality title="Model reproducibility" text="Record run timestamp, input row count, parameters, and output file versions for every pipeline execution." /></div></Panel>
  </>;
}
function Quality({ title, text }: { title: string; text: string }) { return <div className="rounded-md border bg-muted/40 p-4"><div className="flex items-center gap-2 text-sm font-semibold"><CheckCircle2 className="size-4 text-success" />{title}</div><p className="mt-2 text-xs leading-5 text-muted-foreground">{text}</p></div>; }
