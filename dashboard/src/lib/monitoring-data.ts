export type RiskLevel = "Low" | "Medium" | "High" | "Critical";
export type DemoTransaction = {
  transactionId: string;
  amount: number;
  riskScore: number;
  riskLevel: RiskLevel;
  signalCount: number;
  anomalyType: string;
  category: string;
  state: string;
  app: string;
  transactionType: string;
  timestamp: string;
};

export const projectMetrics = {
  totalTransactions: 10000,
  totalValue: 37850000,
  averageAmount: 3784.88,
  anomalyRate: 18.86,
  investigationRequired: 68,
  highRisk: 64,
  criticalRisk: 4,
  averageRiskScore: 5.03,
};
const categoryRateEntries: Array<[string, number]> = [
  ["Peer Transfer", 30.45],
  ["Shopping", 27.76],
  ["Healthcare", 10.64],
  ["Health & Fitness", 9.13],
  ["Entertainment", 9.09],
  ["Transportation", 8.34],
  ["Groceries", 8.01],
  ["Fuel", 7.17],
  ["Food & Dining", 6.97],
  ["Bills & Utilities", 6.26],
];

export const categoryRates: Array<{ name: string; rate: number }> = categoryRateEntries.map(
  ([name, rate]) => ({ name, rate }),
);

const appRateEntries: Array<[string, number]> = [
  ["PhonePe", 19.56],
  ["CRED", 19.01],
  ["Google Pay", 18.89],
  ["BHIM", 18.46],
  ["Paytm", 18.13],
  ["Axis Pay", 17.51],
  ["Amazon Pay", 15.03],
  ["WhatsApp Pay", 14.92],
];

export const appRates: Array<{ name: string; rate: number }> = appRateEntries.map(
  ([name, rate]) => ({ name, rate }),
);

export const riskLevels = [
  { name: "Low", value: 9541 },
  { name: "Medium", value: 391 },
  { name: "High", value: 64 },
  { name: "Critical", value: 4 },
];
export const detectionMethods = [
  { name: "IQR", count: 1004 },
  { name: "Isolation Forest (original)", count: 500 },
  { name: "Time Series", count: 659 },
  { name: "Isolation Forest (new)", count: 500 },
  { name: "LOF", count: 500 },
  { name: "One-Class SVM", count: 504 },
];
export const modelAgreement = [
  { name: "All 3 agree", value: 146 },
  { name: "2+ agree", value: 409 },
  { name: "Other model outcomes", value: 9451 },
];
export const dailyVolume = [
  { date: "Jan 08", transactions: 148, anomalies: 25 },
  { date: "Jan 29", transactions: 311, anomalies: 56 },
  { date: "Feb 19", transactions: 425, anomalies: 73 },
  { date: "Mar 11", transactions: 552, anomalies: 98 },
  { date: "Apr 01", transactions: 488, anomalies: 91 },
  { date: "Apr 22", transactions: 640, anomalies: 122 },
  { date: "May 13", transactions: 725, anomalies: 139 },
  { date: "Jun 03", transactions: 612, anomalies: 110 },
  { date: "Jun 24", transactions: 804, anomalies: 154 },
];
export const weeklyVolume = dailyVolume.map((d, i) => ({
  ...d,
  date: `W${i + 1}`,
  transactions: d.transactions * 5,
  anomalies: d.anomalies * 5,
}));
export const monthlyVolume = [
  { date: "Jan", transactions: 1320, anomalies: 231 },
  { date: "Feb", transactions: 1505, anomalies: 273 },
  { date: "Mar", transactions: 1688, anomalies: 311 },
  { date: "Apr", transactions: 1762, anomalies: 326 },
  { date: "May", transactions: 1845, anomalies: 350 },
  { date: "Jun", transactions: 1880, anomalies: 395 },
];
export const amountBands = [
  { name: "< ₹500", count: 2170 },
  { name: "₹500–1K", count: 1940 },
  { name: "₹1K–3K", count: 2460 },
  { name: "₹3K–5K", count: 1430 },
  { name: "₹5K–10K", count: 1250 },
  { name: "₹10K+", count: 750 },
];
export const stateAnalysis = [
  { name: "Maharashtra", transactions: 1850, rate: 19.4 },
  { name: "Karnataka", transactions: 1520, rate: 18.7 },
  { name: "Delhi", transactions: 1340, rate: 20.1 },
  { name: "Tamil Nadu", transactions: 1270, rate: 17.9 },
  { name: "Uttar Pradesh", transactions: 1160, rate: 18.4 },
  { name: "Other", transactions: 2860, rate: 18.5 },
];
export const signalDistribution = [
  { name: "1 signal", value: 1080 },
  { name: "2 signals", value: 390 },
  { name: "3 signals", value: 146 },
  { name: "4+ signals", value: 68 },
];
export const highRiskCategories = [
  { name: "Peer Transfer", high: 21, critical: 2 },
  { name: "Shopping", high: 17, critical: 1 },
  { name: "Healthcare", high: 8, critical: 0 },
  { name: "Transportation", high: 7, critical: 1 },
  { name: "Other", high: 11, critical: 0 },
];
export const sampleTransactions: DemoTransaction[] = [
  {
    transactionId: "SAMPLE-UPI-0047",
    amount: 48620,
    riskScore: 96,
    riskLevel: "Critical",
    signalCount: 5,
    anomalyType: "Multi-signal outlier",
    category: "Peer Transfer",
    state: "Maharashtra",
    app: "PhonePe",
    transactionType: "P2P",
    timestamp: "2024-06-28 22:14",
  },
  {
    transactionId: "SAMPLE-UPI-0182",
    amount: 32750,
    riskScore: 91,
    riskLevel: "Critical",
    signalCount: 4,
    anomalyType: "Amount + time-series",
    category: "Shopping",
    state: "Delhi",
    app: "Google Pay",
    transactionType: "P2M",
    timestamp: "2024-06-26 01:08",
  },
  {
    transactionId: "SAMPLE-UPI-0316",
    amount: 18490,
    riskScore: 84,
    riskLevel: "High",
    signalCount: 4,
    anomalyType: "ML model agreement",
    category: "Peer Transfer",
    state: "Karnataka",
    app: "CRED",
    transactionType: "P2P",
    timestamp: "2024-06-22 23:41",
  },
  {
    transactionId: "SAMPLE-UPI-0449",
    amount: 12680,
    riskScore: 78,
    riskLevel: "High",
    signalCount: 3,
    anomalyType: "Local density outlier",
    category: "Transportation",
    state: "Tamil Nadu",
    app: "Paytm",
    transactionType: "P2M",
    timestamp: "2024-06-18 18:27",
  },
  {
    transactionId: "SAMPLE-UPI-0581",
    amount: 8750,
    riskScore: 73,
    riskLevel: "High",
    signalCount: 3,
    anomalyType: "Time-series deviation",
    category: "Healthcare",
    state: "Uttar Pradesh",
    app: "BHIM",
    transactionType: "P2M",
    timestamp: "2024-06-14 09:52",
  },
  {
    transactionId: "SAMPLE-UPI-0724",
    amount: 4200,
    riskScore: 57,
    riskLevel: "Medium",
    signalCount: 2,
    anomalyType: "IQR amount outlier",
    category: "Entertainment",
    state: "Maharashtra",
    app: "Amazon Pay",
    transactionType: "P2M",
    timestamp: "2024-06-09 20:11",
  },
  {
    transactionId: "SAMPLE-UPI-0890",
    amount: 1260,
    riskScore: 18,
    riskLevel: "Low",
    signalCount: 0,
    anomalyType: "No active signal",
    category: "Groceries",
    state: "Karnataka",
    app: "WhatsApp Pay",
    transactionType: "P2M",
    timestamp: "2024-06-03 17:36",
  },
];
export const monitoringSnapshot = {
  projectMetrics,
  categoryRates,
  appRates,
  riskLevels,
  detectionMethods,
  modelAgreement,
  dailyVolume,
  weeklyVolume,
  monthlyVolume,
  amountBands,
  stateAnalysis,
  signalDistribution,
  highRiskCategories,
  sampleTransactions,
};
export type MonitoringSnapshot = typeof monitoringSnapshot;
export interface MonitoringDataService {
  getSnapshot(): Promise<MonitoringSnapshot>;
}
class DemoMonitoringDataService implements MonitoringDataService {
  async getSnapshot() {
    return structuredClone(monitoringSnapshot);
  }
}
export const monitoringDataService: MonitoringDataService = new DemoMonitoringDataService();
