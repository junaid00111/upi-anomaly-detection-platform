# UPI Transaction Anomaly Detection & Risk Monitoring

A portfolio-ready UPI analytics project combining statistical anomaly detection, unsupervised ML, PostgreSQL analytics, a FastAPI backend, and an interactive React/TanStack dashboard.

> **Important:** The dataset does not contain a verified fraud label. The system detects unusual transaction behavior and produces review/risk signals; these signals are not confirmed fraud determinations or calibrated fraud probabilities.

## Project structure

```text
UPI project/
├── data/
│   ├── raw/
│   └── processed/
├── src/                 # ETL, EDA, statistics, anomaly detection, risk scoring
├── api/                 # FastAPI + PostgreSQL API
├── dashboard/           # React + TanStack dashboard
├── .env.example
├── requirements.txt
└── README.md
```

## Detection methods

- IQR amount outlier detection
- Isolation Forest
- Local Outlier Factor (LOF)
- One-Class SVM
- Robust time-series anomaly detection
- Multi-signal risk scoring and sensitivity analysis

## Backend

1. Create PostgreSQL database/table using the SQL setup used by the project.
2. Copy `.env.example` to `.env` and set your PostgreSQL credentials.
3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Start FastAPI:

```bash
uvicorn api.main:app --reload --port 8000
```

## Dashboard

```bash
cd dashboard
npm install
```

Copy `dashboard/.env.example` to `dashboard/.env` if you want to change the API URL.

Start the dashboard:

```bash
npm run dev
```

The Vite development server may choose another free port if its default port is busy.

## Checks

```bash
cd dashboard
npx tsc --noEmit
npm run lint
npm run build
```

## Portfolio notes

The dashboard is designed to communicate anomaly monitoring rather than claim confirmed fraud. Model counts describe flags produced by configured unsupervised methods and should not be interpreted as model accuracy.
