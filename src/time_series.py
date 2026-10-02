import pandas as pd
import numpy as np


def create_daily_metrics(df):
    """
    Aggregate UPI transactions by day.
    """

    df = df.copy()

    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Extract date
    df["date"] = df["timestamp"].dt.date

    # Aggregate daily transaction information
    daily = (
        df.groupby("date")
        .agg(
            transaction_count=("transaction_id", "count"),
            total_amount=("amount_inr", "sum"),
            average_amount=("amount_inr", "mean")
        )
        .reset_index()
    )

    # Convert date back to datetime
    daily["date"] = pd.to_datetime(daily["date"])

    # Sort chronologically
    daily = daily.sort_values("date").reset_index(drop=True)

    return daily


def detect_time_series_anomalies(daily):

    daily = daily.copy()

    window = 14

    # ------------------------------------
    # Rolling median
    # ------------------------------------

    daily["count_rolling_median"] = (
        daily["transaction_count"]
        .rolling(window=window, min_periods=7)
        .median()
        .shift(1)
    )

    daily["amount_rolling_median"] = (
        daily["total_amount"]
        .rolling(window=window, min_periods=7)
        .median()
        .shift(1)
    )

    # ------------------------------------
    # Rolling MAD
    # ------------------------------------

    def rolling_mad(series):

        median = series.median()

        return np.median(
            np.abs(series - median)
        )

    daily["count_mad"] = (
        daily["transaction_count"]
        .rolling(window=window, min_periods=7)
        .apply(rolling_mad)
        .shift(1)
    )

    daily["amount_mad"] = (
        daily["total_amount"]
        .rolling(window=window, min_periods=7)
        .apply(rolling_mad)
        .shift(1)
    )

    # ------------------------------------
    # Avoid zero MAD
    # ------------------------------------

    daily["count_mad"] = daily["count_mad"].replace(
        0, np.nan
    )

    daily["amount_mad"] = daily["amount_mad"].replace(
        0, np.nan
    )

    # ------------------------------------
    # Robust Z-Scores
    # ------------------------------------

    daily["count_robust_z"] = (
        0.6745
        * (
            daily["transaction_count"]
            - daily["count_rolling_median"]
        )
        / daily["count_mad"]
    )

    daily["amount_robust_z"] = (
        0.6745
        * (
            daily["total_amount"]
            - daily["amount_rolling_median"]
        )
        / daily["amount_mad"]
    )

    # ------------------------------------
    # Detect anomalies
    # ------------------------------------

    daily["time_series_volume_anomaly"] = (
        daily["count_robust_z"].abs() > 3.5
    ).astype(int)

    daily["time_series_amount_anomaly"] = (
        daily["amount_robust_z"].abs() > 3.5
    ).astype(int)

    daily["time_series_anomaly"] = (
        (
            daily["time_series_volume_anomaly"] == 1
        )
        |
        (
            daily["time_series_amount_anomaly"] == 1
        )
    ).astype(int)

    return daily


if __name__ == "__main__":

    # Load cleaned transaction data
    input_file = "data/processed/upi_cleaned.csv"

    df = pd.read_csv(input_file)

    # Create daily metrics
    daily = create_daily_metrics(df)

    # Detect anomalies
    daily = detect_time_series_anomalies(daily)

    # Save results
    output_file = (
        "data/processed/upi_time_series.csv"
    )

    daily.to_csv(
        output_file,
        index=False
    )

    # ------------------------------------
    # Display results
    # ------------------------------------

    print("\n--- Time-Series Anomaly Detection ---")

    print(
        "Total days:",
        len(daily)
    )

    print(
        "Volume anomalies:",
        daily["time_series_volume_anomaly"].sum()
    )

    print(
        "Amount anomalies:",
        daily["time_series_amount_anomaly"].sum()
    )

    print(
        "Total anomalous days:",
        daily["time_series_anomaly"].sum()
    )

    print(
        "\nAnomalous days:"
    )

    print(
        daily[
            daily["time_series_anomaly"] == 1
        ][
            [
                "date",
                "transaction_count",
                "total_amount",
                "count_robust_z",
                "amount_robust_z"
            ]
        ].to_string(index=False)
    )

    print(
        f"\nSaved to: {output_file}"
    )