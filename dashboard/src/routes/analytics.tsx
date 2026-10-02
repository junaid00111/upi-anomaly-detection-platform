import { useState } from "react";
import { useSuspenseQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { HorizontalRateChart, SimpleBarChart, TrendChart } from "@/components/dashboard/charts";
import { DemoNotice, PageHeader, Panel } from "@/components/dashboard/primitives";
import { monitoringQueryOptions } from "@/lib/monitoring-query";
export const Route = createFileRoute("/analytics")({
  head: () => ({
    meta: [
      { title: "Analytics — UPI Risk Monitor" },
      {
        name: "description",
        content: "Explore UPI anomaly trends across time, amounts, categories, apps, and states.",
      },
      { property: "og:title", content: "UPI Anomaly Analytics" },
      {
        property: "og:description",
        content: "Multi-dimensional analysis of supplied UPI anomaly metrics.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  loader: ({ context }) => context.queryClient.ensureQueryData(monitoringQueryOptions),
  component: Analytics,
  errorComponent: () => <div role="alert">Analytics could not be loaded.</div>,
  notFoundComponent: () => <div>No analytics found.</div>,
});
function Analytics() {
  const { data } = useSuspenseQuery(monitoringQueryOptions);
  const [period, setPeriod] = useState<"Daily" | "Weekly" | "Monthly">("Daily");
  const trend =
    period === "Daily"
      ? data.dailyVolume
      : period === "Weekly"
        ? data.weeklyVolume
        : data.monthlyVolume;
  return (
    <>
      <PageHeader
        title="Analytics"
        description="Explore volume and anomaly patterns across time, transaction size, category, application, and geography."
        actions={
          <div className="flex rounded-md border bg-card p-1">
            {(["Daily", "Weekly", "Monthly"] as const).map((p) => (
              <Button
                key={p}
                size="sm"
                variant={period === p ? "default" : "ghost"}
                onClick={() => setPeriod(p)}
              >
                {p}
              </Button>
            ))}
          </div>
        }
      />
      <DemoNotice />
      <div className="grid gap-4 xl:grid-cols-2">
        <Panel
          title={`${period} transaction volume`}
          subtitle="Daily transaction volume and anomaly signals"
        >
          <TrendChart data={trend} />
        </Panel>
        <Panel title="Amount distribution" subtitle="Transaction distribution by amount range">
          <SimpleBarChart data={data.amountBands} />
        </Panel>
        <Panel title="Category analysis" subtitle="Anomaly rate by transaction category">
          <HorizontalRateChart data={data.categoryRates} />
        </Panel>
        <Panel title="UPI app analysis" subtitle="Anomaly rate by UPI app">
          <HorizontalRateChart data={data.appRates} />
        </Panel>
        <Panel
          title="State transaction volume"
          subtitle="Transaction volume by state"
          className="xl:col-span-2"
        >
          <SimpleBarChart
            data={data.stateAnalysis.map((x) => ({ name: x.name, count: x.transactions }))}
          />
        </Panel>
      </div>
    </>
  );
}
