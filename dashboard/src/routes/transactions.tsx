import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";

import { PageHeader, Panel } from "@/components/dashboard/primitives";

import { TransactionFilters, TransactionTable } from "@/components/dashboard/transaction-table";

import { getTransactions } from "@/lib/monitoring-api";

export const Route = createFileRoute("/transactions")({
  head: () => ({
    meta: [
      {
        title: "Transactions — UPI Risk Monitor",
      },
      {
        name: "description",
        content: "Search and inspect UPI transaction anomaly signals.",
      },
      {
        property: "og:title",
        content: "UPI Transaction Explorer",
      },
      {
        property: "og:description",
        content: "Searchable transaction risk and anomaly signal workspace.",
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

  component: Transactions,

  errorComponent: () => <div role="alert">Transactions could not be loaded.</div>,

  notFoundComponent: () => <div>No transactions found.</div>,
});

function Transactions() {
  const [risk, setRisk] = useState("All risks");
  const [query, setQuery] = useState("");
  const [state, setState] = useState("All states");
  const [app, setApp] = useState("All apps");
  const [category, setCategory] = useState("All categories");

  const [page, setPage] = useState(0);

  const pageSize = 50;

  const { data, isLoading, isFetching, error } = useQuery({
    queryKey: ["transactions", page, query, risk, state, app, category],

    queryFn: () =>
      getTransactions({
        limit: pageSize,
        offset: page * pageSize,
        search: query,
        riskLevel: risk,
        state,
        app,
        category,
      }),

    placeholderData: (previousData) => previousData,
  });

  const rows = data?.transactions ?? [];

  const total = data?.total ?? 0;

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  const firstRecord = total === 0 ? 0 : page * pageSize + 1;

  const lastRecord = Math.min((page + 1) * pageSize, total);

  function changeRisk(value: string) {
    setRisk(value);
    setPage(0);
  }

  function changeSearch(value: string) {
    setQuery(value);
    setPage(0);
  }

  function changeState(value: string) {
    setState(value);
    setPage(0);
  }

  function changeApp(value: string) {
    setApp(value);
    setPage(0);
  }

  function changeCategory(value: string) {
    setCategory(value);
    setPage(0);
  }

  function previousPage() {
    setPage((current) => Math.max(0, current - 1));
  }

  function nextPage() {
    setPage((current) => Math.min(totalPages - 1, current + 1));
  }

  if (error) {
    return (
      <div role="alert" className="p-6">
        Transactions could not be loaded.
      </div>
    );
  }

  return (
    <>
      <PageHeader
        title="Transactions"
        description="Search and inspect transaction-level risk signals from the PostgreSQL-backed monitoring pipeline."
      />

      <div className="mb-4 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
        <strong>Live data source:</strong> PostgreSQL via FastAPI · server-side filtering and
        pagination
      </div>

      <Panel
        title="Transaction explorer"
        subtitle={
          isLoading
            ? "Loading transactions..."
            : `${firstRecord.toLocaleString("en-IN")}–${lastRecord.toLocaleString(
                "en-IN",
              )} of ${total.toLocaleString("en-IN")} matching records`
        }
      >
        <div className="mb-4">
          <TransactionFilters
            risk={risk}
            onRisk={changeRisk}
            query={query}
            onQuery={changeSearch}
            state={state}
            onState={changeState}
            app={app}
            onApp={changeApp}
            category={category}
            onCategory={changeCategory}
            extended
          />
        </div>

        {isFetching && !isLoading && (
          <div className="mb-3 text-xs text-muted-foreground">Updating transaction results...</div>
        )}

        <TransactionTable rows={rows} />

        {/* PAGINATION */}
        <div className="mt-4 flex flex-col gap-3 border-t pt-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="text-sm text-muted-foreground">
            Page {page + 1} of {totalPages}
          </div>

          <div className="flex gap-2">
            <button
              type="button"
              onClick={previousPage}
              disabled={page === 0 || isFetching}
              className="rounded-md border px-4 py-2 text-sm font-medium transition hover:bg-muted disabled:cursor-not-allowed disabled:opacity-50"
            >
              ← Previous
            </button>

            <button
              type="button"
              onClick={nextPage}
              disabled={page >= totalPages - 1 || isFetching}
              className="rounded-md border px-4 py-2 text-sm font-medium transition hover:bg-muted disabled:cursor-not-allowed disabled:opacity-50"
            >
              Next →
            </button>
          </div>
        </div>
      </Panel>
    </>
  );
}
