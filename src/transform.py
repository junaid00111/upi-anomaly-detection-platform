import pandas as pd


def transform_data(df):

    # Make a copy so the original data is not modified
    df = df.copy()

    # -----------------------------
    # 1. Convert timestamp
    # -----------------------------
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # -----------------------------
    # 2. Sort transactions
    # -----------------------------
    df = df.sort_values("timestamp").reset_index(drop=True)

    # -----------------------------
    # 3. Create time features
    # -----------------------------
    df["transaction_date"] = df["timestamp"].dt.date
    df["transaction_hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["month"] = df["timestamp"].dt.month
    df["year"] = df["timestamp"].dt.year

    # -----------------------------
    # 4. Validate transaction amount
    # -----------------------------
    df["amount_valid"] = df["amount_inr"] > 0

    # -----------------------------
    # 5. Validate failure reason
    # -----------------------------
    df["failure_reason_valid"] = (
        ((df["status"] == "FAILED") & df["failure_reason"].notna())
        |
        (df["status"] != "FAILED")
    )

    # -----------------------------
    # 6. Create amount categories
    # -----------------------------
    df["amount_category"] = pd.cut(
        df["amount_inr"],
        bins=[0, 500, 2000, 5000, float("inf")],
        labels=[
            "Low",
            "Medium",
            "High",
            "Very High"
        ]
    )

    # -----------------------------
    # 7. Sender transaction history
    # -----------------------------
    df["sender_transaction_count"] = (
        df.groupby("sender_upi_id")["transaction_id"]
        .transform("count")
    )

    df["sender_total_amount"] = (
        df.groupby("sender_upi_id")["amount_inr"]
        .transform("sum")
    )

    df["sender_average_amount"] = (
        df.groupby("sender_upi_id")["amount_inr"]
        .transform("mean")
    )

    df["sender_amount_std"] = (
        df.groupby("sender_upi_id")["amount_inr"]
        .transform("std")
        .fillna(0)
    )

    # -----------------------------
    # 8. Receiver transaction history
    # -----------------------------
    df["receiver_transaction_count"] = (
        df.groupby("receiver_upi_id")["transaction_id"]
        .transform("count")
    )

    df["receiver_total_amount"] = (
        df.groupby("receiver_upi_id")["amount_inr"]
        .transform("sum")
    )

    df["receiver_average_amount"] = (
        df.groupby("receiver_upi_id")["amount_inr"]
        .transform("mean")
    )

    # -----------------------------
    # 9. Remove duplicate transactions
    # -----------------------------
    df = df.drop_duplicates(subset=["transaction_id"])

    return df


if __name__ == "__main__":

    input_file = "data/raw/upi.csv"

    df = pd.read_csv(input_file)

    cleaned_df = transform_data(df)

    output_file = "data/processed/upi_cleaned.csv"

    cleaned_df.to_csv(output_file, index=False)

    print("Transformation completed successfully!")
    print(f"Rows: {len(cleaned_df)}")
    print(f"Columns: {len(cleaned_df.columns)}")
    print(f"Saved to: {output_file}")