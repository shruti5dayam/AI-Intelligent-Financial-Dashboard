"""
Metadata detection for uploaded bank statements.

Responsibilities:
- Add dashboard-friendly metadata columns
- Detect brands
- Detect store IDs
- Detect bank accounts
- Detect reporting months
- Detect reporting quarters
- Detect statement date range
- Count transactions
"""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

from config import BANK_ACCOUNT_TYPE_KEYWORDS, US_BANK_NAME_KEYWORDS


STORE_ID_PATTERN = re.compile(r"[A-Z]{2}\d{2}", re.IGNORECASE)
ACCOUNT_NUMBER_PATTERN = re.compile(r"\d{3,}")


def extract_store_id_from_text(value: str) -> str:
    """
    Extract a store ID such as DD13, DD14, or BK05 from text.
    """

    match = STORE_ID_PATTERN.search(str(value))

    if not match:
        return ""

    return match.group(0).upper()


def is_bank_account_like(value: str) -> bool:
    """
    Check whether a value looks like a real bank account name.

    A real bank account usually has:
    - a bank name such as Chase, Bank of America, Wells Fargo
    - and either an account type such as Checking/Savings
    - or a partial account number such as 2874
    """

    text = str(value).lower()

    has_bank_name = any(
        bank_name in text
        for bank_name in US_BANK_NAME_KEYWORDS
    )

    has_account_type = any(
        account_type in text
        for account_type in BANK_ACCOUNT_TYPE_KEYWORDS
    )

    has_account_number = bool(ACCOUNT_NUMBER_PATTERN.search(text))

    return has_bank_name and (has_account_type or has_account_number)


def add_metadata_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add Brand, Store ID, Period, and Quarter columns to a bank statement.
    """

    working_df = df.copy()

    if working_df.empty:
        return working_df

    working_df["Brand"] = "Unknown"
    working_df["Store ID"] = ""

    if "Store" in working_df.columns:
        store_text = working_df["Store"].fillna("").astype(str)
        store_parts = store_text.str.split(":", n=1, expand=True)

        working_df["Brand"] = (
            store_parts[0]
            .fillna("")
            .astype(str)
            .str.strip()
            .replace("", "Unknown")
        )

        if store_parts.shape[1] > 1:
            working_df["Store ID"] = (
                store_parts[1]
                .fillna("")
                .astype(str)
                .str.upper()
                .str.strip()
            )

    # File name is often more reliable for store ID.
    # Example: bank_statement_dd14.xlsx -> DD14
    if "Source File" in working_df.columns:
        source_file_store_ids = (
            working_df["Source File"]
            .astype(str)
            .apply(extract_store_id_from_text)
        )

        has_store_id_in_file_name = source_file_store_ids != ""

        working_df.loc[has_store_id_in_file_name, "Store ID"] = (
            source_file_store_ids[has_store_id_in_file_name]
        )

    if "Date" in working_df.columns:
        working_df["Date"] = pd.to_datetime(
            working_df["Date"],
            errors="coerce",
        )

        working_df["Period"] = (
            working_df["Date"]
            .dt.to_period("M")
            .astype(str)
            .replace("NaT", "")
        )

        working_df["Quarter"] = (
            working_df["Date"]
            .dt.to_period("Q")
            .astype(str)
            .replace("NaT", "")
        )
    else:
        working_df["Period"] = ""
        working_df["Quarter"] = ""

    return working_df


def get_unique_non_empty_values(series: pd.Series) -> list[str]:
    """
    Return sorted unique non-empty values from a pandas Series.
    """

    values = (
        series.dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    return sorted(value for value in values if value)


def detect_bank_accounts(working_df: pd.DataFrame) -> list[str]:
    """
    Detect real bank account-like values.

    Important:
    In this project, the Account column may contain GL accounts like
    Food Purchases, Adfund, Insurance Expense, etc.

    Those are not bank accounts, so we only keep values that look like
    actual U.S. bank accounts.
    """

    if "Account" not in working_df.columns:
        return []

    account_values = get_unique_non_empty_values(working_df["Account"])

    return sorted(
        account
        for account in account_values
        if is_bank_account_like(account)
    )


def detect_metadata(bank_df: pd.DataFrame) -> dict[str, Any]:
    """
    Detect metadata from uploaded bank statement data.
    """

    working_df = add_metadata_columns(bank_df)

    if working_df.empty:
        return {
            "transaction_count": 0,
            "brands": [],
            "store_ids": [],
            "bank_accounts": [],
            "months": [],
            "quarters": [],
            "source_files": [],
            "min_date": None,
            "max_date": None,
        }

    source_files = []

    if "Source File" in working_df.columns:
        source_files = get_unique_non_empty_values(working_df["Source File"])

    valid_dates = pd.Series(dtype="datetime64[ns]")

    if "Date" in working_df.columns:
        valid_dates = pd.to_datetime(
            working_df["Date"],
            errors="coerce",
        ).dropna()

    min_date = valid_dates.min().date() if not valid_dates.empty else None
    max_date = valid_dates.max().date() if not valid_dates.empty else None

    return {
        "transaction_count": len(working_df),
        "brands": get_unique_non_empty_values(working_df["Brand"]),
        "store_ids": get_unique_non_empty_values(working_df["Store ID"]),
        "bank_accounts": detect_bank_accounts(working_df),
        "months": get_unique_non_empty_values(working_df["Period"]),
        "quarters": get_unique_non_empty_values(working_df["Quarter"]),
        "source_files": source_files,
        "min_date": min_date,
        "max_date": max_date,
    }