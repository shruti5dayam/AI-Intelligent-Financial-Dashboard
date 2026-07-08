"""
Profit & Loss generator.

Responsibilities:
- Read Trial Balance account totals
- Classify accounts into Income, COGS, and Expenses
- Calculate Gross Profit
- Calculate Net Income
- Return a clean P&L DataFrame
"""

from __future__ import annotations

from typing import Any

import pandas as pd


TRIAL_BALANCE_REQUIRED_COLUMNS = [
    "Account Type",
    "Amount",
]


def normalize_text(value: Any) -> str:
    """
    Normalize text for reliable comparison.

    Parameters
    ----------
    value:
        Any input value.

    Returns
    -------
    str
        Lowercase stripped text.
    """

    if value is None:
        return ""

    return str(value).strip().lower()


def find_missing_columns(
    df: pd.DataFrame,
    required_columns: list[str],
) -> list[str]:
    """
    Find required columns missing from a DataFrame.

    Parameters
    ----------
    df:
        Input DataFrame.

    required_columns:
        Required column names.

    Returns
    -------
    list[str]
        Missing column names.
    """

    return [
        column
        for column in required_columns
        if column not in df.columns
    ]


def is_income_account(account_type: str) -> bool:
    """
    Check whether an account type belongs to income/revenue.

    Parameters
    ----------
    account_type:
        Account type from Trial Balance.

    Returns
    -------
    bool
        True if account type is income-related.
    """

    normalized_type = normalize_text(account_type)

    return (
        "income" in normalized_type
        or "revenue" in normalized_type
        or normalized_type == "sales"
    )


def is_cogs_account(account_type: str) -> bool:
    """
    Check whether an account type belongs to Cost of Goods Sold.

    Parameters
    ----------
    account_type:
        Account type from Trial Balance.

    Returns
    -------
    bool
        True if account type is COGS-related.
    """

    normalized_type = normalize_text(account_type)

    return (
        "cost of goods sold" in normalized_type
        or "cogs" in normalized_type
        or "cost of sales" in normalized_type
    )


def is_expense_account(account_type: str) -> bool:
    """
    Check whether an account type belongs to expenses.

    Parameters
    ----------
    account_type:
        Account type from Trial Balance.

    Returns
    -------
    bool
        True if account type is expense-related.
    """

    normalized_type = normalize_text(account_type)

    return (
        "expense" in normalized_type
        or "expenses" in normalized_type
        or "other expense" in normalized_type
    )


def sum_account_group(
    trial_balance_df: pd.DataFrame,
    classifier,
) -> float:
    """
    Sum Trial Balance amounts for one account group.

    Parameters
    ----------
    trial_balance_df:
        Trial Balance DataFrame.

    classifier:
        Function that receives account type and returns True/False.

    Returns
    -------
    float
        Total amount for the account group.
    """

    matching_rows = trial_balance_df[
        trial_balance_df["Account Type"].apply(classifier)
    ].copy()

    if matching_rows.empty:
        return 0.0

    amounts = pd.to_numeric(
        matching_rows["Amount"],
        errors="coerce",
    ).fillna(0.0)

    return round(float(amounts.sum()), 2)


def generate_pnl(trial_balance_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate Profit & Loss report from Trial Balance.

    Parameters
    ----------
    trial_balance_df:
        Trial Balance DataFrame generated from mapped transactions.

    Returns
    -------
    pd.DataFrame
        Profit & Loss report.

    Raises
    ------
    ValueError
        If required Trial Balance columns are missing.
    """

    if trial_balance_df.empty:
        return pd.DataFrame(
            columns=[
                "Particulars",
                "Amount",
            ]
        )

    missing_columns = find_missing_columns(
        trial_balance_df,
        TRIAL_BALANCE_REQUIRED_COLUMNS,
    )

    if missing_columns:
        raise ValueError(
            f"Missing required columns for P&L generation: {missing_columns}"
        )

    working_df = trial_balance_df.copy()

    working_df["Amount"] = pd.to_numeric(
        working_df["Amount"],
        errors="coerce",
    ).fillna(0.0)

    income_total = sum_account_group(
        working_df,
        is_income_account,
    )

    cogs_total = sum_account_group(
        working_df,
        is_cogs_account,
    )

    expense_total = sum_account_group(
        working_df,
        is_expense_account,
    )

    gross_profit = round(income_total + cogs_total, 2)
    net_income = round(gross_profit + expense_total, 2)

    pnl_rows = [
        {
            "Particulars": "Income",
            "Amount": income_total,
        },
        {
            "Particulars": "Cost of Goods Sold",
            "Amount": cogs_total,
        },
        {
            "Particulars": "Gross Profit",
            "Amount": gross_profit,
        },
        {
            "Particulars": "Expenses",
            "Amount": expense_total,
        },
        {
            "Particulars": "Net Income",
            "Amount": net_income,
        },
    ]

    return pd.DataFrame(pnl_rows)