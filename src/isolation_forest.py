import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest


def create_behavioral_features(df):
    """
    Create transaction features using only historical information.
    """

    df = df.copy()

    # Make sure transactions are chronological
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Basic time features
    df["transaction_hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek

    # ---------------------------------------
    # Previous sender transaction count
    # ---------------------------------------
    df["sender_previous_count"] = (
        df.groupby("sender_upi_id").cumcount()
    )

    # ---------------------------------------
    # Previous sender amount statistics
    # ---------------------------------------
    df["sender_previous_total"] = (
        df.groupby("sender_upi_id")["amount_inr"]
        .transform(lambda x: x.shift(1).expanding().sum())
    )

    df["sender_previous_average"] = (
        df.groupby("sender_upi_id")["amount_inr"]
        .transform(lambda x: x.shift(1).expanding().mean())
    )

    df["sender_previous_std"] = (
        df.groupby("sender_upi_id")["amount_inr"]
        .transform(
            lambda x: x.shift(1).expanding().std()
        )
    )

    # ---------------------------------------
    # Previous receiver transaction count
    # ---------------------------------------
    df["receiver_previous_count"] = (
        df.groupby("receiver_upi_id").cumcount()
    )

    # ---------------------------------------
    # Previous receiver amount statistics
    # ---------------------------------------
    df["receiver_previous_total"] = (
        df.groupby("receiver_upi_id")["amount_inr"]
        .transform(lambda x: x.shift(1).expanding().sum())
    )

    df["receiver_previous_average"] = (
        df.groupby("receiver_upi_id")["amount_inr"]
        .transform(lambda x: x.shift(1).expanding().mean())
    )

    # Replace NaN values for users/receivers
    # with no previous transaction history.
    historical_columns = [
        "sender_previous_total",
        "sender_previous_average",
        "sender_previous_std",
        "receiver_previous_total",
        "receiver_previous_average"
    ]

    df[historical_columns] = df[historical_columns].fillna(0)

    return df


def detect_isolation_forest(df):

    df = df.copy()

    # Features used by Isolation Forest
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

    # Create model
    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42
    )

    # Train and predict
    predictions = model.fit_predict(df[features])

    # Convert:
    # -1 = anomaly
    #  1 = normal
    df["isolation_forest_anomaly"] = (
        predictions == -1
    ).astype(int)

    # Anomaly score
    df["isolation_forest_score"] = (
        model.decision_function(df[features])
    )

    print("\n--- Isolation Forest ---")

    print(
        "Anomalies detected:",
        df["isolation_forest_anomaly"].sum()
    )

    print(
        "Normal transactions:",
        (df["isolation_forest_anomaly"] == 0).sum()
    )

    return df


if __name__ == "__main__":

    input_file = "data/processed/upi_cleaned.csv"

    df = pd.read_csv(input_file)

    # Create historical behavioral features
    df = create_behavioral_features(df)

    # Run Isolation Forest
    df = detect_isolation_forest(df)

    # Save results
    output_file = (
        "data/processed/upi_isolation_forest.csv"
    )

    df.to_csv(output_file, index=False)

    print(
        f"\nSaved to: {output_file}"
    )