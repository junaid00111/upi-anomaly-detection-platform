import pandas as pd
import numpy as np
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "data/processed/upi_anomaly_results.csv"
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "eda_dashboard.html"

# Modern Color Palette
COLOR_NORMAL = "#2b5c8f"
COLOR_ANOMALY = "#e74c3c"
COLOR_BAR = "#3498db"
COLOR_GRID = "#eef2f5"

# ============================================================
# LOAD & PREPARE DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Clean numeric anomaly fields
anomaly_cols = ["iqr_anomaly", "isolation_forest_anomaly", "time_series_anomaly", "anomaly_count"]
for col in anomaly_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df["is_anomaly"] = (df["anomaly_count"] > 0).astype(int)
df["transaction_hour"] = df["timestamp"].dt.hour
df["day_name"] = df["timestamp"].dt.day_name()

day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Calculate rolling 24h count per sender
df = df.sort_values("timestamp").reset_index(drop=True)
df["sender_24h_count"] = 0
for _, group in df.groupby("sender_upi_id"):
    indices = group.index.to_numpy()
    timestamps = group["timestamp"].astype("int64").to_numpy()
    for i, idx in enumerate(indices):
        current_time = timestamps[i]
        prev_24h = current_time - 24 * 60 * 60 * 1_000_000_000
        left = np.searchsorted(timestamps, prev_24h, side="left")
        df.loc[idx, "sender_24h_count"] = i - left + 1

# Metrics
total_transactions = len(df)
total_value = df["amount_inr"].sum()
total_anomalies = int(df["is_anomaly"].sum())
anomaly_rate = (total_anomalies / total_transactions * 100) if total_transactions > 0 else 0
average_amount = df["amount_inr"].mean()

print("\n==============================================")
print("          UPI TRANSACTION ANALYTICS           ")
print("==============================================")
print(f"Total Transactions      : {total_transactions:,}")
print(f"Total Transaction Value : ₹{total_value:,.2f}")
print(f"Average Transaction     : ₹{average_amount:,.2f}")
print(f"Anomalous Transactions  : {total_anomalies:,}")
print(f"Overall Anomaly Rate    : {anomaly_rate:.2f}%")
print("\nBuilding clean HTML dashboard layout...")

# ============================================================
# CREATE SUBPLOTS
# ============================================================

fig = make_subplots(
    rows=6,
    cols=2,
    specs=[
        [{"type": "xy"}, {"type": "xy"}],
        [{"type": "xy"}, {"type": "xy"}],
        [{"type": "xy"}, {"type": "xy"}],
        [{"type": "xy"}, {"type": "xy"}],
        [{"type": "xy"}, {"type": "xy"}],
        [{"type": "heatmap", "colspan": 2}, None],
    ],
    subplot_titles=[
        "1. Amount Distribution by Anomaly Status",
        "2. Anomaly Rate by Hour of Day",
        "3. Anomaly Rate by UPI App",
        "4. Anomaly Rate by Transaction Category",
        "5. Anomaly Rate by Device OS",
        "6. Top 15 States by Anomaly Rate",
        "7. Anomaly Rate by Amount Category",
        "8. Transaction Velocity vs Amount (Sampled)",
        "9. Detections by Method",
        "10. Distribution of Anomaly Signals",
        "11. Hour × Day Anomaly Heatmap (%)"
    ],
    vertical_spacing=0.08,
    horizontal_spacing=0.09
)

# ------------------------------------------------------------
# 1. Amount Box Plot
# ------------------------------------------------------------
fig.add_trace(
    go.Box(
        y=df.loc[df["is_anomaly"] == 0, "amount_inr"],
        name="Normal",
        boxmean=True,
        marker_color=COLOR_NORMAL,
        hovertemplate="Amount: ₹%{y:,.2f}<extra>Normal</extra>"
    ),
    row=1, col=1
)
fig.add_trace(
    go.Box(
        y=df.loc[df["is_anomaly"] == 1, "amount_inr"],
        name="Anomalous",
        boxmean=True,
        marker_color=COLOR_ANOMALY,
        hovertemplate="Amount: ₹%{y:,.2f}<extra>Anomalous</extra>"
    ),
    row=1, col=1
)

# ------------------------------------------------------------
# 2. Hourly Anomaly Rate
# ------------------------------------------------------------
hour_stats = (
    df.groupby("transaction_hour")
    .agg(transactions=("transaction_id", "count"), anomalies=("is_anomaly", "sum"))
    .reindex(range(24), fill_value=0)
)
hour_stats["anomaly_rate"] = (hour_stats["anomalies"] / hour_stats["transactions"].replace(0, 1)) * 100

fig.add_trace(
    go.Bar(
        x=hour_stats.index,
        y=hour_stats["anomaly_rate"],
        text=[f"{x:.1f}%" for x in hour_stats["anomaly_rate"]],
        textposition="outside",
        marker_color=COLOR_BAR,
        showlegend=False,
        customdata=np.column_stack([hour_stats["transactions"], hour_stats["anomalies"]]),
        hovertemplate="<b>Hour %{x}:00</b><br>Total: %{customdata[0]:,}<br>Anomalies: %{customdata[1]:,}<br>Rate: %{y:.2f}%<extra></extra>"
    ),
    row=1, col=2
)

# ------------------------------------------------------------
# 3. UPI App
# ------------------------------------------------------------
app_stats = (
    df.groupby("upi_app")
    .agg(transactions=("transaction_id", "count"), anomalies=("is_anomaly", "sum"))
)
app_stats["anomaly_rate"] = (app_stats["anomalies"] / app_stats["transactions"]) * 100
app_stats = app_stats.sort_values("anomaly_rate", ascending=False)

fig.add_trace(
    go.Bar(
        x=app_stats.index,
        y=app_stats["anomaly_rate"],
        text=[f"{x:.1f}%" for x in app_stats["anomaly_rate"]],
        textposition="outside",
        marker_color=COLOR_BAR,
        showlegend=False,
        customdata=np.column_stack([app_stats["transactions"], app_stats["anomalies"]]),
        hovertemplate="<b>%{x}</b><br>Total: %{customdata[0]:,}<br>Anomalies: %{customdata[1]:,}<br>Rate: %{y:.2f}%<extra></extra>"
    ),
    row=2, col=1
)

# ------------------------------------------------------------
# 4. Category
# ------------------------------------------------------------
cat_stats = (
    df.groupby("category")
    .agg(transactions=("transaction_id", "count"), anomalies=("is_anomaly", "sum"))
)
cat_stats["anomaly_rate"] = (cat_stats["anomalies"] / cat_stats["transactions"]) * 100
cat_stats = cat_stats.sort_values("anomaly_rate", ascending=False)

fig.add_trace(
    go.Bar(
        x=cat_stats.index,
        y=cat_stats["anomaly_rate"],
        text=[f"{x:.1f}%" for x in cat_stats["anomaly_rate"]],
        textposition="outside",
        marker_color=COLOR_BAR,
        showlegend=False,
        customdata=np.column_stack([cat_stats["transactions"], cat_stats["anomalies"]]),
        hovertemplate="<b>%{x}</b><br>Total: %{customdata[0]:,}<br>Anomalies: %{customdata[1]:,}<br>Rate: %{y:.2f}%<extra></extra>"
    ),
    row=2, col=2
)

# ------------------------------------------------------------
# 5. Device OS
# ------------------------------------------------------------
os_stats = (
    df.groupby("device_os")
    .agg(transactions=("transaction_id", "count"), anomalies=("is_anomaly", "sum"))
)
os_stats["anomaly_rate"] = (os_stats["anomalies"] / os_stats["transactions"]) * 100
os_stats = os_stats.sort_values("anomaly_rate", ascending=False)

fig.add_trace(
    go.Bar(
        x=os_stats.index,
        y=os_stats["anomaly_rate"],
        text=[f"{x:.1f}%" for x in os_stats["anomaly_rate"]],
        textposition="outside",
        marker_color=COLOR_BAR,
        showlegend=False,
        customdata=np.column_stack([os_stats["transactions"], os_stats["anomalies"]]),
        hovertemplate="<b>%{x}</b><br>Total: %{customdata[0]:,}<br>Anomalies: %{customdata[1]:,}<br>Rate: %{y:.2f}%<extra></extra>"
    ),
    row=3, col=1
)

# ------------------------------------------------------------
# 6. State Anomaly Rate
# ------------------------------------------------------------
state_stats = (
    df.groupby("location_state")
    .agg(transactions=("transaction_id", "count"), anomalies=("is_anomaly", "sum"))
)
state_stats["anomaly_rate"] = (state_stats["anomalies"] / state_stats["transactions"]) * 100
state_stats = state_stats[state_stats["transactions"] >= 50].sort_values("anomaly_rate", ascending=True).tail(15)

fig.add_trace(
    go.Bar(
        x=state_stats["anomaly_rate"],
        y=state_stats.index,
        orientation="h",
        text=[f"{x:.1f}%" for x in state_stats["anomaly_rate"]],
        textposition="outside",
        marker_color=COLOR_BAR,
        showlegend=False,
        customdata=np.column_stack([state_stats["transactions"], state_stats["anomalies"]]),
        hovertemplate="<b>%{y}</b><br>Total: %{customdata[0]:,}<br>Anomalies: %{customdata[1]:,}<br>Rate: %{x:.2f}%<extra></extra>"
    ),
    row=3, col=2
)

# ------------------------------------------------------------
# 7. Amount Category
# ------------------------------------------------------------
amount_order = ["Micro", "Low", "Medium", "High", "Very High"]
amount_stats = (
    df.groupby("amount_category")
    .agg(transactions=("transaction_id", "count"), anomalies=("is_anomaly", "sum"))
)
amount_stats["anomaly_rate"] = (amount_stats["anomalies"] / amount_stats["transactions"]) * 100
amount_stats = amount_stats.reindex([c for c in amount_order if c in amount_stats.index])

fig.add_trace(
    go.Bar(
        x=amount_stats.index,
        y=amount_stats["anomaly_rate"],
        text=[f"{x:.1f}%" for x in amount_stats["anomaly_rate"]],
        textposition="outside",
        marker_color=COLOR_BAR,
        showlegend=False,
        customdata=np.column_stack([amount_stats["transactions"], amount_stats["anomalies"]]),
        hovertemplate="<b>%{x}</b><br>Total: %{customdata[0]:,}<br>Anomalies: %{customdata[1]:,}<br>Rate: %{y:.2f}%<extra></extra>"
    ),
    row=4, col=1
)

# ------------------------------------------------------------
# 8. Velocity vs Amount
# ------------------------------------------------------------
plot_df = df.sample(min(5000, len(df)), random_state=42)
norm_plot = plot_df[plot_df["is_anomaly"] == 0]
anom_plot = plot_df[plot_df["is_anomaly"] == 1]

fig.add_trace(
    go.Scatter(
        x=norm_plot["sender_24h_count"],
        y=norm_plot["amount_inr"],
        mode="markers",
        name="Normal (Scatter)",
        showlegend=False,
        marker=dict(size=5, opacity=0.35, color=COLOR_NORMAL),
        hovertemplate="24h Count: %{x}<br>Amount: ₹%{y:,.2f}<extra>Normal</extra>"
    ),
    row=4, col=2
)
fig.add_trace(
    go.Scatter(
        x=anom_plot["sender_24h_count"],
        y=anom_plot["amount_inr"],
        mode="markers",
        name="Anomalous (Scatter)",
        showlegend=False,
        marker=dict(size=6, opacity=0.75, color=COLOR_ANOMALY),
        hovertemplate="24h Count: %{x}<br>Amount: ₹%{y:,.2f}<extra>Anomalous</extra>"
    ),
    row=4, col=2
)

# ------------------------------------------------------------
# 9. Detection Methods
# ------------------------------------------------------------
method_names = ["IQR", "Isolation Forest", "Time-Series"]
method_values = [
    df["iqr_anomaly"].sum(),
    df["isolation_forest_anomaly"].sum(),
    df["time_series_anomaly"].sum()
]

fig.add_trace(
    go.Bar(
        x=method_names,
        y=method_values,
        text=[f"{int(x):,}" for x in method_values],
        textposition="outside",
        marker_color=COLOR_BAR,
        showlegend=False,
        hovertemplate="<b>%{x}</b><br>Flagged: %{y:,}<extra></extra>"
    ),
    row=5, col=1
)

# ------------------------------------------------------------
# 10. Signals Count Distribution
# ------------------------------------------------------------
anomaly_dist = df["anomaly_count"].value_counts().sort_index()

fig.add_trace(
    go.Bar(
        x=[f"{int(i)} signals" if i > 0 else "0 (Normal)" for i in anomaly_dist.index],
        y=anomaly_dist.values,
        text=[f"{x:,}" for x in anomaly_dist.values],
        textposition="outside",
        marker_color=COLOR_BAR,
        showlegend=False,
        hovertemplate="<b>%{x}</b><br>Count: %{y:,}<extra></extra>"
    ),
    row=5, col=2
)

# ------------------------------------------------------------
# 11. Hour x Day Heatmap
# ------------------------------------------------------------
heatmap_data = (
    df.pivot_table(
        index="day_name",
        columns="transaction_hour",
        values="is_anomaly",
        aggfunc="mean"
    )
    .reindex(day_order)
    .fillna(0) * 100
)

fig.add_trace(
    go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale="Viridis",
        colorbar=dict(
            title="Anomaly Rate (%)",
            len=0.12,
            y=0.065,
            yanchor="middle"
        ),
        hovertemplate="<b>%{y}</b>, %{x}:00<br>Rate: %{z:.2f}%<extra></extra>"
    ),
    row=6, col=1
)

# ============================================================
# LAYOUT & STYLING
# ============================================================

fig.update_layout(
    height=2700,
    template="plotly_white",
    paper_bgcolor="#ffffff",
    plot_bgcolor="#ffffff",
    font=dict(family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, sans-serif", size=12, color="#2c3e50"),
    margin=dict(l=60, r=60, t=50, b=50),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.01,
        xanchor="center",
        x=0.5
    )
)

# Format Subplot Titles
for annotation in fig["layout"]["annotations"]:
    annotation["font"] = dict(size=14, color="#1a252f")

# Axes formatting
fig.update_xaxes(showgrid=False, linecolor="#dbe2e8")
fig.update_yaxes(gridcolor=COLOR_GRID, linecolor="#dbe2e8")

# Specific axes titles & ranges
fig.update_xaxes(tickmode="linear", dtick=2, title_text="Hour of Day", row=1, col=2)
fig.update_yaxes(title_text="Amount (INR)", row=1, col=1)
fig.update_yaxes(title_text="Anomaly Rate (%)", row=1, col=2)

fig.update_yaxes(title_text="Anomaly Rate (%)", row=2, col=1)
fig.update_yaxes(title_text="Anomaly Rate (%)", row=2, col=2)

fig.update_yaxes(title_text="Anomaly Rate (%)", row=3, col=1)
fig.update_xaxes(title_text="Anomaly Rate (%)", row=3, col=2)

fig.update_yaxes(title_text="Anomaly Rate (%)", row=4, col=1)
fig.update_xaxes(title_text="24h Transaction Velocity", row=4, col=2)
fig.update_yaxes(title_text="Amount (INR)", row=4, col=2)

fig.update_yaxes(title_text="Flagged Count", row=5, col=1)
fig.update_yaxes(title_text="Transaction Count", row=5, col=2)

fig.update_xaxes(tickmode="linear", dtick=1, title_text="Hour of Day", row=6, col=1)
fig.update_yaxes(title_text="Day of Week", row=6, col=1)

# ============================================================
# EXPORT STANDALONE HTML WITH NATIVE RESPONSIVE HEADER & KPIS
# ============================================================

plotly_div = fig.to_html(include_plotlyjs="cdn", full_html=False)

html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UPI Transaction Analytics & Anomaly Dashboard</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            background-color: #f4f7fa;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            color: #2c3e50;
            padding: 24px 20px;
        }}
        .dashboard-container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 24px;
        }}
        .header h1 {{
            font-size: 28px;
            font-weight: 700;
            color: #1e293b;
            letter-spacing: -0.5px;
            margin-bottom: 6px;
        }}
        .header p {{
            font-size: 15px;
            color: #64748b;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .kpi-card {{
            background: #ffffff;
            border-radius: 10px;
            padding: 18px 20px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            text-align: center;
        }}
        .kpi-title {{
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: #64748b;
            margin-bottom: 8px;
        }}
        .kpi-value {{
            font-size: 24px;
            font-weight: 700;
            color: #0f172a;
        }}
        .kpi-subtext {{
            font-size: 11px;
            color: #94a3b8;
            margin-top: 4px;
        }}
        .charts-container {{
            background: #ffffff;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
            padding: 16px;
            overflow: hidden;
        }}
        .footer {{
            text-align: center;
            margin-top: 24px;
            font-size: 13px;
            color: #64748b;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="header">
            <h1>UPI TRANSACTION ANALYTICS</h1>
            <p>Anomaly Detection & Risk Exploration Dashboard</p>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Total Transactions</div>
                <div class="kpi-value">{total_transactions:,}</div>
                <div class="kpi-subtext">Processed Records</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Total Volume</div>
                <div class="kpi-value">₹{total_value / 1_000_000:.2f}M</div>
                <div class="kpi-subtext">INR Value</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Average Amount</div>
                <div class="kpi-value">₹{average_amount:,.2f}</div>
                <div class="kpi-subtext">Per Transaction</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Total Anomalies</div>
                <div class="kpi-value" style="color: #e74c3c;">{total_anomalies:,}</div>
                <div class="kpi-subtext">Flagged Cases</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Anomaly Rate</div>
                <div class="kpi-value" style="color: #e74c3c;">{anomaly_rate:.2f}%</div>
                <div class="kpi-subtext">Of Total Transactions</div>
            </div>
        </div>

        <div class="charts-container">
            {plotly_div}
        </div>

        <div class="footer">
            <p><strong>UPI Transaction Anomaly Detection</strong> • IQR + Isolation Forest + Time-Series Analysis</p>
            <p style="font-size: 12px; color: #94a3b8;">Anomaly signals represent statistical outliers and behavioral risk indicators, not confirmed fraud.</p>
        </div>
    </div>
</body>
</html>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_template)

print("==============================================")
print("       DASHBOARD CREATED SUCCESSFULLY         ")
print("==============================================")
print(f"Dashboard saved at: {OUTPUT_FILE}")
print("Open this file in your browser to view the clean, aligned dashboard.")
