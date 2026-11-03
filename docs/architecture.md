# UPI Transaction Anomaly Detection & Risk Monitoring Platform — System Design & Architecture

This document describes the system design, architecture, data flow, and deployment model of the UPI Anomaly Detection Platform. It is the companion reference to the README.

---

## 1. System Overview

The platform is an **end-to-end anomaly detection and risk monitoring system** for UPI (Unified Payments Interface) transaction data. It ingests raw transaction data, cleans it, applies multiple unsupervised anomaly-detection techniques, scores each transaction with a risk metric, persists results to PostgreSQL, exposes them through a REST API, and renders them in an interactive web dashboard.

### 1.1 Primary Objectives

1. Detect unusual (anomalous) transaction behavior using statistical and unsupervised ML methods.
2. Produce a human-interpretable **risk score** and **investigation queue**.
3. Store processed results in a queryable analytics database (PostgreSQL).
4. Expose analytics via a clean REST API.
5. Visualize results via a role-friendly interactive dashboard.

### 1.2 Design Tenets

| Tenet | Implementation |
|-------|----------------|
| **Modular pipeline** | Each pipeline stage is an independent, executable script (single-responsibility), orchestrated by a stage runner. |
| **Unsupervised first** | No verified fraud label exists; the system flags anomalies for investigation rather than claiming confirmed fraud. |
| **Stateless API** | FastAPI reads only from PostgreSQL; it holds no in-memory analytics state. |
| **Single source of truth** | PostgreSQL is the system of record; both the API and Power BI read from it. |
| **Developer ergonomics** | All stages run via one command; the dashboard auto-configures its API base URL. |

---

## 2. Overall Architecture

The system follows a **layered, pipeline-shaped architecture** with four logical layers:

```
┌────────────────────────────────────────────────────────────────────────────┐
│                             PRESENTATION LAYER                             │
│  ┌──────────────────────┐      ┌──────────────────────┐                   │
│  │  React + Vite        │      │  Power BI (optional) │                   │
│  │  TanStack Dashboard  │      │  .pbix report        │                   │
│  └──────────┬───────────┘      └──────────┬───────────┘                   │
│             │ HTTP (CORS)                 │ SQL / import                  │
└─────────────┼─────────────────────────────┼───────────────────────────────┘
              │                             │
┌─────────────┼─────────────────────────────┼───────────────────────────────┐
│             ▼                             ▼                               │
│        APPLICATION LAYER            ANALYTICS LAYER                       │
│  ┌──────────────────────┐      ┌──────────────────────┐                  │
│  │  FastAPI / uvicorn   │      │  PostgreSQL 18       │                  │
│  │  REST endpoints      │◄────►│  upi_anomaly_db      │                  │
│  └──────────────────────┘      └──────────────────────┘                  │
└────────────────────────────────────────────────────────────────────────────┘
              ▲
              │  loads csv (??)

┌─────────────┼─────────────────────────────────────────────────────────────┐
│             ▼                                                             │
│        PROCESSING LAYER (Data Pipeline)                                   │
│  ┌──────────────────────┐    ┌──────────────────────┐                    │
│  │  Clean / Transform   │───►│  Detectors:          │                    │
│  │  (transform.py)      │    │  • IQR              │                    │
│  └──────────────────────┘    │  • Isolation Forest  │                    │
│         │                    │  • LOF / One-Class SVM│                    │
│         │                    │  • Time-series       │                    │
│         │                    └──────────┬───────────┘                    │
│         │                               │                                │
│         │                    ┌──────────▼───────────┐                    │
│         │                    │ 1 Anomaly signals    │                    │
│         │                    │ 2 Risk scoring       │                    │
│         │                    │ 3 Validation         │                    │
│         │                    └──────────┬───────────┘                    │
│         │                               │                                │
│         ▼                               ▼                                │
│  ┌──────────────────────┐      ┌──────────────────────┐                  │
│  │  Raw UPI dataset     │      │  Processed outputs   │                  │
│  │  (data/raw/*.csv)    │      │  (data/processed/*)  │                  │
│  └──────────────────────┘      └──────────────────────┘                  │
└────────────────────────────────────────────────────────────────────────────┘
```

**Key architectural decisions:**

- **Pipeline ↔ storage bridge:** The final pipeline stage (`src/load.py`) connects to PostgreSQL and upserts the scored transaction table. This is the only place the pipeline writes to the database.
- **API ↔ storage bridge:** FastAPI connects to the same PostgreSQL database (via `DB_*` env vars) and serves aggregated + transaction-level JSON.
- **Frontend ↔ API bridge:** The dashboard calls the API through a typed client (`monitoring-api.ts`) whose base URL defaults to `http://localhost:8002`.

---

## 3. Data Flow

### 3.1 End-to-end flow

```
 Raw CSV ──► Clean ──► EDA ──► Detect ──► Combine ──► Score ──► Validate ──► Load ──► API ──► Dashboard
            │           │         │            │          │          │         │         │
            │           │         │            │          │          │         │         │
            ▼           ▼         ▼            ▼          ▼          ▼         ▼         ▼
        data/raw    EDA plots   iqr/isof   combined    risk_scores  quality   postgres    JSON
                           (charts)   (csv)    signals      csv       report   upi_  ⇐⇐⇐
                                              (csv)      (csv)      (json)   anomalyy_db
```

### 3.2 Stage inventory

| # | Stage | Script | Input | Output |
|---|-------|--------|-------|--------|
| 1 | Transform & clean | `src/transform.py` | `data/raw/upi_transactions.csv` | `data/processed/upi_cleaned.csv` |
| 2 | IQR anomaly detection | `src/anomaly_detection.py` | cleaned CSV | IQR anomalies |
| 3 | Isolation Forest | `src/isolation_forest.py` | cleaned CSV | isolation-forest anomalies |
| 4 | Time-series detection | `src/time_series.py` | cleaned CSV | time-series anomalies |
| 5 | Combine signals | `src/combine_anomalies.py` | detector outputs | combined anomaly signals |
| 6 | ML model comparison | `src/ml_models.py` | cleaned CSV | LOF / One-Class SVM comparison |
| 7 | Risk scoring | `src/risk_scoring.py` | combined signals | `upi_risk_scores.csv` |
| 8 | Sensitivity analysis | `src/sensitivity_analysis.py` | risk scores | sensitivity reports |
| 9 | Data quality validation | `src/data_quality_check.py` | processed outputs | quality report |
| 10 | PostgreSQL load | `src/load.py` | risk scores | `upi_anomaly_db` table |

The orchestration lives in `src/pipeline.py`, which runs the stages **sequentially** and **halts on first failure** to guarantee a consistent dataset.

---

## 4. Components

### 4.1 Data Generator (`generate_upi_data.py`)
Synthetic UPI transaction dataset (10,000 rows over Jan–Jun 2024) matching real UPI field characteristics. Keeps the project self-contained and reproducible.

### 4.2 Pipeline (`/src`)
Independent, executable Python modules, one per stage (see §3.2). Each reads a CSV/JSON, computes, and writes a derived artifact.

### 4.3 Storage (PostgreSQL)
- Database: `upi_anomaly_db`
- Schema: `sql/schema.sql`
- Contains the scored transaction table with risk columns (amount validity, anomaly flags, risk level, risk score, investigation-required flag, etc.).

### 4.4 API (FastAPI)
- Runs on `http://localhost:8002` via uvicorn.
- Reads config from `.env` via `load_dotenv()`.
- Enables CORS for the dashboard origins.
- Endpoints:
  - `GET /` — service health/summary
  - `GET /api/health` — health check
  - `GET /api/summary` — KPIs (total transactions/value, anomaly rate, investigation queue)
  - `GET /api/risk-levels` — risk distribution
  - `GET /api/transactions` — paginated transaction table
  - (additional analytics endpoints as defined in `api/main.py`)

### 4.5 Dashboard (React + Vite + TanStack)
- `dashboard/src/` — typed API client (`monitoring-api.ts`), routing, pages.
- Routes: overview, transactions, alerts, analytics, ML models, risk/investigation, settings.
- Calls the API at `http://localhost:8002` by default (overridable via `VITE_API_BASE_URL`).

### 4.6 Power BI (optional)
`powerBi analytics.pbix` connects to the PostgreSQL database for ad-hoc reporting without the web UI.

---

## 5. Deployment / Runtime

The reference runtime is Windows + PowerShell (`start-dev.ps1`), which:
1. Runs the pipeline (`python src/pipeline.py`).
2. Starts the backend on 8002.
3. Starts the dashboard dev server on 8080.

Required environment variables (in root `.env`):

| Variable | Purpose |
|----------|---------|
| `DB_HOST` | PostgreSQL host |
| `DB_PORT` | PostgreSQL port (default 5432) |
| `DB_NAME` | Database name (`upi_anomaly_db`) |
| `DB_USER` | DB user |
| `DB_PASSWORD` | DB password |

---

## 6. Monitoring, Security & Non-functional Notes

- **CORS** whitelists only local dev origins.
- **Secrets** are read from `.env`; the file is git-ignored (`.gitignore`), and `.env.example` is intended for template documentation.
- **Deterministic pipeline**: ordering is guaranteed; failure stops downstream stages.
- **Scalability**: the current design is single-node; PostgreSQL is the scaling bottleneck. The API is stateless and could be load-balanced behind a reverse proxy in production.
- **Accuracy model**: unsupervised. Validation is via sensitivity analysis + cross-model agreement rather than precision/recall (no ground-truth labels).

---

## 7. Technology Stack

| Layer | Technology |
|-------|------------|
| Language (pipeline/API) | Python 3.8+ |
| Data manipulation | pandas, numpy |
| Machine learning | scikit-learn (IsolationForest, LOF, OneClassSVM) |
| Statistics | scipy, hypothesis testing (Mann–Whitney U, chi-square) |
| Visualization (static) | matplotlib, seaborn, plotly |
| Database | PostgreSQL 18 |
| API | FastAPI, uvicorn, psycopg2 |
| Frontend | React, Vite, TanStack, TypeScript |
| Version control | Git |

---

## 8. Request/Response Sample (API)

The dashboard requests `GET /api/summary`:

```json
{
  "total_transactions": 10000,
  "total_value": 37850000,
  "average_amount": 3784.88,
  "anomalous_transactions": 1886,
  "anomaly_rate": 0.1886,
  "investigation_required": 68
}
```

The dashboard requests `GET /api/transactions?limit=25&offset=0` for the paginated table.

---

## 9. Recommendations for the Future

1. Add a **real labelled dataset** or a labelled slice for supervised evaluation.
2. Introduce **explainability** (e.g., SHAP) for the ML detectors.
3. Make ingestion **streaming-capable** (Kafka-like) instead of batch-only.
4. Add **alerting/threshold automation** based on risk score bands.
5. Containerize the whole runtime (`docker compose`) for one-command reproducibility.
6. Add CI (GitHub Actions) running pytest + lint + build.
