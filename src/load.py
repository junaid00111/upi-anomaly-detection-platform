import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values


# ============================================================
# UPI POSTGRESQL LOAD
# ============================================================

load_dotenv()


# ------------------------------------------------------------
# DATABASE CONNECTION
# ------------------------------------------------------------

def get_connection():
    """Create PostgreSQL database connection."""

    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

def load_data():

    input_file = "data/processed/upi_risk_scores.csv"

    print("\nLoading master risk dataset:")
    print(input_file)

    # --------------------------------------------------------
    # READ DATA
    # --------------------------------------------------------

    df = pd.read_csv(input_file)

    print(f"Transactions to load: {len(df):,}")

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )


    # --------------------------------------------------------
    # CONNECT TO POSTGRESQL
    # --------------------------------------------------------

    connection = get_connection()
    cursor = connection.cursor()

    print("Connected to PostgreSQL")


    # --------------------------------------------------------
    # ENSURE REQUIRED COLUMNS EXIST
    # --------------------------------------------------------

    print("\nChecking PostgreSQL schema...")

    alter_query = """
        ALTER TABLE upi_transactions

        ADD COLUMN IF NOT EXISTS isolation_forest_new INTEGER,

        ADD COLUMN IF NOT EXISTS lof_anomaly INTEGER,

        ADD COLUMN IF NOT EXISTS one_class_svm_anomaly INTEGER,

        ADD COLUMN IF NOT EXISTS ml_model_agreement INTEGER,

        ADD COLUMN IF NOT EXISTS risk_signal_count INTEGER,

        ADD COLUMN IF NOT EXISTS risk_score NUMERIC(6, 2),

        ADD COLUMN IF NOT EXISTS risk_level VARCHAR(30),

        ADD COLUMN IF NOT EXISTS investigation_required VARCHAR(10);
    """

    cursor.execute(alter_query)

    connection.commit()

    print("Database schema checked.")


    # --------------------------------------------------------
    # COLUMNS REQUIRED FROM MASTER DATASET
    # --------------------------------------------------------

    columns = [

        "transaction_id",
        "timestamp",

        "sender_name",
        "sender_upi_id",
        "sender_bank",

        "receiver_name",
        "receiver_upi_id",
        "receiver_bank",

        "amount_inr",
        "transaction_type",
        "category",
        "upi_app",
        "device_os",
        "location_state",

        "status",
        "failure_reason",

        "iqr_anomaly",
        "isolation_forest_anomaly",
        "isolation_forest_score",

        "time_series_volume_anomaly",
        "time_series_amount_anomaly",
        "time_series_anomaly",

        "anomaly_count",
        "anomaly_type",

        "isolation_forest_new",
        "lof_anomaly",
        "one_class_svm_anomaly",

        "ml_model_agreement",

        "risk_signal_count",
        "risk_score",
        "risk_level",
        "investigation_required"
    ]


    # --------------------------------------------------------
    # CHECK INPUT COLUMNS
    # --------------------------------------------------------

    missing_columns = [
        column
        for column in columns
        if column not in df.columns
    ]

    if missing_columns:

        print("\nERROR: Missing columns in input dataset:")

        for column in missing_columns:
            print(f"  - {column}")

        cursor.close()
        connection.close()

        raise ValueError(
            "Input dataset does not contain all "
            "required PostgreSQL columns."
        )


    # --------------------------------------------------------
    # UPSERT QUERY
    # --------------------------------------------------------

    insert_query = """
        INSERT INTO upi_transactions (

            transaction_id,
            timestamp,

            sender_name,
            sender_upi_id,
            sender_bank,

            receiver_name,
            receiver_upi_id,
            receiver_bank,

            amount_inr,
            transaction_type,
            category,
            upi_app,
            device_os,
            location_state,

            status,
            failure_reason,

            iqr_anomaly,
            isolation_forest_anomaly,
            isolation_forest_score,

            time_series_volume_anomaly,
            time_series_amount_anomaly,
            time_series_anomaly,

            anomaly_count,
            anomaly_type,

            isolation_forest_new,
            lof_anomaly,
            one_class_svm_anomaly,

            ml_model_agreement,

            risk_signal_count,
            risk_score,
            risk_level,
            investigation_required

        )

        VALUES %s

        ON CONFLICT (transaction_id)

        DO UPDATE SET

            timestamp = EXCLUDED.timestamp,

            sender_name = EXCLUDED.sender_name,
            sender_upi_id = EXCLUDED.sender_upi_id,
            sender_bank = EXCLUDED.sender_bank,

            receiver_name = EXCLUDED.receiver_name,
            receiver_upi_id = EXCLUDED.receiver_upi_id,
            receiver_bank = EXCLUDED.receiver_bank,

            amount_inr = EXCLUDED.amount_inr,
            transaction_type = EXCLUDED.transaction_type,
            category = EXCLUDED.category,
            upi_app = EXCLUDED.upi_app,
            device_os = EXCLUDED.device_os,
            location_state = EXCLUDED.location_state,

            status = EXCLUDED.status,
            failure_reason = EXCLUDED.failure_reason,

            iqr_anomaly = EXCLUDED.iqr_anomaly,

            isolation_forest_anomaly =
                EXCLUDED.isolation_forest_anomaly,

            isolation_forest_score =
                EXCLUDED.isolation_forest_score,

            time_series_volume_anomaly =
                EXCLUDED.time_series_volume_anomaly,

            time_series_amount_anomaly =
                EXCLUDED.time_series_amount_anomaly,

            time_series_anomaly =
                EXCLUDED.time_series_anomaly,

            anomaly_count =
                EXCLUDED.anomaly_count,

            anomaly_type =
                EXCLUDED.anomaly_type,

            isolation_forest_new =
                EXCLUDED.isolation_forest_new,

            lof_anomaly =
                EXCLUDED.lof_anomaly,

            one_class_svm_anomaly =
                EXCLUDED.one_class_svm_anomaly,

            ml_model_agreement =
                EXCLUDED.ml_model_agreement,

            risk_signal_count =
                EXCLUDED.risk_signal_count,

            risk_score =
                EXCLUDED.risk_score,

            risk_level =
                EXCLUDED.risk_level,

            investigation_required =
                EXCLUDED.investigation_required;
    """


    # --------------------------------------------------------
    # PREPARE RECORDS
    # --------------------------------------------------------

    records = []

    for row in df[columns].itertuples(
        index=False,
        name=None
    ):

        cleaned_row = tuple(
            None if pd.isna(value)
            else value
            for value in row
        )

        records.append(cleaned_row)


    # --------------------------------------------------------
    # UPSERT DATA
    # --------------------------------------------------------

    print(
        f"\nUpserting {len(records):,} transactions..."
    )

    execute_values(
        cursor,
        insert_query,
        records,
        page_size=1000
    )

    connection.commit()


    # --------------------------------------------------------
    # VERIFY DATABASE COUNT
    # --------------------------------------------------------

    cursor.execute(
        "SELECT COUNT(*) FROM upi_transactions;"
    )

    database_count = cursor.fetchone()[0]

    print(
        f"\nPostgreSQL transaction count: "
        f"{database_count:,}"
    )


    # --------------------------------------------------------
    # VERIFY RISK COLUMNS
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            COUNT(*) AS total,
            COUNT(risk_score) AS risk_scores,
            COUNT(risk_level) AS risk_levels,
            COUNT(investigation_required)
                AS investigation_flags
        FROM upi_transactions;
        """
    )

    verification = cursor.fetchone()

    print("\nRisk column verification:")

    print(
        f"Total rows: "
        f"{verification[0]:,}"
    )

    print(
        f"Risk scores populated: "
        f"{verification[1]:,}"
    )

    print(
        f"Risk levels populated: "
        f"{verification[2]:,}"
    )

    print(
        f"Investigation flags populated: "
        f"{verification[3]:,}"
    )


    # --------------------------------------------------------
    # CLOSE CONNECTION
    # --------------------------------------------------------

    cursor.close()
    connection.close()

    print("\nDatabase connection closed.")

    print(
        "\nPostgreSQL load completed successfully."
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    load_data()