import { ArrowDownRight, ArrowUpRight, Info, type LucideIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

export function PageHeader({
  title,
  description,
  actions,
}: {
  title: string;
  description: string;
  actions?: ReactNode;
}) {
  return (
    <div className="mb-6 grid grid-cols-[minmax(0,1fr)_auto] items-end gap-4">
      <div className="min-w-0">
        <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase text-primary">
          <span className="h-px w-5 bg-primary" />
          UPI anomaly monitoring
        </div>
        <h1 className="text-2xl font-bold text-foreground sm:text-3xl">{title}</h1>
        <p className="mt-1 max-w-3xl text-sm text-muted-foreground">{description}</p>
      </div>
      {actions && <div className="shrink-0">{actions}</div>}
    </div>
  );
}
export function DemoNotice() {
  return (
    <div className="mb-5 flex items-start gap-2 rounded-md border border-warning/35 bg-warning/10 px-3 py-2 text-xs text-foreground">
      <Info className="mt-0.5 size-4 shrink-0 text-warning" />
      <span>
        Live PostgreSQL data is connected through FastAPI for supported views. Anomaly signals
        indicate unusual behavior and do not represent confirmed fraud.
      </span>
    </div>
  );
}
export function MetricCard({
  label,
  value,
  note,
  icon: Icon,
  tone = "primary",
}: {
  label: string;
  value: string;
  note: string;
  icon: LucideIcon;
  tone?: "primary" | "success" | "warning" | "critical";
}) {
  const tones = {
    primary: "bg-primary/10 text-primary",
    success: "bg-success/10 text-success",
    warning: "bg-warning/15 text-warning",
    critical: "bg-critical/10 text-critical",
  };
  return (
    <Card className="glass-card overflow-hidden rounded-lg border-border/70 transition-transform hover:-translate-y-0.5">
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className={cn("grid size-10 place-items-center rounded-md", tones[tone])}>
            <Icon className="size-5" />
          </div>
          <Tooltip>
            <TooltipTrigger asChild>
              <Info className="size-4 text-muted-foreground" />
            </TooltipTrigger>
            <TooltipContent>{note}</TooltipContent>
          </Tooltip>
        </div>
        <div className="mt-5 font-display text-2xl font-bold text-foreground">{value}</div>
        <div className="mt-1 text-xs font-medium text-muted-foreground">{label}</div>
      </CardContent>
    </Card>
  );
}
export function Panel({
  title,
  subtitle,
  children,
  className,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <Card className={cn("glass-card rounded-lg border-border/70", className)}>
      <CardHeader className="grid grid-cols-[minmax(0,1fr)_auto] gap-3 p-5 pb-2">
        <div className="min-w-0">
          <CardTitle className="text-base">{title}</CardTitle>
          {subtitle && <p className="mt-1 text-xs text-muted-foreground">{subtitle}</p>}
        </div>
      </CardHeader>
      <CardContent className="p-5 pt-3">{children}</CardContent>
    </Card>
  );
}
export function RiskBadge({ level }: { level: string }) {
  const cls =
    level === "Critical"
      ? "border-critical/30 bg-critical/10 text-critical"
      : level === "High"
        ? "border-warning/35 bg-warning/15 text-warning"
        : level === "Medium"
          ? "border-primary/25 bg-primary/10 text-primary"
          : "border-success/25 bg-success/10 text-success";
  return (
    <Badge variant="outline" className={cn("whitespace-nowrap font-semibold", cls)}>
      {level}
    </Badge>
  );
}
export function Delta({ value, positive = true }: { value: string; positive?: boolean }) {
  const I = positive ? ArrowUpRight : ArrowDownRight;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 text-xs",
        positive ? "text-success" : "text-critical",
      )}
    >
      <I className="size-3" />
      {value}
    </span>
  );
}
export const formatINR = (value: number) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
