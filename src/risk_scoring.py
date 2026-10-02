import pandas as pd
import numpy as np

# ============================================================
# UPI TRANSACTION RISK SCORING
# ============================================================

print("\n" + "=" * 70)
print("              UPI TRANSACTION RISK SCORING")
print("=" * 70)

# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

base_file = "data/processed/upi_anomaly_results.csv"
ml_file = "data/processed/upi_ml_comparison.csv"

base_df = pd.read_csv(base_file)
ml_df = pd.read_csv(ml_file)

print(f"\nBase transactions: {len(base_df):,}")
print(f"ML comparison rows: {len(ml_df):,}")


# ------------------------------------------------------------
# 2. KEEP ONLY REQUIRED ML COLUMNS
# ------------------------------------------------------------

ml_columns = [
    "transaction_id",
    "isolation_forest_new",
    "lof_anomaly",
    "one_class_svm_anomaly"
]

ml_df = ml_df[ml_columns].copy()


# ------------------------------------------------------------
# 3. MERGE DATA
# ------------------------------------------------------------

df = base_df.merge(
    ml_df,
    on="transaction_id",
    how="left"
)

print(f"Merged dataset: {len(df):,} transactions")


# ------------------------------------------------------------
# 4. HANDLE MISSING VALUES
# ------------------------------------------------------------

anomaly_columns = [
    "iqr_anomaly",
    "isolation_forest_anomaly",
    "time_series_anomaly",
    "isolation_forest_new",
    "lof_anomaly",
    "one_class_svm_anomaly"
]

for column in anomaly_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    ).fillna(0).astype(int)


# ------------------------------------------------------------
# 5. CALCULATE ML MODEL AGREEMENT
# ------------------------------------------------------------

df["ml_model_agreement"] = (
    df["isolation_forest_new"]
    + df["lof_anomaly"]
    + df["one_class_svm_anomaly"]
)

print("\nML agreement distribution:")

print(
    df["ml_model_agreement"]
    .value_counts()
    .sort_index()
)


# ------------------------------------------------------------
# 6. CREATE RISK SCORE
# ------------------------------------------------------------

df["risk_score"] = 0.0

# Existing anomaly signals
df["risk_score"] += df["iqr_anomaly"] * 15
df["risk_score"] += df["isolation_forest_anomaly"] * 15
df["risk_score"] += df["time_series_anomaly"] * 15

# New ML models
df["risk_score"] += df["isolation_forest_new"] * 10
df["risk_score"] += df["lof_anomaly"] * 10
df["risk_score"] += df["one_class_svm_anomaly"] * 10


# ------------------------------------------------------------
# 7. MULTI-MODEL AGREEMENT BONUS
# ------------------------------------------------------------

# Two models agree → +5
df.loc[df["ml_model_agreement"] == 2, "risk_score"] += 5

# Three models agree → +10
df.loc[df["ml_model_agreement"] == 3, "risk_score"] += 10


# ------------------------------------------------------------
# 8. CAP SCORE AT 100
# ------------------------------------------------------------

df["risk_score"] = df["risk_score"].clip(upper=100)

df["risk_score"] = df["risk_score"].round(2)


# ------------------------------------------------------------
# 9. CREATE RISK LEVEL
# ------------------------------------------------------------

def classify_risk(score):

    if score >= 80:
        return "Critical"

    elif score >= 60:
        return "High"

    elif score >= 30:
        return "Medium"

    else:
        return "Low"


df["risk_level"] = df["risk_score"].apply(classify_risk)


# ------------------------------------------------------------
# 10. CREATE RISK SIGNAL COUNT
# ------------------------------------------------------------

df["risk_signal_count"] = (
    df["iqr_anomaly"]
    + df["isolation_forest_anomaly"]
    + df["time_series_anomaly"]
    + df["isolation_forest_new"]
    + df["lof_anomaly"]
    + df["one_class_svm_anomaly"]
)


# ------------------------------------------------------------
# 11. CREATE INVESTIGATION FLAG
# ------------------------------------------------------------

df["investigation_required"] = np.where(
    df["risk_score"] >= 60,
    "Yes",
    "No"
)


# ------------------------------------------------------------
# 12. SAVE RESULTS
# ------------------------------------------------------------

output_file = "data/processed/upi_risk_scores.csv"

df.to_csv(
    output_file,
    index=False
)


# ------------------------------------------------------------
# 13. DISPLAY RESULTS
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("RISK SCORE SUMMARY")
print("-" * 70)

print(
    f"Average risk score: "
    f"{df['risk_score'].mean():.2f}"
)

print(
    f"Maximum risk score: "
    f"{df['risk_score'].max():.2f}"
)

print(
    f"Minimum risk score: "
    f"{df['risk_score'].min():.2f}"
)


print("\n" + "-" * 70)
print("RISK LEVEL DISTRIBUTION")
print("-" * 70)

risk_distribution = (
    df["risk_level"]
    .value_counts()
    .reindex(
        ["Low", "Medium", "High", "Critical"],
        fill_value=0
    )
)

for level, count in risk_distribution.items():

    percentage = (count / len(df)) * 100

    print(
        f"{level:10} : "
        f"{count:5,} transactions "
        f"({percentage:.2f}%)"
    )


print("\n" + "-" * 70)
print("INVESTIGATION SUMMARY")
print("-" * 70)

investigation_count = (
    df["investigation_required"] == "Yes"
).sum()

print(
    f"Transactions requiring investigation: "
    f"{investigation_count:,}"
)

print(
    f"Investigation rate: "
    f"{investigation_count / len(df) * 100:.2f}%"
)


print("\n" + "-" * 70)
print("TOP 10 HIGHEST-RISK TRANSACTIONS")
print("-" * 70)

top_transactions = (
    df[
        [
            "transaction_id",
            "amount_inr",
            "risk_score",
            "risk_level",
            "risk_signal_count"
        ]
    ]
    .sort_values(
        "risk_score",
        ascending=False
    )
    .head(10)
)

print(top_transactions.to_string(index=False))


print("\n" + "=" * 70)
print("RISK SCORING COMPLETED")
print("=" * 70)

print(f"\nResults saved to:")
print(output_file)

print("\nNOTE:")
print(
    "Risk scores represent the number and strength of "
    "anomaly signals and are NOT probabilities of fraud."
)