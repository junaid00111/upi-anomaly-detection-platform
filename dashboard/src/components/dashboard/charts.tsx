import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  Legend,
  Line,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
const tooltipStyle = {
  borderRadius: 8,
  border: "1px solid var(--border)",
  background: "var(--popover)",
  color: "var(--popover-foreground)",
  boxShadow: "0 12px 28px oklch(.18 .065 280 / 12%)",
};
const colors = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
];
export function TrendChart({
  data,
}: {
  data: { date: string; transactions: number; anomalies: number }[];
}) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <ComposedChart data={data} margin={{ left: -18, right: 8, top: 12 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
        <XAxis dataKey="date" tickLine={false} axisLine={false} fontSize={11} />
        <YAxis tickLine={false} axisLine={false} fontSize={11} />
        <Tooltip contentStyle={tooltipStyle} />
        <Legend iconType="circle" iconSize={7} />
        <Line
          type="monotone"
          dataKey="transactions"
          name="Transaction volume"
          stroke="var(--chart-1)"
          strokeWidth={3}
          dot={false}
        />
        <Line
          type="monotone"
          dataKey="anomalies"
          name="Anomaly signals"
          stroke="var(--chart-4)"
          strokeWidth={2}
          dot={false}
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
export function HorizontalRateChart({ data }: { data: { name: string; rate: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} layout="vertical" margin={{ left: 16, right: 18 }}>
        <CartesianGrid horizontal={false} stroke="var(--border)" />
        <XAxis type="number" unit="%" tickLine={false} axisLine={false} fontSize={10} />
        <YAxis
          dataKey="name"
          type="category"
          width={105}
          tickLine={false}
          axisLine={false}
          fontSize={10}
        />
        <Tooltip contentStyle={tooltipStyle} formatter={(v) => [`${v}%`, "Anomaly rate"]} />
        <Bar dataKey="rate" fill="var(--chart-1)" radius={[0, 4, 4, 0]} barSize={11} />
      </BarChart>
    </ResponsiveContainer>
  );
}
export function CountBarChart({ data }: { data: { name: string; count: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} margin={{ left: -12, right: 8, bottom: 35 }}>
        <CartesianGrid vertical={false} stroke="var(--border)" />
        <XAxis
          dataKey="name"
          angle={-24}
          textAnchor="end"
          interval={0}
          tickLine={false}
          axisLine={false}
          fontSize={9}
        />
        <YAxis tickLine={false} axisLine={false} fontSize={10} />
        <Tooltip contentStyle={tooltipStyle} />
        <Bar dataKey="count" name="Anomaly count" fill="var(--chart-2)" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
export function DonutChart({
  data,
  centerLabel,
  centerValue,
}: {
  data: { name: string; value: number }[];
  centerLabel: string;
  centerValue: string;
}) {
  return (
    <div className="relative">
      <ResponsiveContainer width="100%" height={245}>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            innerRadius={62}
            outerRadius={88}
            paddingAngle={2}
          >
            {data.map((_, i) => (
              <Cell key={i} fill={colors[i % colors.length]} />
            ))}
          </Pie>
          <Tooltip contentStyle={tooltipStyle} />
          <Legend iconType="circle" iconSize={7} />
        </PieChart>
      </ResponsiveContainer>
      <div className="pointer-events-none absolute left-1/2 top-[98px] -translate-x-1/2 text-center">
        <div className="font-display text-xl font-bold">{centerValue}</div>
        <div className="text-[10px] text-muted-foreground">{centerLabel}</div>
      </div>
    </div>
  );
}
export function StackedRiskChart({
  data,
}: {
  data: { name: string; high: number; critical: number }[];
}) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} margin={{ left: -20, right: 8 }}>
        <CartesianGrid vertical={false} stroke="var(--border)" />
        <XAxis dataKey="name" tickLine={false} axisLine={false} fontSize={10} />
        <YAxis tickLine={false} axisLine={false} fontSize={10} />
        <Tooltip contentStyle={tooltipStyle} />
        <Legend iconType="circle" iconSize={7} />
        <Bar
          dataKey="high"
          name="High"
          stackId="risk"
          fill="var(--chart-3)"
          radius={[0, 0, 0, 0]}
        />
        <Bar
          dataKey="critical"
          name="Critical"
          stackId="risk"
          fill="var(--chart-4)"
          radius={[4, 4, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}
export function SimpleBarChart({
  data,
  dataKey = "count",
  unit,
}: {
  data: { name: string; [key: string]: string | number }[];
  dataKey?: string;
  unit?: string;
}) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} margin={{ left: -15, right: 8 }}>
        <CartesianGrid vertical={false} stroke="var(--border)" />
        <XAxis dataKey="name" tickLine={false} axisLine={false} fontSize={10} />
        <YAxis
          tickLine={false}
          axisLine={false}
          fontSize={10}
          {...(unit !== undefined ? { unit } : {})}
        />
        <Tooltip contentStyle={tooltipStyle} />
        <Bar dataKey={dataKey} fill="var(--chart-1)" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
