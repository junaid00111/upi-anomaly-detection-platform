import pandas as pd

# ============================================================
# UPI RISK SENSITIVITY ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("              UPI RISK SENSITIVITY ANALYSIS")
print("=" * 70)

# ------------------------------------------------------------
# 1. LOAD RISK-SCORED DATA
# ------------------------------------------------------------

input_file = "data/processed/upi_risk_scores.csv"

df = pd.read_csv(input_file)

print(f"\nTransactions loaded: {len(df):,}")


# ------------------------------------------------------------
# 2. DEFINE SENSITIVITY LEVELS
# ------------------------------------------------------------

sensitivity_levels = {
    "Low": 80,
    "Medium": 60,
    "High": 30
}


# ------------------------------------------------------------
# 3. ANALYZE EACH SENSITIVITY LEVEL
# ------------------------------------------------------------

results = []

print("\n" + "-" * 70)
print("SENSITIVITY COMPARISON")
print("-" * 70)

for sensitivity, threshold in sensitivity_levels.items():

    flagged = df[df["risk_score"] >= threshold]

    count = len(flagged)

    percentage = (count / len(df)) * 100

    results.append({
        "sensitivity": sensitivity,
        "risk_threshold": threshold,
        "transactions_flagged": count,
        "flag_rate_percent": round(percentage, 2)
    })

    print(
        f"{sensitivity:10} | "
        f"Threshold >= {threshold:3} | "
        f"Flagged: {count:5,} | "
        f"Rate: {percentage:.2f}%"
    )


# ------------------------------------------------------------
# 4. CREATE RESULTS DATAFRAME
# ------------------------------------------------------------

sensitivity_df = pd.DataFrame(results)


# ------------------------------------------------------------
# 5. ADD RISK LEVEL BREAKDOWN
# ------------------------------------------------------------

for sensitivity, threshold in sensitivity_levels.items():

    flagged = df[df["risk_score"] >= threshold]

    print("\n" + "-" * 70)
    print(f"{sensitivity.upper()} SENSITIVITY")
    print("-" * 70)

    if len(flagged) == 0:
        print("No transactions flagged.")
        continue

    breakdown = (
        flagged["risk_level"]
        .value_counts()
        .reindex(
            ["Low", "Medium", "High", "Critical"],
            fill_value=0
        )
    )

    for level, count in breakdown.items():
        if count > 0:
            print(f"{level:10}: {count:,}")


# ------------------------------------------------------------
# 6. SAVE SUMMARY
# ------------------------------------------------------------

output_file = "data/processed/upi_sensitivity_analysis.csv"

sensitivity_df.to_csv(
    output_file,
    index=False
)


# ------------------------------------------------------------
# 7. SAVE FLAGGED TRANSACTIONS FOR EACH LEVEL
# ------------------------------------------------------------

for sensitivity, threshold in sensitivity_levels.items():

    flagged = df[df["risk_score"] >= threshold].copy()

    filename = (
        f"data/processed/"
        f"upi_{sensitivity.lower()}_sensitivity.csv"
    )

    flagged.to_csv(
        filename,
        index=False
    )


# ------------------------------------------------------------
# 8. FINAL OUTPUT
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("SENSITIVITY ANALYSIS COMPLETED")
print("=" * 70)

print("\nSummary saved to:")
print(output_file)

print("\nDetailed transaction files saved:")
print("data/processed/upi_low_sensitivity.csv")
print("data/processed/upi_medium_sensitivity.csv")
print("data/processed/upi_high_sensitivity.csv")