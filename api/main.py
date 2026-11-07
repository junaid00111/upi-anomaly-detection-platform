import os
from typing import Optional, Literal
from pydantic import BaseModel, Field

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(
    title="UPI Risk Monitoring API",
    description="API for UPI transaction anomaly and risk analytics",
    version="1.0.0",
)

class ThresholdSettings(BaseModel):
    low_threshold: float = Field(ge=0, le=100)
    medium_threshold: float = Field(ge=0, le=100)
    high_threshold: float = Field(ge=0, le=100)

class InvestigationUpdate(BaseModel):
    status: Literal["New", "In Review", "Escalated", "Resolved", "Dismissed"]
    assignee: Optional[str] = Field(default=None, max_length=120)
    notes: Optional[str] = Field(default=None, max_length=5000)
    resolution_reason: Optional[str] = Field(default=None, max_length=255)

# ------------------------------------------------------------
# CORS
# ------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:8081",
    "http://127.0.0.1:8081",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------
# DATABASE CONNECTION
# ------------------------------------------------------------

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


# ------------------------------------------------------------
# HEALTH CHECK
# ------------------------------------------------------------

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "UPI Risk Monitoring API",
        "version": "1.0.0",
    }


@app.get("/api/health")
def health_check():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM upi_transactions;")
        count = cursor.fetchone()[0]

        return {
            "status": "healthy",
            "database": "connected",
            "transactions": count,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}",
        )

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ------------------------------------------------------------
# EXECUTIVE SUMMARY
# ------------------------------------------------------------

@app.get("/api/alerts/count")
def get_alert_count():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM upi_transactions WHERE risk_level IN ('High', 'Critical')")
            return {"count": cursor.fetchone()[0]}
    finally:
        connection.close()

@app.get("/api/data-quality")
def get_data_quality():
    connection = get_connection()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT COUNT(*) AS rows, COUNT(DISTINCT transaction_id) AS unique_ids,
                COUNT(*) FILTER (WHERE amount_inr IS NULL OR amount_inr <= 0) AS invalid_amounts,
                COUNT(*) FILTER (WHERE timestamp IS NULL) AS invalid_timestamps,
                COUNT(*) FILTER (WHERE status IS NULL OR status NOT IN ('SUCCESS','FAILED','PENDING')) AS invalid_statuses,
                COUNT(*) FILTER (WHERE risk_score IS NULL OR risk_score < 0 OR risk_score > 100) AS invalid_scores
                FROM upi_transactions
            """)
            row = dict(cursor.fetchone())
            total = int(row["rows"] or 0)
            duplicate_count = total - int(row["unique_ids"] or 0)
            defects = duplicate_count + sum(int(row[k] or 0) for k in ("invalid_amounts", "invalid_timestamps", "invalid_statuses", "invalid_scores"))
            row.update({"duplicate_ids": duplicate_count, "quality_percent": round(max(0, 100 * (1 - defects / max(total, 1))), 2)})
            return row
    finally:
        connection.close()

@app.get("/api/settings/thresholds")
def get_thresholds():
    connection = get_connection()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT low_threshold, medium_threshold, high_threshold FROM monitoring_settings WHERE id = 1")
            return dict(cursor.fetchone())
    finally:
        connection.close()

@app.put("/api/settings/thresholds")
def save_thresholds(settings: ThresholdSettings):
    if not settings.low_threshold < settings.medium_threshold < settings.high_threshold:
        raise HTTPException(status_code=422, detail="Thresholds must be in ascending order")
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""UPDATE monitoring_settings SET low_threshold=%s, medium_threshold=%s, high_threshold=%s, updated_at=CURRENT_TIMESTAMP WHERE id=1""", (settings.low_threshold, settings.medium_threshold, settings.high_threshold))
        connection.commit()
        return settings.model_dump()
    finally:
        connection.close()

@app.patch("/api/investigations/{transaction_id}")
def update_investigation(transaction_id: str, update: InvestigationUpdate):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM upi_transactions WHERE transaction_id=%s", (transaction_id,))
            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail="Transaction not found")
            cursor.execute("""INSERT INTO investigation_cases(transaction_id,status,assignee,notes,resolution_reason) VALUES(%s,%s,%s,%s,%s) ON CONFLICT(transaction_id) DO UPDATE SET status=EXCLUDED.status, assignee=EXCLUDED.assignee, notes=EXCLUDED.notes, resolution_reason=EXCLUDED.resolution_reason, updated_at=CURRENT_TIMESTAMP""", (transaction_id, update.status, update.assignee, update.notes, update.resolution_reason))
            cursor.execute("INSERT INTO investigation_events(transaction_id,event_type,details,actor) VALUES(%s,%s,%s,%s)", (transaction_id, update.status, update.notes or update.resolution_reason, update.assignee))
        connection.commit()
        return {"transaction_id": transaction_id, **update.model_dump()}
    finally:
        connection.close()

@app.get("/api/summary")
def get_summary():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                COUNT(*) AS total_transactions,
                COALESCE(SUM(amount_inr), 0) AS total_value,
                COALESCE(AVG(amount_inr), 0) AS average_amount,
                COALESCE(AVG(risk_score), 0) AS average_risk_score,

                COUNT(*) FILTER (
                    WHERE anomaly_count > 0
                ) AS anomalous_transactions,

                ROUND(
                    100.0 * COUNT(*) FILTER (
                        WHERE anomaly_count > 0
                    ) / NULLIF(COUNT(*), 0),
                    2
                ) AS anomaly_rate,

                COUNT(*) FILTER (
                    WHERE risk_level IN ('High', 'Critical')
                ) AS investigation_required

            FROM upi_transactions;
        """

        cursor.execute(query)
        result = cursor.fetchone()

        return {
            "total_transactions": int(result["total_transactions"]),
            "total_value": float(result["total_value"]),
            "average_amount": float(result["average_amount"]),
            "average_risk_score": float(result["average_risk_score"]),
            "anomalous_transactions": int(result["anomalous_transactions"]),
            "anomaly_rate": float(result["anomaly_rate"]),
            "investigation_required": int(result["investigation_required"]),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ------------------------------------------------------------
# RISK LEVEL DISTRIBUTION
# ------------------------------------------------------------

@app.get("/api/risk-levels")
def get_risk_levels():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                risk_level,
                COUNT(*) AS transaction_count
            FROM upi_transactions
            GROUP BY risk_level
            ORDER BY
                CASE risk_level
                    WHEN 'Critical' THEN 1
                    WHEN 'High' THEN 2
                    WHEN 'Medium' THEN 3
                    WHEN 'Low' THEN 4
                    ELSE 5
                END;
        """

        cursor.execute(query)

        results = cursor.fetchall()

        return [
            {
                "risk_level": row["risk_level"],
                "transaction_count": int(row["transaction_count"]),
            }
            for row in results
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ------------------------------------------------------------
# TRANSACTIONS
# ------------------------------------------------------------

@app.get("/api/transactions")
def get_transactions(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    risk_level: Optional[str] = None,
    search: Optional[str] = None,
    state: Optional[str] = None,
    app: Optional[str] = None,
    category: Optional[str] = None,
):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
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

                anomaly_count,
                anomaly_type,
                iqr_anomaly,
                time_series_anomaly,
                isolation_forest_new,
                lof_anomaly,
                one_class_svm_anomaly,
                ml_model_agreement,

                risk_signal_count,
                risk_score,
                risk_level,
                investigation_required

            FROM upi_transactions
        """

        conditions = []
        parameters = []

        # ----------------------------------------------------
        # RISK FILTER
        # ----------------------------------------------------

        if risk_level and risk_level != "All risks":
            conditions.append("risk_level = %s")
            parameters.append(risk_level)

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        if search:
            search_pattern = f"%{search.strip()}%"

            conditions.append("""
                (
                    transaction_id ILIKE %s
                    OR sender_name ILIKE %s
                    OR sender_upi_id ILIKE %s
                    OR receiver_name ILIKE %s
                    OR receiver_upi_id ILIKE %s
                    OR category ILIKE %s
                    OR upi_app ILIKE %s
                    OR location_state ILIKE %s
                    OR transaction_type ILIKE %s
                    OR anomaly_type ILIKE %s
                )
            """)

            parameters.extend([
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern,
            ])

        # ----------------------------------------------------
        # STATE FILTER
        # ----------------------------------------------------

        if state and state != "All states":
            conditions.append("location_state = %s")
            parameters.append(state)

        # ----------------------------------------------------
        # UPI APP FILTER
        # ----------------------------------------------------

        if app and app != "All apps":
            conditions.append("upi_app = %s")
            parameters.append(app)

        # ----------------------------------------------------
        # CATEGORY FILTER
        # ----------------------------------------------------

        if category and category != "All categories":
            conditions.append("category = %s")
            parameters.append(category)

        # ----------------------------------------------------
        # WHERE CLAUSE
        # ----------------------------------------------------

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # ----------------------------------------------------
        # ORDER + PAGINATION
        # ----------------------------------------------------

        query += """
            ORDER BY timestamp DESC
            LIMIT %s
            OFFSET %s
        """

        parameters.extend([limit, offset])

        cursor.execute(query, parameters)

        rows = cursor.fetchall()

        # ----------------------------------------------------
        # TOTAL MATCHING RECORDS
        # ----------------------------------------------------

        count_query = """
            SELECT COUNT(*) AS total
            FROM upi_transactions
        """

        count_parameters = []

        if conditions:
            count_query += " WHERE " + " AND ".join(conditions)

            # Remove LIMIT/OFFSET parameters.
            # The filter parameters are the first parameters.
            count_parameters = parameters[:-2]

        cursor.execute(
            count_query,
            count_parameters,
        )

        total = cursor.fetchone()["total"]

        # ----------------------------------------------------
        # FORMAT TRANSACTIONS
        # ----------------------------------------------------

        transactions = []

        for row in rows:
            transaction = dict(row)

            if transaction.get("timestamp"):
                transaction["timestamp"] = (
                    transaction["timestamp"].isoformat()
                )

            for key, value in transaction.items():
                if value is not None and hasattr(value, "item"):
                    transaction[key] = value.item()

            transactions.append(transaction)

        return {
            "count": len(transactions),
            "total": int(total),
            "limit": limit,
            "offset": offset,
            "transactions": transactions,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ------------------------------------------------------------
# ANOMALY DETECTION METHODS
# ------------------------------------------------------------

@app.get("/api/anomalies")
def get_anomaly_methods():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                COUNT(*) FILTER (
                    WHERE iqr_anomaly = 1
                ) AS iqr,

                COUNT(*) FILTER (
                    WHERE time_series_anomaly = 1
                ) AS time_series,

                COUNT(*) FILTER (
                    WHERE isolation_forest_new = 1
                ) AS isolation_forest,

                COUNT(*) FILTER (
                    WHERE lof_anomaly = 1
                ) AS lof,

                COUNT(*) FILTER (
                    WHERE one_class_svm_anomaly = 1
                ) AS one_class_svm

            FROM upi_transactions;
        """

        cursor.execute(query)
        result = cursor.fetchone()

        return {
            "iqr": int(result["iqr"]),
            "time_series": int(result["time_series"]),
            "isolation_forest": int(result["isolation_forest"]),
            "lof": int(result["lof"]),
            "one_class_svm": int(result["one_class_svm"]),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ------------------------------------------------------------
# CATEGORY ANALYTICS
# ------------------------------------------------------------

@app.get("/api/analytics/categories")
def get_category_analytics():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                category,
                COUNT(*) AS total_transactions,
                COUNT(*) FILTER (
                    WHERE anomaly_count > 0
                ) AS anomalous_transactions,

                ROUND(
                    100.0 * COUNT(*) FILTER (
                        WHERE anomaly_count > 0
                    ) / NULLIF(COUNT(*), 0),
                    2
                ) AS anomaly_rate,

                ROUND(
                    AVG(amount_inr),
                    2
                ) AS average_amount

            FROM upi_transactions
            GROUP BY category
            ORDER BY anomaly_rate DESC;
        """

        cursor.execute(query)

        results = cursor.fetchall()

        return [dict(row) for row in results]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ------------------------------------------------------------
# UPI APP ANALYTICS
# ------------------------------------------------------------

@app.get("/api/analytics/apps")
def get_app_analytics():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                upi_app,
                COUNT(*) AS total_transactions,
                COUNT(*) FILTER (
                    WHERE anomaly_count > 0
                ) AS anomalous_transactions,

                ROUND(
                    100.0 * COUNT(*) FILTER (
                        WHERE anomaly_count > 0
                    ) / NULLIF(COUNT(*), 0),
                    2
                ) AS anomaly_rate

            FROM upi_transactions
            GROUP BY upi_app
            ORDER BY anomaly_rate DESC;
        """

        cursor.execute(query)

        results = cursor.fetchall()

        return [dict(row) for row in results]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ------------------------------------------------------------
# DAILY TRANSACTION ANALYTICS
# ------------------------------------------------------------

@app.get("/api/analytics/daily")
def get_daily_analytics():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                DATE(timestamp) AS transaction_date,
                COUNT(*) AS transaction_count,
                ROUND(
                    SUM(amount_inr),
                    2
                ) AS total_amount,

                COUNT(*) FILTER (
                    WHERE anomaly_count > 0
                ) AS anomalous_transactions

            FROM upi_transactions

            GROUP BY DATE(timestamp)

            ORDER BY transaction_date;
        """

        cursor.execute(query)

        results = cursor.fetchall()

        data = []

        for row in results:
            item = dict(row)

            if item["transaction_date"]:
                item["transaction_date"] = item[
                    "transaction_date"
                ].isoformat()

            data.append(item)

        return data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ------------------------------------------------------------
# HIGH-RISK INVESTIGATION QUEUE
# ------------------------------------------------------------

@app.get("/api/investigations")
def get_investigations(
    limit: int = Query(100, ge=1, le=1000)
):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                transaction_id,
                timestamp,
                amount_inr,
                risk_score,
                risk_level,
                risk_signal_count,
                anomaly_type,
                iqr_anomaly,
                time_series_anomaly,
                isolation_forest_new,
                lof_anomaly,
                one_class_svm_anomaly,
                ml_model_agreement,
                transaction_type,
                category,
                upi_app,
                location_state,
                status,
                investigation_required

            FROM upi_transactions

            WHERE risk_level IN ('High', 'Critical')

            ORDER BY
                CASE risk_level
                    WHEN 'Critical' THEN 1
                    WHEN 'High' THEN 2
                    ELSE 3
                END,
                risk_score DESC

            LIMIT %s;
        """

        cursor.execute(query, (limit,))

        results = cursor.fetchall()

        data = []

        for row in results:
            item = dict(row)

            if item.get("timestamp"):
                item["timestamp"] = item["timestamp"].isoformat()

            data.append(item)

        return {
            "count": len(data),
            "transactions": data,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            
            
            # ------------------------------------------------------------
# ML MODEL AGREEMENT
# ------------------------------------------------------------

@app.get("/api/analytics/model-agreement")
def get_model_agreement():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                ml_model_agreement,
                COUNT(*) AS transaction_count
            FROM upi_transactions
            GROUP BY ml_model_agreement
            ORDER BY ml_model_agreement;
        """

        cursor.execute(query)

        results = cursor.fetchall()

        agreement_0 = 0
        agreement_1 = 0
        agreement_2 = 0
        agreement_3 = 0

        for row in results:
            agreement = row["ml_model_agreement"]
            count = int(row["transaction_count"])

            if agreement == 0:
                agreement_0 = count
            elif agreement == 1:
                agreement_1 = count
            elif agreement == 2:
                agreement_2 = count
            elif agreement == 3:
                agreement_3 = count

        return [
            {
                "name": "0 models agree",
                "value": agreement_0,
            },
            {
                "name": "1 model agrees",
                "value": agreement_1,
            },
            {
                "name": "2 models agree",
                "value": agreement_2,
            },
            {
                "name": "All 3 agree",
                "value": agreement_3,
            },
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ------------------------------------------------------------
# RISK SIGNAL DISTRIBUTION
# ------------------------------------------------------------

@app.get("/api/analytics/signal-distribution")
def get_signal_distribution():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                risk_signal_count,
                COUNT(*) AS transaction_count
            FROM upi_transactions
            GROUP BY risk_signal_count
            ORDER BY risk_signal_count;
        """

        cursor.execute(query)

        results = cursor.fetchall()

        return [
            {
                "name": f"{int(row['risk_signal_count'])} signals",
                "value": int(row["transaction_count"]),
            }
            for row in results
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ------------------------------------------------------------
# HIGH / CRITICAL RISK BY CATEGORY
# ------------------------------------------------------------

@app.get("/api/analytics/high-risk-categories")
def get_high_risk_categories():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                category,

                COUNT(*) FILTER (
                    WHERE risk_level = 'High'
                ) AS high,

                COUNT(*) FILTER (
                    WHERE risk_level = 'Critical'
                ) AS critical

            FROM upi_transactions

            WHERE risk_level IN ('High', 'Critical')

            GROUP BY category

            ORDER BY
                (
                    COUNT(*) FILTER (
                        WHERE risk_level = 'High'
                    )
                    +
                    COUNT(*) FILTER (
                        WHERE risk_level = 'Critical'
                    )
                ) DESC;
        """

        cursor.execute(query)

        results = cursor.fetchall()

        return [
            {
                "name": row["category"],
                "high": int(row["high"]),
                "critical": int(row["critical"]),
            }
            for row in results
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            
# ------------------------------------------------------------
# AMOUNT BAND ANALYTICS
# ------------------------------------------------------------

@app.get("/api/analytics/amount-bands")
def get_amount_bands():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                CASE
                    WHEN amount_inr < 500 THEN '< ₹500'
                    WHEN amount_inr < 1000 THEN '₹500–₹1K'
                    WHEN amount_inr < 3000 THEN '₹1K–₹3K'
                    WHEN amount_inr < 5000 THEN '₹3K–₹5K'
                    WHEN amount_inr < 10000 THEN '₹5K–₹10K'
                    ELSE '₹10K+'
                END AS name,
                COUNT(*) AS count
            FROM upi_transactions
            GROUP BY
                CASE
                    WHEN amount_inr < 500 THEN '< ₹500'
                    WHEN amount_inr < 1000 THEN '₹500–₹1K'
                    WHEN amount_inr < 3000 THEN '₹1K–₹3K'
                    WHEN amount_inr < 5000 THEN '₹3K–₹5K'
                    WHEN amount_inr < 10000 THEN '₹5K–₹10K'
                    ELSE '₹10K+'
                END
            ORDER BY
                CASE
                    WHEN MIN(amount_inr) < 500 THEN 1
                    WHEN MIN(amount_inr) < 1000 THEN 2
                    WHEN MIN(amount_inr) < 3000 THEN 3
                    WHEN MIN(amount_inr) < 5000 THEN 4
                    WHEN MIN(amount_inr) < 10000 THEN 5
                    ELSE 6
                END;
        """

        cursor.execute(query)
        results = cursor.fetchall()

        return [
            {
                "name": row["name"],
                "count": int(row["count"]),
            }
            for row in results
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ------------------------------------------------------------
# STATE ANALYTICS
# ------------------------------------------------------------

@app.get("/api/analytics/states")
def get_state_analytics():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                location_state AS name,
                COUNT(*) AS transactions,

                ROUND(
                    100.0 * COUNT(*) FILTER (
                        WHERE anomaly_count > 0
                    ) / NULLIF(COUNT(*), 0),
                    2
                ) AS rate

            FROM upi_transactions

            GROUP BY location_state

            ORDER BY transactions DESC;
        """

        cursor.execute(query)
        results = cursor.fetchall()

        return [
            {
                "name": row["name"],
                "transactions": int(row["transactions"]),
                "rate": float(row["rate"] or 0),
            }
            for row in results
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()