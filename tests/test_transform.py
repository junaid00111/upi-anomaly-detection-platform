"""Tests for the data transformation stage (src/transform.py)."""

from datetime import datetime

import pandas as pd
import pytest

from src.transform import transform_data

# Columns as produced by generate_upi_data.py
RAW_COLUMNS = [
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
]


def make_row(**overrides):
    """Return a valid raw transaction row (dict)."""
    row = {
        "transaction_id": "UPI2024011000000001",
        "timestamp": "2024-01-10 12:30:00",
        "sender_name": "Aarav Sharma",
        "sender_upi_id": "aarav.sharma10@okhdfcbank",
        "sender_bank": "HDFC Bank",
        "receiver_name": "Swiggy",
        "receiver_upi_id": "swiggy@ybl",
        "receiver_bank": "Yes Bank",
        "amount_inr": 450.50,
        "transaction_type": "P2M",
        "category": "Food & Dining",
        "upi_app": "Google Pay",
        "device_os": "Android",
        "location_state": "Maharashtra",
        "status": "SUCCESS",
        "failure_reason": "",
    }
    row.update(overrides)
    return row


def make_df(rows):
    return pd.DataFrame(rows, columns=RAW_COLUMNS)


def test_transform_adds_expected_columns():
    df = transform_data(make_df([make_row()]))

    expected_columns = {
        "transaction_date",
        "transaction_hour",
        "day_of_week",
        "month",
        "year",
        "amount_valid",
        "failure_reason_valid",
        "amount_category",
        "sender_transaction_count",
        "sender_total_amount",
        "sender_average_amount",
        "sender_amount_std",
        "receiver_transaction_count",
        "receiver_total_amount",
        "receiver_average_amount",
    }

    assert expected_columns.issubset(df.columns)


def test_transform_parses_and_sorts_timestamps():
    rows = [
        make_row(
            transaction_id="UPI002",
            timestamp="2024-01-10 12:30:00",
        ),
        make_row(
            transaction_id="UPI001",
            timestamp="2024-01-09 08:15:00",
        ),
    ]

    df = transform_data(make_df(rows))

    assert list(df["transaction_id"]) == ["UPI001", "UPI002"]
    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])


def test_transform_extracts_time_features():
    df = transform_data(make_df([
        make_row(timestamp="2024-01-10 12:30:00"),
    ]))

    assert df.loc[0, "transaction_hour"] == 12
    assert df.loc[0, "month"] == 1
    assert df.loc[0, "year"] == 2024
    # 2024-01-10 was a Wednesday
    assert df.loc[0, "day_of_week"] == 2


def test_transform_validates_amount():
    bad = transform_data(make_df([
        make_row(amount_inr=0),
    ]))
    assert not bad.loc[0, "amount_valid"]

    good = transform_data(make_df([
        make_row(amount_inr=500.0),
    ]))
    assert good.loc[0, "amount_valid"]


def test_transform_validates_failure_reason():
    # FAILED without a reason (NaN) -> invalid
    failed_no_reason = transform_data(make_df([
        make_row(status="FAILED", failure_reason=None),
    ]))
    assert not failed_no_reason.loc[0, "failure_reason_valid"]

    # FAILED with a reason -> valid
    failed_with_reason = transform_data(make_df([
        make_row(status="FAILED", failure_reason="Insufficient balance"),
    ]))
    assert failed_with_reason.loc[0, "failure_reason_valid"]

    # Non-FAILED -> always valid
    success = transform_data(make_df([
        make_row(status="SUCCESS", failure_reason=""),
    ]))
    assert success.loc[0, "failure_reason_valid"]


def test_transform_buckets_amount_category():
    df = transform_data(make_df([
        make_row(transaction_id="UPI001", amount_inr=300.0),    # Low
        make_row(transaction_id="UPI002", amount_inr=1000.0),   # Medium
        make_row(transaction_id="UPI003", amount_inr=3000.0),   # High
        make_row(transaction_id="UPI004", amount_inr=10000.0),  # Very High
    ]))

    categories = df["amount_category"].tolist()
    assert categories == ["Low", "Medium", "High", "Very High"]


def test_transform_computes_sender_history():
    rows = [
        make_row(
            transaction_id="UPI001",
            sender_upi_id="sender@okhdfcbank",
            amount_inr=100.0,
        ),
        make_row(
            transaction_id="UPI002",
            sender_upi_id="sender@okhdfcbank",
            amount_inr=300.0,
        ),
        make_row(
            transaction_id="UPI003",
            sender_upi_id="other@ybl",
            amount_inr=50.0,
        ),
    ]

    df = transform_data(make_df(rows))

    # Sender "sender@okhdfcbank" sent 2 transactions totalling 400
    sender_rows = df[df["sender_upi_id"] == "sender@okhdfcbank"]
    assert set(sender_rows["sender_transaction_count"]) == {2}
    assert set(sender_rows["sender_total_amount"]) == {400.0}
    assert set(sender_rows["sender_average_amount"]) == {200.0}


def test_transform_removes_duplicate_transactions():
    rows = [
        make_row(transaction_id="UPI001"),
        make_row(transaction_id="UPI002"),
        make_row(transaction_id="UPI002"),  # duplicate
    ]

    df = transform_data(make_df(rows))

    assert len(df) == 2
    assert df["transaction_id"].is_unique


def test_transform_returns_copy_not_mutation():
    source = make_df([make_row()])
    _ = transform_data(source)

    assert "transaction_date" not in source.columns
    assert list(source.columns) == RAW_COLUMNS
