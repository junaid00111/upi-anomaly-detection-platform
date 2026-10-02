import pandas as pd
import numpy as np

# ============================================================
# UPI DATA QUALITY CHECK
# ============================================================

INPUT_FILE = "data/processed/upi_risk_scores.csv"

print("\n" + "=" * 75)
print("                 UPI DATA QUALITY CHECK")
print("=" * 75)


# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print(f"\nDataset loaded: {len(df):,} rows")
print(f"Columns: {len(df.columns)}")


# ------------------------------------------------------------
# 2. DUPLICATE TRANSACTION IDs
# ------------------------------------------------------------

duplicate_ids = df["transaction_id"].duplicated().sum()

print("\n" + "-" * 75)
print("1. DUPLICATE TRANSACTION IDs")
print("-" * 75)

print(f"Duplicate transaction IDs: {duplicate_ids}")

if duplicate_ids == 0:
    print("PASS")
else:
    print("FAIL")


# ------------------------------------------------------------
# 3. MISSING VALUES
# ------------------------------------------------------------

print("\n" + "-" * 75)
print("2. MISSING VALUES")
print("-" * 75)

missing = df.isnull().sum()

# failure_reason is expected to be empty for
# successful and pending transactions.
# Therefore, it is excluded from the generic
# required-field missing-value check.

general_missing = missing.drop(
    labels=["failure_reason"],
    errors="ignore"
)

general_missing_total = general_missing.sum()

print(
    f"Missing values in required fields: "
    f"{general_missing_total}"
)

if general_missing_total == 0:
    print("PASS — No missing values in required fields")
else:
    print("\nColumns with missing required values:")

    print(
        general_missing[general_missing > 0]
        .sort_values(ascending=False)
    )


# ------------------------------------------------------------
# FAILURE REASON BUSINESS-RULE CHECK
# ------------------------------------------------------------

failed_transactions = df[
    df["status"] == "FAILED"
]

failed_missing_reason = failed_transactions[
    "failure_reason"
].isna().sum()

print(
    f"\nFAILED transactions without failure reason: "
    f"{failed_missing_reason}"
)

if failed_missing_reason == 0:
    print(
        "PASS — All FAILED transactions have "
        "a failure reason"
    )
else:
    print(
        "FAIL — Some FAILED transactions are "
        "missing failure reasons"
    )


# ------------------------------------------------------------
# 4. TRANSACTION AMOUNT VALIDATION
# ------------------------------------------------------------

print("\n" + "-" * 75)
print("3. TRANSACTION AMOUNT VALIDATION")
print("-" * 75)

invalid_amounts = (
    df["amount_inr"].isna()
    | (df["amount_inr"] <= 0)
)

invalid_amount_count = invalid_amounts.sum()

print(
    f"Invalid transaction amounts: "
    f"{invalid_amount_count}"
)

if invalid_amount_count == 0:
    print("PASS")
else:
    print("FAIL")


# ------------------------------------------------------------
# 5. ANOMALY FLAG VALIDATION
# ------------------------------------------------------------

anomaly_columns = [
    "iqr_anomaly",
    "isolation_forest_anomaly",
    "time_series_anomaly",
    "isolation_forest_new",
    "lof_anomaly",
    "one_class_svm_anomaly"
]

print("\n" + "-" * 75)
print("4. ANOMALY FLAG VALIDATION")
print("-" * 75)

anomaly_pass = True

for column in anomaly_columns:

    values = set(
        pd.to_numeric(
            df[column],
            errors="coerce"
        )
        .dropna()
        .unique()
    )

    invalid_values = values - {0, 1}

    if invalid_values:

        print(
            f"{column}: FAIL "
            f"(invalid values: {invalid_values})"
        )

        anomaly_pass = False

    else:
        print(f"{column}: PASS")


# ------------------------------------------------------------
# 6. RISK SCORE VALIDATION
# ------------------------------------------------------------

print("\n" + "-" * 75)
print("5. RISK SCORE VALIDATION")
print("-" * 75)

invalid_scores = (
    df["risk_score"].isna()
    | (df["risk_score"] < 0)
    | (df["risk_score"] > 100)
)

invalid_score_count = invalid_scores.sum()

print(
    f"Invalid risk scores: "
    f"{invalid_score_count}"
)

print(
    f"Minimum score: "
    f"{df['risk_score'].min():.2f}"
)

print(
    f"Maximum score: "
    f"{df['risk_score'].max():.2f}"
)

if invalid_score_count == 0:
    print("PASS")
else:
    print("FAIL")


# ------------------------------------------------------------
# 7. RISK LEVEL VALIDATION
# ------------------------------------------------------------

print("\n" + "-" * 75)
print("6. RISK LEVEL VALIDATION")
print("-" * 75)

valid_levels = {
    "Low",
    "Medium",
    "High",
    "Critical"
}

actual_levels = set(
    df["risk_level"]
    .dropna()
    .unique()
)

invalid_levels = actual_levels - valid_levels

print(
    f"Risk levels found: "
    f"{sorted(actual_levels)}"
)

if invalid_levels:

    print(
        f"FAIL — Invalid levels: "
        f"{invalid_levels}"
    )

else:
    print("PASS")


# ------------------------------------------------------------
# 8. RISK SCORE ↔ RISK LEVEL CONSISTENCY
# ------------------------------------------------------------

def expected_risk_level(score):

    if score >= 80:
        return "Critical"

    elif score >= 60:
        return "High"

    elif score >= 30:
        return "Medium"

    else:
        return "Low"


expected_levels = df["risk_score"].apply(
    expected_risk_level
)

level_mismatches = (
    df["risk_level"] != expected_levels
).sum()

print(
    "\nRisk score/level mismatches:",
    level_mismatches
)

if level_mismatches == 0:
    print("PASS")
else:
    print("FAIL")


# ------------------------------------------------------------
# 9. TRANSACTION COUNT CHECK
# ------------------------------------------------------------

print("\n" + "-" * 75)
print("7. TRANSACTION COUNT CHECK")
print("-" * 75)

print(
    f"Transactions: "
    f"{len(df):,}"
)

if len(df) == 10000:

    print(
        "PASS — Expected 10,000 transactions"
    )

else:

    print(
        "WARNING — Transaction count differs "
        "from expected 10,000"
    )


# ------------------------------------------------------------
# 10. TIMESTAMP VALIDATION
# ------------------------------------------------------------

print("\n" + "-" * 75)
print("8. TIMESTAMP VALIDATION")
print("-" * 75)

timestamps = pd.to_datetime(
    df["timestamp"],
    errors="coerce"
)

invalid_timestamps = timestamps.isna().sum()

print(
    f"Invalid timestamps: "
    f"{invalid_timestamps}"
)

if invalid_timestamps == 0:

    print("PASS")

    print(
        f"Date range: "
        f"{timestamps.min()} → "
        f"{timestamps.max()}"
    )

else:

    print("FAIL")


# ------------------------------------------------------------
# 11. INVESTIGATION FLAG VALIDATION
# ------------------------------------------------------------

print("\n" + "-" * 75)
print("9. INVESTIGATION FLAG VALIDATION")
print("-" * 75)

expected_investigation = np.where(
    df["risk_score"] >= 60,
    "Yes",
    "No"
)

investigation_mismatches = (
    df["investigation_required"]
    != expected_investigation
).sum()

print(
    f"Investigation flag mismatches: "
    f"{investigation_mismatches}"
)

if investigation_mismatches == 0:
    print("PASS")
else:
    print("FAIL")


# ------------------------------------------------------------
# 12. FINAL DATA QUALITY STATUS
# ------------------------------------------------------------

all_checks_pass = (
    duplicate_ids == 0
    and general_missing_total == 0
    and failed_missing_reason == 0
    and invalid_amount_count == 0
    and anomaly_pass
    and invalid_score_count == 0
    and len(invalid_levels) == 0
    and level_mismatches == 0
    and invalid_timestamps == 0
    and investigation_mismatches == 0
)


print("\n" + "=" * 75)
print("                    FINAL DATA QUALITY")
print("=" * 75)


if all_checks_pass:

    print("\nSTATUS: PASS")

    print(
        "The Power BI master dataset is ready."
    )

else:

    print("\nSTATUS: REVIEW REQUIRED")

    print(
        "One or more data-quality checks failed."
    )


print("\nMaster dataset:")
print(INPUT_FILE)

print("\n" + "=" * 75)