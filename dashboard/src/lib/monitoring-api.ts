import type { MonitoringSnapshot, RiskLevel, DemoTransaction } from "./monitoring-data";

const API_BASE_URL = import.meta.env["VITE_API_BASE_URL"] ?? "http://localhost:8000";

async function fetchApi<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`);

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

// ------------------------------------------------------------
// API RESPONSE TYPES
// ------------------------------------------------------------

type SummaryResponse = {
  total_transactions: number;
  total_value: number;
  average_amount: number;
  anomalous_transactions: number;
  anomaly_rate: number;
  investigation_required: number;
};

type RiskLevelResponse = {
  risk_level: string;
  transaction_count: number;
};

type AnomalyResponse = {
  iqr: number;
  time_series: number;
  isolation_forest: number;
  lof: number;
  one_class_svm: number;
};

type CategoryResponse = {
  category: string;
  total_transactions: number;
  anomalous_transactions: number;
  anomaly_rate: number;
  average_amount: number;
};

type AppResponse = {
  upi_app: string;
  total_transactions: number;
  anomalous_transactions: number;
  anomaly_rate: number;
};

type DailyResponse = {
  transaction_date: string;
  transaction_count: number;
  total_amount: number;
  anomalous_transactions: number;
};

type TransactionResponse = {
  transaction_id: string;
  timestamp: string;
  amount_inr: number;
  risk_score: number;
  risk_level: RiskLevel;
  risk_signal_count: number;
  anomaly_type: string;
  category: string;
  location_state: string;
  upi_app: string;
  transaction_type: string;
};

export type TransactionListResponse = {
  count: number;
  total: number;
  limit: number;
  offset: number;
  transactions: TransactionResponse[];
};

type ModelAgreementResponse = {
  name: string;
  value: number;
};

type SignalDistributionResponse = {
  name: string;
  value: number;
};

type HighRiskCategoryResponse = {
  name: string;
  high: number;
  critical: number;
};
type AmountBandResponse = {
  name: string;
  count: number;
};

type StateResponse = {
  name: string;
  transactions: number;
  rate: number;
};

// ------------------------------------------------------------
// API REQUESTS
// ------------------------------------------------------------

async function getProjectMetrics() {
  return fetchApi<SummaryResponse>("/api/summary");
}

async function getRiskLevels() {
  return fetchApi<RiskLevelResponse[]>("/api/risk-levels");
}

async function getAnomalyMethods() {
  return fetchApi<AnomalyResponse>("/api/anomalies");
}

async function getCategories() {
  return fetchApi<CategoryResponse[]>("/api/analytics/categories");
}

async function getApps() {
  return fetchApi<AppResponse[]>("/api/analytics/apps");
}

async function getDailyData() {
  return fetchApi<DailyResponse[]>("/api/analytics/daily");
}
async function getAmountBands() {
  return fetchApi<AmountBandResponse[]>("/api/analytics/amount-bands");
}

async function getStates() {
  return fetchApi<StateResponse[]>("/api/analytics/states");
}

export type TransactionQuery = {
  limit?: number;
  offset?: number;
  search?: string;
  riskLevel?: string;
  state?: string;
  app?: string;
  category?: string;
};

async function getTransactionSnapshot(): Promise<TransactionListResponse> {
  return fetchApi<TransactionListResponse>("/api/transactions?limit=100");
}

// Public transaction explorer API. Converts the FastAPI response shape into
// the frontend row model used by TransactionTable.
export async function getTransactions(options: TransactionQuery = {}): Promise<{
  total: number;
  transactions: DemoTransaction[];
}> {
  const params = new URLSearchParams();

  params.set("limit", String(options.limit ?? 50));
  params.set("offset", String(options.offset ?? 0));

  if (options.search?.trim()) {
    params.set("search", options.search.trim());
  }

  if (options.riskLevel && options.riskLevel !== "All risks") {
    params.set("risk_level", options.riskLevel);
  }

  if (options.state && options.state !== "All states") {
    params.set("state", options.state);
  }

  if (options.app && options.app !== "All apps") {
    params.set("app", options.app);
  }

  if (options.category && options.category !== "All categories") {
    params.set("category", options.category);
  }

  const response = await fetchApi<TransactionListResponse>(
    `/api/transactions?${params.toString()}`,
  );

  return {
    total: response.total,
    transactions: response.transactions.map((item) => ({
      transactionId: item.transaction_id,
      amount: Number(item.amount_inr),
      riskScore: Number(item.risk_score),
      riskLevel: item.risk_level,
      signalCount: Number(item.risk_signal_count),
      anomalyType: item.anomaly_type,
      category: item.category,
      state: item.location_state,
      app: item.upi_app,
      transactionType: item.transaction_type,
      timestamp: item.timestamp,
    })),
  };
}

// NEW
async function getModelAgreement() {
  return fetchApi<ModelAgreementResponse[]>("/api/analytics/model-agreement");
}

// NEW
async function getSignalDistribution() {
  return fetchApi<SignalDistributionResponse[]>("/api/analytics/signal-distribution");
}

// NEW
async function getHighRiskCategories() {
  return fetchApi<HighRiskCategoryResponse[]>("/api/analytics/high-risk-categories");
}

// ------------------------------------------------------------
// INVESTIGATION QUEUE
// ------------------------------------------------------------

export async function getInvestigations(limit = 100): Promise<DemoTransaction[]> {
  const response = await fetchApi<{
    count: number;
    transactions: TransactionResponse[];
  }>(`/api/investigations?limit=${limit}`);

  return response.transactions.map((item) => ({
    transactionId: item.transaction_id,
    amount: Number(item.amount_inr),
    riskScore: Number(item.risk_score),
    riskLevel: item.risk_level,
    signalCount: Number(item.risk_signal_count),
    anomalyType: item.anomaly_type,
    category: item.category,
    state: item.location_state,
    app: item.upi_app,
    transactionType: item.transaction_type,
    timestamp: item.timestamp,
  }));
}

// ------------------------------------------------------------
// BUILD DASHBOARD SNAPSHOT
// ------------------------------------------------------------

function buildSnapshot(
  summary: SummaryResponse,
  risks: RiskLevelResponse[],
  anomalies: AnomalyResponse,
  categories: CategoryResponse[],
  apps: AppResponse[],
  daily: DailyResponse[],
  amountBands: AmountBandResponse[],
  states: StateResponse[],
  transactions: TransactionListResponse,
  modelAgreement: ModelAgreementResponse[],
  signalDistribution: SignalDistributionResponse[],
  highRiskCategories: HighRiskCategoryResponse[],
): MonitoringSnapshot {
  // ----------------------------------------------------------
  // RISK LEVELS
  // ----------------------------------------------------------

  const riskLevels = risks.map((item) => ({
    name: item.risk_level,
    value: item.transaction_count,
  }));

  // ----------------------------------------------------------
  // CATEGORY RATES
  // ----------------------------------------------------------

  const categoryRates = categories.map((item) => ({
    name: item.category,
    rate: Number(item.anomaly_rate),
  }));

  // ----------------------------------------------------------
  // UPI APP RATES
  // ----------------------------------------------------------

  const appRates = apps.map((item) => ({
    name: item.upi_app,
    rate: Number(item.anomaly_rate),
  }));

  // ----------------------------------------------------------
  // DETECTION METHODS
  // ----------------------------------------------------------

  const detectionMethods = [
    {
      name: "IQR",
      count: anomalies.iqr,
    },
    {
      name: "Time Series",
      count: anomalies.time_series,
    },
    {
      name: "Isolation Forest",
      count: anomalies.isolation_forest,
    },
    {
      name: "LOF",
      count: anomalies.lof,
    },
    {
      name: "One-Class SVM",
      count: anomalies.one_class_svm,
    },
  ];

  // ----------------------------------------------------------
  // DAILY VOLUME
  // ----------------------------------------------------------

  const dailyVolume = daily.map((item) => ({
    date: item.transaction_date,
    transactions: item.transaction_count,
    anomalies: item.anomalous_transactions,
  }));

  // ----------------------------------------------------------
  // TRANSACTIONS
  // ----------------------------------------------------------

  const sampleTransactions: DemoTransaction[] = transactions.transactions.map((item) => ({
    transactionId: item.transaction_id,
    amount: item.amount_inr,
    riskScore: item.risk_score,
    riskLevel: item.risk_level,
    signalCount: item.risk_signal_count,
    anomalyType: item.anomaly_type,
    category: item.category,
    state: item.location_state,
    app: item.upi_app,
    transactionType: item.transaction_type,
    timestamp: item.timestamp,
  }));

  // ----------------------------------------------------------
  // RETURN COMPLETE SNAPSHOT
  // ----------------------------------------------------------

  return {
    projectMetrics: {
      totalTransactions: summary.total_transactions,
      totalValue: summary.total_value,
      averageAmount: summary.average_amount,
      anomalyRate: summary.anomaly_rate,
      investigationRequired: summary.investigation_required,

      highRisk: riskLevels.find((r) => r.name === "High")?.value ?? 0,

      criticalRisk: riskLevels.find((r) => r.name === "Critical")?.value ?? 0,

      averageRiskScore: 0,
    },

    categoryRates,

    appRates,

    riskLevels,

    detectionMethods,

    // REAL
    modelAgreement,

    dailyVolume,

weeklyVolume: [],

monthlyVolume: [],

amountBands,

stateAnalysis: states,

    // REAL
    signalDistribution,

    // REAL
    highRiskCategories,

    sampleTransactions,
  };
}

// ------------------------------------------------------------
// PUBLIC DATA SERVICE
// ------------------------------------------------------------

export const apiMonitoringDataService = {
  async getSnapshot(): Promise<MonitoringSnapshot> {
  const [
  summary,
  risks,
  anomalies,
  categories,
  apps,
  daily,
  amountBands,
  states,
  transactions,

      // NEW
      modelAgreement,
      signalDistribution,
      highRiskCategories,
] = await Promise.all([
  getProjectMetrics(),
  getRiskLevels(),
  getAnomalyMethods(),
  getCategories(),
  getApps(),
  getDailyData(),
  getAmountBands(),
  getStates(),
  getTransactionSnapshot(),

  // NEW
  getModelAgreement(),
  getSignalDistribution(),
  getHighRiskCategories(),
]);

    return buildSnapshot(
      summary,
      risks,
      anomalies,
      categories,
      apps,
      daily,
      amountBands,
      states,
      transactions,

      // NEW
      modelAgreement,
      signalDistribution,
      highRiskCategories,
    );
  },
};
