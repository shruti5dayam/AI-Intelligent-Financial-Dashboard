"""
Validation utilities for mapped financial transactions.

Responsibilities:
- Count total transactions
- Count mapped and unmatched transactions
- Count missing COA mappings
- Detect invalid amounts
- Produce a validation summary for dashboard KPIs
"""

from __future__ import annotations

from typing import Any

import pandas as pd


def safe_percentage(numerator: int | float, denominator: int | float) -> float:
    """
    Calculate percentage safely.

    Parameters
    ----------
    numerator:
        Top value in the percentage calculation.

    denominator:
        Bottom value in the percentage calculation.

    Returns
    -------
    float
        Percentage value. Returns 0.0 if denominator is zero.
    """

    if denominator == 0:
        return 0.0

    return round((numerator / denominator) * 100, 2)


def count_invalid_amounts(df: pd.DataFrame) -> int:
    """
    Count rows where Amount is missing or cannot be interpreted as numeric.

    Parameters
    ----------
    df:
        Transaction DataFrame.

    Returns
    -------
    int
        Number of rows with invalid Amount values.
    """

    if df.empty or "Amount" not in df.columns:
        return 0

    numeric_amounts = pd.to_numeric(df["Amount"], errors="coerce")

    return int(numeric_amounts.isna().sum())


def get_unmatched_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return transactions that were not mapped by any rule.

    Parameters
    ----------
    df:
        Mapped transaction DataFrame.

    Returns
    -------
    pd.DataFrame
        Transactions with Mapping Status equal to Unmatched.
    """

    if df.empty or "Mapping Status" not in df.columns:
        return pd.DataFrame()

    return df[df["Mapping Status"] == "Unmatched"].copy()


def get_missing_coa_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return transactions that were mapped by rules but not found in the COA.

    Parameters
    ----------
    df:
        COA-enriched transaction DataFrame.

    Returns
    -------
    pd.DataFrame
        Transactions missing Chart of Accounts mapping.
    """

    if df.empty or "COA Mapping Status" not in df.columns:
        return pd.DataFrame()

    return df[df["COA Mapping Status"] == "Missing COA Mapping"].copy()


def validate_transactions(df: pd.DataFrame) -> dict[str, Any]:
    """
    Create a validation summary for mapped financial transactions.

    Parameters
    ----------
    df:
        Final mapped and COA-enriched transaction DataFrame.

    Returns
    -------
    dict[str, Any]
        Validation summary used by the dashboard.
    """

    total_transactions = len(df)

    if total_transactions == 0:
        return {
            "total_transactions": 0,
            "mapped_transactions": 0,
            "unmatched_transactions": 0,
            "missing_coa_mappings": 0,
            "invalid_amounts": 0,
            "mapping_percentage": 0.0,
            "coa_mapping_percentage": 0.0,
        }

    unmatched_df = get_unmatched_transactions(df)
    missing_coa_df = get_missing_coa_transactions(df)

    unmatched_count = len(unmatched_df)
    missing_coa_count = len(missing_coa_df)
    invalid_amount_count = count_invalid_amounts(df)

    mapped_count = total_transactions - unmatched_count
    coa_mapped_count = total_transactions - missing_coa_count

    return {
        "total_transactions": total_transactions,
        "mapped_transactions": mapped_count,
        "unmatched_transactions": unmatched_count,
        "missing_coa_mappings": missing_coa_count,
        "invalid_amounts": invalid_amount_count,
        "mapping_percentage": safe_percentage(
            mapped_count,
            total_transactions,
        ),
        "coa_mapping_percentage": safe_percentage(
            coa_mapped_count,
            total_transactions,
        ),
    }