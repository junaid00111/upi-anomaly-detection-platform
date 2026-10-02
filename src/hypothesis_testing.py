import pandas as pd
import numpy as np

from scipy.stats import mannwhitneyu
from scipy.stats import chi2_contingency


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "data/processed/upi_anomaly_results.csv"

ALPHA = 0.05


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

df["timestamp"] = pd.to_datetime(df["timestamp"])

df["anomaly_count"] = pd.to_numeric(
    df["anomaly_count"],
    errors="coerce"
).fillna(0)

df["is_anomaly"] = (
    df["anomaly_count"] > 0
).astype(int)


# ============================================================
# EFFECT SIZE FUNCTIONS
# ============================================================

def rank_biserial_effect_size(u_statistic, n1, n2):
    """
    Rank-biserial correlation for Mann-Whitney U.

    Range:
        -1 to +1

    The absolute value indicates the strength
    of the difference between the two groups.
    """

    return (
        (2 * u_statistic) / (n1 * n2)
    ) - 1


def interpret_rank_biserial(effect):

    magnitude = abs(effect)

    if magnitude < 0.10:
        strength = "Negligible"

    elif magnitude < 0.30:
        strength = "Small"

    elif magnitude < 0.50:
        strength = "Moderate"

    else:
        strength = "Large"

    return strength


def cramers_v(chi2, n, rows, columns):
    """
    Cramér's V effect size for Chi-square test.
    """

    minimum_dimension = min(
        rows - 1,
        columns - 1
    )

    return np.sqrt(
        chi2 /
        (n * minimum_dimension)
    )


def interpret_cramers_v(effect):

    if effect < 0.10:
        return "Negligible"

    elif effect < 0.30:
        return "Small"

    elif effect < 0.50:
        return "Moderate"

    else:
        return "Large"


# ============================================================
# HEADER
# ============================================================

print("\n")
print("=" * 75)
print("              UPI HYPOTHESIS TESTING")
print("=" * 75)

print(f"\nDataset size: {len(df):,} transactions")

print(f"Significance level (α): {ALPHA}")


# ============================================================
# TEST 1
# P2P vs P2M
# ============================================================

print("\n")
print("-" * 75)
print("TEST 1 — P2P vs P2M TRANSACTION AMOUNTS")
print("-" * 75)


p2p = df.loc[
    df["transaction_type"] == "P2P",
    "amount_inr"
].dropna()

p2m = df.loc[
    df["transaction_type"] == "P2M",
    "amount_inr"
].dropna()


u_statistic, p_value = mannwhitneyu(
    p2p,
    p2m,
    alternative="two-sided"
)


effect = rank_biserial_effect_size(
    u_statistic,
    len(p2p),
    len(p2m)
)


print(f"\nP2P transactions: {len(p2p):,}")
print(f"P2M transactions: {len(p2m):,}")

print(
    f"\nP2P median amount: "
    f"₹{p2p.median():,.2f}"
)

print(
    f"P2M median amount: "
    f"₹{p2m.median():,.2f}"
)

print(
    f"\nMann–Whitney U: "
    f"{u_statistic:,.0f}"
)

print(
    f"P-value: "
    f"{p_value:.6e}"
)

print(
    f"Rank-biserial effect size: "
    f"{effect:.4f}"
)

print(
    f"Effect strength: "
    f"{interpret_rank_biserial(effect)}"
)


if p_value < ALPHA:

    print(
        "\nResult: Statistically significant"
    )

    print(
        "There is statistical evidence that "
        "P2P and P2M transaction amount "
        "distributions differ."
    )

else:

    print(
        "\nResult: Not statistically significant"
    )


# ============================================================
# TEST 2
# NORMAL vs ANOMALOUS
# ============================================================

print("\n")
print("-" * 75)
print("TEST 2 — NORMAL vs ANOMALOUS TRANSACTION AMOUNTS")
print("-" * 75)


normal = df.loc[
    df["is_anomaly"] == 0,
    "amount_inr"
].dropna()

anomalous = df.loc[
    df["is_anomaly"] == 1,
    "amount_inr"
].dropna()


u_statistic, p_value = mannwhitneyu(
    normal,
    anomalous,
    alternative="two-sided"
)


effect = rank_biserial_effect_size(
    u_statistic,
    len(normal),
    len(anomalous)
)


print(f"\nNormal transactions: {len(normal):,}")
print(f"Anomalous transactions: {len(anomalous):,}")

print(
    f"\nNormal median amount: "
    f"₹{normal.median():,.2f}"
)

print(
    f"Anomalous median amount: "
    f"₹{anomalous.median():,.2f}"
)

print(
    f"\nMann–Whitney U: "
    f"{u_statistic:,.0f}"
)

print(
    f"P-value: "
    f"{p_value:.6e}"
)

print(
    f"Rank-biserial effect size: "
    f"{effect:.4f}"
)

print(
    f"Effect strength: "
    f"{interpret_rank_biserial(effect)}"
)


if p_value < ALPHA:

    print(
        "\nResult: Statistically significant"
    )

    print(
        "Transaction amount distributions "
        "differ between normal and anomalous "
        "transactions."
    )

else:

    print(
        "\nResult: Not statistically significant"
    )


# ============================================================
# TEST 3
# CATEGORY vs ANOMALY
# ============================================================

print("\n")
print("-" * 75)
print("TEST 3 — CATEGORY vs ANOMALY STATUS")
print("-" * 75)


contingency_table = pd.crosstab(
    df["category"],
    df["is_anomaly"]
)


print("\nContingency Table:")
print(contingency_table)


chi2, p_value, degrees_of_freedom, expected = (
    chi2_contingency(
        contingency_table
    )
)


rows, columns = contingency_table.shape

v = cramers_v(
    chi2,
    len(df),
    rows,
    columns
)


print(
    f"\nChi-square statistic: "
    f"{chi2:.4f}"
)

print(
    f"Degrees of freedom: "
    f"{degrees_of_freedom}"
)

print(
    f"P-value: "
    f"{p_value:.6e}"
)

print(
    f"Cramér's V: "
    f"{v:.4f}"
)

print(
    f"Association strength: "
    f"{interpret_cramers_v(v)}"
)


if p_value < ALPHA:

    print(
        "\nResult: Statistically significant"
    )

    print(
        "There is statistical evidence of an "
        "association between transaction category "
        "and anomaly status."
    )

else:

    print(
        "\nResult: Not statistically significant"
    )


# ============================================================
# CATEGORY SUMMARY
# ============================================================

print("\n")
print("-" * 75)
print("ANOMALY RATE BY CATEGORY")
print("-" * 75)


category_summary = (
    df.groupby("category")
    .agg(
        transactions=("transaction_id", "count"),
        anomalies=("is_anomaly", "sum")
    )
)

category_summary["anomaly_rate"] = (
    category_summary["anomalies"]
    / category_summary["transactions"]
    * 100
)

category_summary = category_summary.sort_values(
    "anomaly_rate",
    ascending=False
)


print(
    category_summary.to_string(
        formatters={
            "anomaly_rate": "{:.2f}%".format
        }
    )
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n")
print("=" * 75)
print("                    FINAL SUMMARY")
print("=" * 75)


# ------------------------------------------------------------
# TEST 1 SUMMARY — P2P vs P2M
# ------------------------------------------------------------

u1, p1 = mannwhitneyu(
    p2p,
    p2m,
    alternative="two-sided"
)

effect1 = rank_biserial_effect_size(
    u1,
    len(p2p),
    len(p2m)
)

strength1 = interpret_rank_biserial(effect1)


print("\nTEST 1 — P2P vs P2M")

print(
    f"  P-value: {p1:.6e}"
)

print(
    f"  Effect size: {effect1:.4f}"
)

print(
    f"  Effect strength: {strength1}"
)


# ------------------------------------------------------------
# TEST 2 SUMMARY — NORMAL vs ANOMALOUS
# ------------------------------------------------------------

u2, p2 = mannwhitneyu(
    normal,
    anomalous,
    alternative="two-sided"
)

effect2 = rank_biserial_effect_size(
    u2,
    len(normal),
    len(anomalous)
)

strength2 = interpret_rank_biserial(effect2)


print("\nTEST 2 — NORMAL vs ANOMALOUS")

print(
    f"  P-value: {p2:.6e}"
)

print(
    f"  Effect size: {effect2:.4f}"
)

print(
    f"  Effect strength: {strength2}"
)


# ------------------------------------------------------------
# TEST 3 SUMMARY — CATEGORY vs ANOMALY
# ------------------------------------------------------------

print("\nTEST 3 — CATEGORY vs ANOMALY")

print(
    f"  P-value: {p_value:.6e}"
)

print(
    f"  Cramér's V: {v:.4f}"
)

print(
    f"  Association strength: "
    f"{interpret_cramers_v(v)}"
)


# ------------------------------------------------------------
# FINAL NOTES
# ------------------------------------------------------------

print("\n")
print("=" * 75)

print(
    "Note: Statistical significance does not establish causation."
)

print(
    "An anomalous transaction is not necessarily fraudulent."
)

print("=" * 75)

print(
    "\nHypothesis testing completed successfully."
)