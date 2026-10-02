# RiskGuard Dashboard

Build a portfolio-ready web dashboard for my project "UPI Transaction Anomaly Detection & Fraud Risk Monitoring System".

IMPORTANT: This is anomaly/risk monitoring, NOT confirmed fraud classification. Never label anomaly transactions as confirmed fraud and never invent fraud labels, model accuracy, probabilities, or real-time claims that the dataset does not support.

Use a polished modern fintech/SaaS design inspired by the uploaded reference project's dashboard style: dark navy/purple gradient shell, glass/white cards, rounded corners, subtle shadows, left sidebar navigation, top header, responsive layout, professional charts and tables. Do NOT copy its fraudulent metrics or wording; use our project's actual metrics and terminology.

Build these sections/pages:
1. Dashboard / Executive Overview
2. Transactions
3. Analytics
4. ML Models
5. Risk & Investigation
6. Alerts
7. Settings

Use React + TypeScript + Tailwind + shadcn/ui and a chart library such as Recharts.

Use these actual project metrics as the initial dashboard data:
- Total transactions: 10,000
- Total transaction value: ₹37.85M
- Average transaction amount: ₹3,784.88
- Overall anomaly rate: 18.86%
- Investigation required: 68
- High risk: 64
- Critical risk: 4
- Average risk score: 5.03
- IQR anomalies: 1,004
- Original Isolation Forest anomalies: 500
- Time-series anomalies: 659
- New Isolation Forest anomalies: 500
- LOF anomalies: 500
- One-Class SVM anomalies: 504
- All 3 ML models agree: 146
- 2+ ML models agree: 409

Dashboard visuals:
- KPI cards for total transactions, transaction value, average amount, anomaly rate, investigation required
- daily transaction volume line chart
- risk-level donut chart: Low 9,541; Medium 391; High 64; Critical 4
- anomaly rate by UPI app
- anomaly rate by transaction category
- detection method comparison
- ML model agreement distribution
- risk signal distribution
- high/critical risk by category

Use these known category anomaly rates:
Peer Transfer 30.45%, Shopping 27.76%, Healthcare 10.64%, Health & Fitness 9.13%, Entertainment 9.09%, Transportation 8.34%, Groceries 8.01%, Fuel 7.17%, Food & Dining 6.97%, Bills & Utilities 6.26%.

Use these known UPI-app anomaly rates:
PhonePe 19.56%, CRED 19.01%, Google Pay 18.89%, BHIM 18.46%, Paytm 18.13%, Axis Pay 17.51%, Amazon Pay 15.03%, WhatsApp Pay 14.92%.

Risk & Investigation page:
- KPI cards above
- investigation table filtered by High/Critical by default
- columns: transaction_id, amount_inr, risk_score, risk_level, risk_signal_count, anomaly_type, category, location_state
- sort highest risk first
- use realistic transaction IDs and amounts from the project data only if supplied later; for now use clearly marked sample rows or leave table populated from a local data adapter.
- add filters for date, state, UPI app, transaction type, risk level, category.

Transactions page:
- searchable/filterable transaction table
- risk-level badges
- anomaly signal count
- amount and timestamp
- transaction detail drawer/modal when clicked.

ML Models page:
- comparison cards/charts for IQR, Isolation Forest, Time Series, LOF, One-Class SVM
- show anomaly counts, not accuracy
- show model agreement distribution
- clearly explain contamination/threshold assumptions where relevant.

Alerts page:
- show High/Critical investigation candidates
- severity badges
- anomaly signal count
- allow filtering by severity
- label alerts as "risk/anomaly alerts", not confirmed fraud alerts.

Analytics page:
- daily/weekly/monthly transaction volume
- anomaly trends
- amount distribution
- category/app/state analysis
- interactive filters.

Settings page:
- sensitivity thresholds represented as configurable UI values: Low 80, Medium 60, High 30
- explain these are project-defined risk thresholds, not calibrated fraud probabilities.

Add a persistent disclaimer in the footer or dashboard:
"Anomaly signals indicate unusual transaction behavior and do not represent confirmed fraud."

Architecture should be ready for a future FastAPI backend. Create a clean API/data service abstraction so static demo data can later be replaced by endpoints without rewriting components. Do not add a fake backend or fake real-time metrics. Add a small "Data source: Demo dataset | Jan–Jun 2024" indicator.

Make the app visually impressive and portfolio-ready, with responsive sidebar, active navigation, tooltips, hover states, loading/empty states, accessible contrast, and clean typography.

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/0de5387b-b99a-4d1a-a70d-b5db632403c9).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
