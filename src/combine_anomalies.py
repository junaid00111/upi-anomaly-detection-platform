import pandas as pd


def combine_anomaly_results():

    # -----------------------------------------
    # 1. Load original cleaned transaction data
    # -----------------------------------------
    transactions = pd.read_csv(
        "data/processed/upi_cleaned.csv"
    )

    transactions["timestamp"] = pd.to_datetime(
        transactions["timestamp"]
    )

    transactions["date"] = (
        transactions["timestamp"].dt.date
    )

    # -----------------------------------------
    # 2. Load IQR results
    # -----------------------------------------
    iqr = pd.read_csv(
        "data/processed/upi_iqr.csv"
    )

    iqr = iqr[
        [
            "transaction_id",
            "iqr_anomaly"
        ]
    ]

    # -----------------------------------------
    # 3. Load Isolation Forest results
    # -----------------------------------------
    isolation = pd.read_csv(
        "data/processed/upi_isolation_forest.csv"
    )

    isolation = isolation[
        [
            "transaction_id",
            "isolation_forest_anomaly",
            "isolation_forest_score"
        ]
    ]

    # -----------------------------------------
    # 4. Load Time-Series results
    # -----------------------------------------
    time_series = pd.read_csv(
        "data/processed/upi_time_series.csv"
    )

    time_series["date"] = pd.to_datetime(
        time_series["date"]
    ).dt.date

    time_series = time_series[
        [
            "date",
            "time_series_volume_anomaly",
            "time_series_amount_anomaly",
            "time_series_anomaly"
        ]
    ]

    # -----------------------------------------
    # 5. Merge IQR results
    # -----------------------------------------
    combined = transactions.merge(
        iqr,
        on="transaction_id",
        how="left"
    )

    # -----------------------------------------
    # 6. Merge Isolation Forest
    # -----------------------------------------
    combined = combined.merge(
        isolation,
        on="transaction_id",
        how="left"
    )

    # -----------------------------------------
    # 7. Merge Time-Series results
    # -----------------------------------------
    combined = combined.merge(
        time_series,
        on="date",
        how="left"
    )

    # -----------------------------------------
    # 8. Fill missing anomaly values
    # -----------------------------------------
    anomaly_columns = [
        "iqr_anomaly",
        "isolation_forest_anomaly",
        "time_series_volume_anomaly",
        "time_series_amount_anomaly",
        "time_series_anomaly"
    ]

    combined[anomaly_columns] = (
        combined[anomaly_columns]
        .fillna(0)
        .astype(int)
    )

    # -----------------------------------------
    # 9. Calculate anomaly count
    # -----------------------------------------
    combined["anomaly_count"] = (
        combined["iqr_anomaly"]
        + combined["isolation_forest_anomaly"]
        + combined["time_series_anomaly"]
    )

    # -----------------------------------------
    # 10. Classify anomaly
    # -----------------------------------------
    def classify_anomaly(row):

        count = row["anomaly_count"]

        if count == 0:
            return "Normal"

        elif count == 1:
            return "Single Signal"

        elif count == 2:
            return "Multiple Signals"

        else:
            return "All Methods"

    combined["anomaly_type"] = (
        combined.apply(
            classify_anomaly,
            axis=1
        )
    )

    # -----------------------------------------
    # 11. Remove helper date column
    # -----------------------------------------
    combined.drop(
        columns=["date"],
        inplace=True
    )

    # -----------------------------------------
    # 12. Save final dataset
    # -----------------------------------------
    output_file = (
        "data/processed/upi_anomaly_results.csv"
    )

    combined.to_csv(
        output_file,
        index=False
    )

    # -----------------------------------------
    # 13. Display summary
    # -----------------------------------------
    print("\n--- Combined Anomaly Results ---")

    print(
        "Total transactions:",
        len(combined)
    )

    print(
        "IQR anomalies:",
        combined["iqr_anomaly"].sum()
    )

    print(
        "Isolation Forest anomalies:",
        combined[
            "isolation_forest_anomaly"
        ].sum()
    )

    print(
        "Time-series anomalous transactions:",
        combined[
            "time_series_anomaly"
        ].sum()
    )

    print(
        "Transactions flagged by all methods:",
        (
            combined["anomaly_count"] == 3
        ).sum()
    )

    print(
        "\nAnomaly classification:"
    )

    print(
        combined["anomaly_type"]
        .value_counts()
    )

    print(
        f"\nSaved to: {output_file}"
    )


if __name__ == "__main__":
    combine_anomaly_results()