import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest


def detect_iqr_anomalies(df):
    """
    Detect transaction amount outliers using IQR.
    """

    df = df.copy()

    Q1 = df["amount_inr"].quantile(0.25)
    Q3 = df["amount_inr"].quantile(0.75)

    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    df["iqr_anomaly"] = (
        (df["amount_inr"] < lower_bound) |
        (df["amount_inr"] > upper_bound)
    )

    print("\n--- IQR Anomaly Detection ---")
    print(f"Q1: {Q1:.2f}")
    print(f"Q3: {Q3:.2f}")
    print(f"IQR: {IQR:.2f}")
    print(f"Lower Bound: {lower_bound:.2f}")
    print(f"Upper Bound: {upper_bound:.2f}")
    print(f"IQR anomalies: {df['iqr_anomaly'].sum()}")

    return df


if __name__ == "__main__":

    input_file = "data/processed/upi_cleaned.csv"

    df = pd.read_csv(input_file)

    df = detect_iqr_anomalies(df)

    output_file = "data/processed/upi_iqr.csv"

    df.to_csv(output_file, index=False)

    print(f"\nSaved to: {output_file}")