"""
Trial Balance generator.

Responsibilities:
- Validate required accounting columns
- Filter transactions that have valid COA mapping
- Group transactions by account
- Sum amounts by account
- Return Trial Balance DataFrame
"""

from __future__ import annotations

import pandas as pd


TRIAL_BALANCE_GROUP_COLUMNS = [
    "Account Number",
    "Account Name",
    "Account Type",
    "Detail Type",
]

REQUIRED_TRIAL_BALANCE_COLUMNS = TRIAL_BALANCE_GROUP_COLUMNS + ["Amount"]


def find_missing_columns(
    df: pd.DataFrame,
    required_columns: list[str],
) -> list[str]:
    """
    Find required columns that are missing from a DataFrame.

    Parameters
    ----------
    df:
        Input DataFrame.

    required_columns:
        Columns that must exist.

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


def filter_trial_balance_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only transactions that are ready for Trial Balance reporting.

    Parameters
    ----------
    df:
        COA-enriched transaction DataFrame.

    Returns
    -------
    pd.DataFrame
        Filtered transaction DataFrame.
    """

    working_df = df.copy()

    if working_df.empty:
        return working_df

    if "COA Mapping Status" in working_df.columns:
        working_df = working_df[
            working_df["COA Mapping Status"] == "Mapped"
        ].copy()

    working_df = working_df[
        working_df["Account Name"].fillna("").astype(str).str.strip() != ""
    ].copy()

    return working_df


def generate_trial_balance(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate Trial Balance from mapped and COA-enriched transactions.

    Parameters
    ----------
    transactions_df:
        Final transaction DataFrame after rule mapping and COA enrichment.

    Returns
    -------
    pd.DataFrame
        Trial Balance grouped by account.

    Raises
    ------
    ValueError
        If required accounting columns are missing.
    """

    if transactions_df.empty:
        return pd.DataFrame(columns=REQUIRED_TRIAL_BALANCE_COLUMNS)

    missing_columns = find_missing_columns(
        transactions_df,
        REQUIRED_TRIAL_BALANCE_COLUMNS,
    )

    if missing_columns:
        raise ValueError(
            f"Missing required columns for Trial Balance: {missing_columns}"
        )

    working_df = filter_trial_balance_transactions(transactions_df)

    if working_df.empty:
        return pd.DataFrame(columns=REQUIRED_TRIAL_BALANCE_COLUMNS)

    working_df["Amount"] = pd.to_numeric(
        working_df["Amount"],
        errors="coerce",
    ).fillna(0.0)

    trial_balance_df = (
        working_df.groupby(
            TRIAL_BALANCE_GROUP_COLUMNS,
            as_index=False,
        )["Amount"]
        .sum()
        .sort_values(
            ["Account Type", "Account Number", "Account Name"],
            na_position="last",
        )
        .reset_index(drop=True)
    )

    trial_balance_df["Amount"] = trial_balance_df["Amount"].round(2)

    return trial_balance_df