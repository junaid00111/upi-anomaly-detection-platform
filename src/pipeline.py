import subprocess
import sys
import time


# ============================================================
# UPI AUTOMATED ANOMALY DETECTION PIPELINE
# ============================================================

print("\n" + "=" * 75)
print("              UPI ANOMALY DETECTION PIPELINE")
print("=" * 75)

start_time = time.time()


# ------------------------------------------------------------
# PIPELINE STAGES
# ------------------------------------------------------------

stages = [
    ("Transforming and cleaning data", "src/transform.py"),
    ("IQR anomaly detection", "src/anomaly_detection.py"),
    ("Isolation Forest", "src/isolation_forest.py"),
    ("Time-series anomaly detection", "src/time_series.py"),
    ("Combining anomaly signals", "src/combine_anomalies.py"),
    ("ML model comparison", "src/ml_models.py"),
    ("Risk scoring", "src/risk_scoring.py"),
    ("Sensitivity analysis", "src/sensitivity_analysis.py"),
    ("Data quality validation", "src/data_quality_check.py"),
    ("PostgreSQL loading", "src/load.py")
]


# ------------------------------------------------------------
# RUN ONE PIPELINE STAGE
# ------------------------------------------------------------

def run_stage(number, total, description, script):

    print("\n")
    print("-" * 75)
    print(f"[{number}/{total}] {description}")
    print("-" * 75)

    try:

        subprocess.run(
            [sys.executable, script],
            check=True
        )

        print(
            f"\n[{number}/{total}] "
            f"{description} → PASS"
        )

        return True

    except subprocess.CalledProcessError as error:

        print("\n" + "!" * 75)
        print(
            f"[{number}/{total}] "
            f"{description} → FAILED"
        )
        print(
            f"Exit code: {error.returncode}"
        )
        print("!" * 75)

        return False

    except FileNotFoundError:

        print("\n" + "!" * 75)
        print(
            f"[{number}/{total}] "
            f"{description} → FAILED"
        )
        print(
            f"Script not found: {script}"
        )
        print("!" * 75)

        return False


# ------------------------------------------------------------
# EXECUTE PIPELINE
# ------------------------------------------------------------

total_stages = len(stages)

for index, (description, script) in enumerate(
    stages,
    start=1
):

    success = run_stage(
        index,
        total_stages,
        description,
        script
    )

    # --------------------------------------------------------
    # STOP PIPELINE IF A STAGE FAILS
    # --------------------------------------------------------

    if not success:

        elapsed = time.time() - start_time

        print("\n")
        print("=" * 75)
        print("                 PIPELINE FAILED")
        print("=" * 75)

        print(
            f"\nFailed stage: {description}"
        )

        print(
            f"Execution time: "
            f"{elapsed:.2f} seconds"
        )

        print(
            "\nPostgreSQL loading was stopped."
        )

        print(
            "Fix the failed stage and run the "
            "pipeline again."
        )

        print("=" * 75)

        sys.exit(1)


# ------------------------------------------------------------
# PIPELINE SUCCESS
# ------------------------------------------------------------

elapsed = time.time() - start_time

print("\n")
print("=" * 75)
print("              PIPELINE COMPLETED SUCCESSFULLY")
print("=" * 75)

print(
    f"\nTotal stages completed: "
    f"{total_stages}/{total_stages}"
)

print(
    f"Execution time: "
    f"{elapsed:.2f} seconds"
)

print("\nMain output:")
print(
    "data/processed/upi_risk_scores.csv"
)

print("\nDatabase:")
print("upi_anomaly_db")

print("\nStatus:")
print(
    "DATA PROCESSED → "
    "ANALYZED → "
    "SCORED → "
    "VALIDATED → "
    "LOADED"
)

print("\n" + "=" * 75)