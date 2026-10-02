import { useMemo, useState } from "react";
import { ArrowUpDown, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { DemoTransaction } from "@/lib/monitoring-data";
import { formatINR, RiskBadge } from "./primitives";

export function TransactionFilters({
  risk,
  onRisk,
  query,
  onQuery,
  state,
  onState,
  app,
  onApp,
  category,
  onCategory,
  extended = false,
}: {
  risk: string;
  onRisk: (v: string) => void;
  query: string;
  onQuery: (v: string) => void;

  state?: string;
  onState?: (v: string) => void;

  app?: string;
  onApp?: (v: string) => void;

  category?: string;
  onCategory?: (v: string) => void;

  extended?: boolean;
}) {
  return (
    <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-6">
      {/* SEARCH */}
      <div className="relative xl:col-span-2">
        <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />

        <Input
          value={query}
          onChange={(e) => onQuery(e.target.value)}
          placeholder="Search transactions..."
          className="bg-background pl-9"
        />
      </div>

      {/* RISK */}
      <Select value={risk} onValueChange={onRisk}>
        <SelectTrigger className="bg-background">
          <SelectValue placeholder="Risk level" />
        </SelectTrigger>

        <SelectContent>
          {["All risks", "Low", "Medium", "High", "Critical"].map((x) => (
            <SelectItem key={x} value={x}>
              {x}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {extended && (
        <>
          {/* STATE */}
          <Select value={state ?? "All states"} onValueChange={(value) => onState?.(value)}>
            <SelectTrigger className="bg-background">
              <SelectValue placeholder="State" />
            </SelectTrigger>

            <SelectContent>
              {[
                "All states",
                "Maharashtra",
                "Karnataka",
                "Delhi",
                "Tamil Nadu",
                "Uttar Pradesh",
                "Telangana",
                "Gujarat",
                "West Bengal",
                "Rajasthan",
                "Kerala",
              ].map((x) => (
                <SelectItem key={x} value={x}>
                  {x}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* UPI APP */}
          <Select value={app ?? "All apps"} onValueChange={(value) => onApp?.(value)}>
            <SelectTrigger className="bg-background">
              <SelectValue placeholder="UPI app" />
            </SelectTrigger>

            <SelectContent>
              {[
                "All apps",
                "PhonePe",
                "Google Pay",
                "CRED",
                "Paytm",
                "BHIM",
                "Axis Pay",
                "Amazon Pay",
                "WhatsApp Pay",
              ].map((x) => (
                <SelectItem key={x} value={x}>
                  {x}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* CATEGORY */}
          <Select
            value={category ?? "All categories"}
            onValueChange={(value) => onCategory?.(value)}
          >
            <SelectTrigger className="bg-background">
              <SelectValue placeholder="Category" />
            </SelectTrigger>

            <SelectContent>
              {[
                "All categories",
                "Peer Transfer",
                "Shopping",
                "Healthcare",
                "Health & Fitness",
                "Entertainment",
                "Transportation",
                "Groceries",
                "Fuel",
                "Food & Dining",
                "Bills & Utilities",
              ].map((x) => (
                <SelectItem key={x} value={x}>
                  {x}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </>
      )}
    </div>
  );
}
export function TransactionTable({
  rows,
  investigation = false,
}: {
  rows: DemoTransaction[];
  investigation?: boolean;
}) {
  const [selected, setSelected] = useState<DemoTransaction>();
  const [descending, setDescending] = useState(true);
  const sorted = useMemo(
    () =>
      [...rows].sort((a, b) =>
        descending ? b.riskScore - a.riskScore : a.riskScore - b.riskScore,
      ),
    [rows, descending],
  );
  return (
    <>
      <div className="overflow-hidden rounded-md border">
        <Table>
          <TableHeader className="bg-muted/70">
            <TableRow>
              <TableHead>Transaction ID</TableHead>
              <TableHead>Amount</TableHead>
              <TableHead>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setDescending((v) => !v)}
                  className="-ml-3"
                >
                  Risk score
                  <ArrowUpDown />
                </Button>
              </TableHead>
              <TableHead>Risk</TableHead>
              <TableHead>Signals</TableHead>
              {investigation && (
                <>
                  <TableHead>Anomaly type</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>State</TableHead>
                </>
              )}{" "}
              {!investigation && (
                <>
                  <TableHead>Category</TableHead>
                  <TableHead>Timestamp</TableHead>
                </>
              )}
            </TableRow>
          </TableHeader>
          <TableBody>
            {sorted.length ? (
              sorted.map((row) => (
                <TableRow
                  key={row.transactionId}
                  className="cursor-pointer"
                  onClick={() => setSelected(row)}
                >
                  <TableCell className="font-mono text-xs font-semibold text-primary">
                    {row.transactionId}
                  </TableCell>
                  <TableCell className="font-semibold">{formatINR(row.amount)}</TableCell>
                  <TableCell>{row.riskScore}</TableCell>
                  <TableCell>
                    <RiskBadge level={row.riskLevel} />
                  </TableCell>
                  <TableCell>
                    <span className="inline-grid size-7 place-items-center rounded-md bg-secondary text-xs font-bold">
                      {row.signalCount}
                    </span>
                  </TableCell>
                  {investigation && (
                    <>
                      <TableCell>{row.anomalyType}</TableCell>
                      <TableCell>{row.category}</TableCell>
                      <TableCell>{row.state}</TableCell>
                    </>
                  )}
                  {!investigation && (
                    <>
                      <TableCell>{row.category}</TableCell>
                      <TableCell className="whitespace-nowrap text-xs text-muted-foreground">
                        {row.timestamp}
                      </TableCell>
                    </>
                  )}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={9} className="h-28 text-center text-muted-foreground">
                  No sample transactions match these filters.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <Sheet open={Boolean(selected)} onOpenChange={(open) => !open && setSelected(undefined)}>
        <SheetContent className="w-full overflow-y-auto sm:max-w-md">
          <SheetHeader>
            <SheetTitle>Transaction detail</SheetTitle>
            <SheetDescription>
              Illustrative sample record — not a confirmed fraud determination.
            </SheetDescription>
          </SheetHeader>
          {selected && (
            <div className="mt-6 space-y-5">
              <div className="rounded-lg border bg-muted/50 p-4">
                <div className="font-mono text-sm font-bold text-primary">
                  {selected.transactionId}
                </div>
                <div className="mt-2 font-display text-3xl font-bold">
                  {formatINR(selected.amount)}
                </div>
                <div className="mt-3">
                  <RiskBadge level={selected.riskLevel} />
                </div>
              </div>
              {[
                ["Risk score", selected.riskScore],
                ["Anomaly signals", selected.signalCount],
                ["Signal type", selected.anomalyType],
                ["Category", selected.category],
                ["State", selected.state],
                ["UPI app", selected.app],
                ["Transaction type", selected.transactionType],
                ["Timestamp", selected.timestamp],
              ].map(([k, v]) => (
                <div
                  key={String(k)}
                  className="flex items-center justify-between border-b pb-3 text-sm"
                >
                  <span className="text-muted-foreground">{k}</span>
                  <span className="text-right font-semibold">{v}</span>
                </div>
              ))}
              <div className="rounded-md border border-warning/35 bg-warning/10 p-3 text-xs">
                This sample indicates unusual behavior for review. It is not a confirmed fraud label
                or calibrated probability.
              </div>
            </div>
          )}
        </SheetContent>
      </Sheet>
    </>
  );
}
