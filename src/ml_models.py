import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.ensemble import IsolationForest


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "data/processed/upi_anomaly_results.csv"
OUTPUT_FILE = "data/processed/upi_ml_comparison.csv"


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sort chronologically.
# This is VERY important because our historical
# features must only use information available
# before the current transaction.
df = df.sort_values("timestamp").reset_index(drop=True)


print("\n" + "=" * 70)
print("             UPI ML ANOMALY MODEL COMPARISON")
print("=" * 70)

print(f"\nDataset size: {len(df):,} transactions")


# ============================================================
# HISTORICAL FEATURE ENGINEERING
# ============================================================

print("\nCreating historical transaction features...")


# ------------------------------------------------------------
# Sender previous transaction count
# ------------------------------------------------------------

df["sender_previous_count"] = (
    df.groupby("sender_upi_id")
    .cumcount()
)


# ------------------------------------------------------------
# Sender previous total amount
# ------------------------------------------------------------

df["sender_previous_total"] = (
    df.groupby("sender_upi_id")["amount_inr"]
    .transform(
        lambda x:
        x.shift(1)
        .expanding()
        .sum()
    )
)


# ------------------------------------------------------------
# Sender previous average amount
# ------------------------------------------------------------

df["sender_previous_average"] = (
    df.groupby("sender_upi_id")["amount_inr"]
    .transform(
        lambda x:
        x.shift(1)
        .expanding()
        .mean()
    )
)


# ------------------------------------------------------------
# Sender previous standard deviation
# ------------------------------------------------------------

df["sender_previous_std"] = (
    df.groupby("sender_upi_id")["amount_inr"]
    .transform(
        lambda x:
        x.shift(1)
        .expanding()
        .std()
    )
)


# ------------------------------------------------------------
# Receiver previous transaction count
# ------------------------------------------------------------

df["receiver_previous_count"] = (
    df.groupby("receiver_upi_id")
    .cumcount()
)


# ------------------------------------------------------------
# Receiver previous total amount
# ------------------------------------------------------------

df["receiver_previous_total"] = (
    df.groupby("receiver_upi_id")["amount_inr"]
    .transform(
        lambda x:
        x.shift(1)
        .expanding()
        .sum()
    )
)


# ------------------------------------------------------------
# Receiver previous average amount
# ------------------------------------------------------------

df["receiver_previous_average"] = (
    df.groupby("receiver_upi_id")["amount_inr"]
    .transform(
        lambda x:
        x.shift(1)
        .expanding()
        .mean()
    )
)


# Historical features are undefined for first transactions.
# Zero means there is no previous transaction history.
historical_features = [
    "sender_previous_count",
    "sender_previous_total",
    "sender_previous_average",
    "sender_previous_std",
    "receiver_previous_count",
    "receiver_previous_total",
    "receiver_previous_average"
]

df[historical_features] = (
    df[historical_features]
    .replace(
        [np.inf, -np.inf],
        np.nan
    )
    .fillna(0)
)


# ============================================================
# FEATURES USED BY ML MODELS
# ============================================================

features = [
    "amount_inr",
    "transaction_hour",
    "day_of_week",
    "sender_previous_count",
    "sender_previous_total",
    "sender_previous_average",
    "sender_previous_std",
    "receiver_previous_count",
    "receiver_previous_total",
    "receiver_previous_average"
]


print("\nFeatures used:")

for feature in features:
    print(f"  - {feature}")


# ============================================================
# PREPARE FEATURE MATRIX
# ============================================================

X = df[features].copy()

X = X.replace(
    [np.inf, -np.inf],
    np.nan
)

X = X.fillna(0)


# ============================================================
# SCALE FEATURES
# ============================================================

print("\nScaling features...")

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# ============================================================
# MODEL 1
# ISOLATION FOREST
# ============================================================

print("\n" + "-" * 70)
print("MODEL 1 — ISOLATION FOREST")
print("-" * 70)

isolation_forest = IsolationForest(
    n_estimators=200,
    contamination=0.05,
    random_state=42
)

isolation_predictions = (
    isolation_forest.fit_predict(X_scaled)
)

df["isolation_forest_new"] = (
    isolation_predictions == -1
).astype(int)

isolation_count = int(
    df["isolation_forest_new"].sum()
)

print(
    f"Anomalies detected: "
    f"{isolation_count:,}"
)

print(
    f"Anomaly rate: "
    f"{isolation_count / len(df) * 100:.2f}%"
)


# ============================================================
# MODEL 2
# LOCAL OUTLIER FACTOR
# ============================================================

print("\n" + "-" * 70)
print("MODEL 2 — LOCAL OUTLIER FACTOR")
print("-" * 70)

lof = LocalOutlierFactor(
    n_neighbors=20,
    contamination=0.05,
    novelty=False
)

lof_predictions = lof.fit_predict(
    X_scaled
)

df["lof_anomaly"] = (
    lof_predictions == -1
).astype(int)

lof_count = int(
    df["lof_anomaly"].sum()
)

print(
    f"Anomalies detected: "
    f"{lof_count:,}"
)

print(
    f"Anomaly rate: "
    f"{lof_count / len(df) * 100:.2f}%"
)


# ============================================================
# MODEL 3
# ONE-CLASS SVM
# ============================================================

print("\n" + "-" * 70)
print("MODEL 3 — ONE-CLASS SVM")
print("-" * 70)

one_class_svm = OneClassSVM(
    kernel="rbf",
    gamma="scale",
    nu=0.05
)

svm_predictions = (
    one_class_svm.fit_predict(X_scaled)
)

df["one_class_svm_anomaly"] = (
    svm_predictions == -1
).astype(int)

svm_count = int(
    df["one_class_svm_anomaly"].sum()
)

print(
    f"Anomalies detected: "
    f"{svm_count:,}"
)

print(
    f"Anomaly rate: "
    f"{svm_count / len(df) * 100:.2f}%"
)


# ============================================================
# MODEL COMPARISON
# ============================================================

print("\n" + "=" * 70)
print("                    MODEL COMPARISON")
print("=" * 70)

comparison = pd.DataFrame({

    "Model": [
        "Isolation Forest",
        "Local Outlier Factor",
        "One-Class SVM"
    ],

    "Anomalies": [
        isolation_count,
        lof_count,
        svm_count
    ]
})

comparison["Anomaly Rate (%)"] = (
    comparison["Anomalies"]
    / len(df)
    * 100
)

print("\n")

print(
    comparison.to_string(
        index=False,
        formatters={
            "Anomaly Rate (%)": "{:.2f}".format
        }
    )
)


# ============================================================
# MODEL AGREEMENT
# ============================================================

print("\n" + "=" * 70)
print("                    MODEL AGREEMENT")
print("=" * 70)

df["ml_model_count"] = (
    df["isolation_forest_new"]
    + df["lof_anomaly"]
    + df["one_class_svm_anomaly"]
)

agreement_distribution = (
    df["ml_model_count"]
    .value_counts()
    .sort_index()
)

print(
    "\nNumber of models flagging each transaction:"
)

for count, transactions in (
    agreement_distribution.items()
):

    percentage = (
        transactions
        / len(df)
        * 100
    )

    print(
        f"{count} models: "
        f"{transactions:,} transactions "
        f"({percentage:.2f}%)"
    )


# ============================================================
# ALL THREE MODELS AGREE
# ============================================================

all_three = int(
    (
        df["ml_model_count"] == 3
    ).sum()
)

print(
    f"\nAll three ML models agree: "
    f"{all_three:,} transactions"
)


# ============================================================
# PAIRWISE OVERLAP
# ============================================================

if_overlap = int(
    (
        (df["isolation_forest_new"] == 1)
        &
        (df["lof_anomaly"] == 1)
    ).sum()
)

if_svm_overlap = int(
    (
        (df["isolation_forest_new"] == 1)
        &
        (df["one_class_svm_anomaly"] == 1)
    ).sum()
)

lof_svm_overlap = int(
    (
        (df["lof_anomaly"] == 1)
        &
        (df["one_class_svm_anomaly"] == 1)
    ).sum()
)


print("\nPairwise overlap:")

print(
    f"Isolation Forest + LOF: "
    f"{if_overlap:,}"
)

print(
    f"Isolation Forest + One-Class SVM: "
    f"{if_svm_overlap:,}"
)

print(
    f"LOF + One-Class SVM: "
    f"{lof_svm_overlap:,}"
)


# ============================================================
# OVERLAP WITH EXISTING ANOMALY ENGINE
# ============================================================

df["existing_anomaly"] = (
    df["anomaly_count"] > 0
).astype(int)

ml_and_existing = int(
    (
        (df["ml_model_count"] > 0)
        &
        (df["existing_anomaly"] == 1)
    ).sum()
)


print("\nTransactions flagged by both:")

print(
    f"Existing anomaly engine + "
    f"at least one new ML model: "
    f"{ml_and_existing:,}"
)


# ============================================================
# SAVE RESULTS
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n" + "=" * 70)

print(
    "ML MODEL COMPARISON COMPLETED"
)

print(
    f"\nResults saved to:"
    f"\n{OUTPUT_FILE}"
)

print("=" * 70)