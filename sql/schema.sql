CREATE TABLE IF NOT EXISTS upi_transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    timestamp TIMESTAMP,
    sender_name VARCHAR(100),
    sender_upi_id VARCHAR(150),
    sender_bank VARCHAR(100),
    receiver_name VARCHAR(100),
    receiver_upi_id VARCHAR(150),
    receiver_bank VARCHAR(100),
    amount_inr NUMERIC(12, 2),
    transaction_type VARCHAR(50),
    category VARCHAR(100),
    upi_app VARCHAR(50),
    device_os VARCHAR(50),
    location_state VARCHAR(100),
    status VARCHAR(30),
    failure_reason VARCHAR(255),
    iqr_anomaly INTEGER,
    isolation_forest_anomaly INTEGER,
    isolation_forest_score NUMERIC,
    time_series_volume_anomaly INTEGER,
    time_series_amount_anomaly INTEGER,
    time_series_anomaly INTEGER,
    anomaly_count INTEGER,
    anomaly_type VARCHAR(50),
    isolation_forest_new INTEGER,
    lof_anomaly INTEGER,
    one_class_svm_anomaly INTEGER,
    ml_model_agreement INTEGER,
    risk_signal_count INTEGER,
    risk_score NUMERIC(6, 2),
    risk_level VARCHAR(30),
    investigation_required VARCHAR(10)
);

CREATE INDEX IF NOT EXISTS idx_upi_timestamp
    ON upi_transactions (timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_upi_risk_level
    ON upi_transactions (risk_level);

CREATE INDEX IF NOT EXISTS idx_upi_category
    ON upi_transactions (category);

CREATE INDEX IF NOT EXISTS idx_upi_app
    ON upi_transactions (upi_app);

CREATE INDEX IF NOT EXISTS idx_upi_state
    ON upi_transactions (location_state);
