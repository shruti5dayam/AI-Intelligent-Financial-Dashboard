"""
Chart of Accounts lookup utilities.

Responsibilities:
- Build a lookup dictionary from the Chart of Accounts
- Match mapped GL Account names to COA rows
- Enrich transactions with Account Number, Account Name, Account Type, and Detail Type
"""

from __future__ import annotations

from typing import Any

import pandas as pd


COA_ACCOUNT_NUMBER_COLUMN = "Account number"
COA_ACCOUNT_NAME_COLUMN = "Account name"
COA_ACCOUNT_TYPE_COLUMN = "Account type"
COA_DETAIL_TYPE_COLUMN = "Detail type"


def normalize_account_name(value: Any) -> str:
    """
    Normalize an account name for reliable matching.

    Parameters
    ----------
    value:
        Account name value.

    Returns
    -------
    str
        Lowercase stripped account name.
    """

    if value is None:
        return ""

    return str(value).strip().lower()


def build_coa_lookup(coa_df: pd.DataFrame) -> dict[str, dict[str, str]]:
    """
    Build a lookup dictionary from the Chart of Accounts.

    Parameters
    ----------
    coa_df:
        Chart of Accounts DataFrame.

    Returns
    -------
    dict[str, dict[str, str]]
        Dictionary where key is normalized account name and value contains COA details.
    """

    lookup = {}

    if coa_df.empty:
        return lookup

    for _, row in coa_df.iterrows():
        account_name = normalize_account_name(
            row.get(COA_ACCOUNT_NAME_COLUMN, "")
        )

        if not account_name:
            continue

        lookup[account_name] = {
            "Account Number": str(row.get(COA_ACCOUNT_NUMBER_COLUMN, "")).strip(),
            "Account Name": str(row.get(COA_ACCOUNT_NAME_COLUMN, "")).strip(),
            "Account Type": str(row.get(COA_ACCOUNT_TYPE_COLUMN, "")).strip(),
            "Detail Type": str(row.get(COA_DETAIL_TYPE_COLUMN, "")).strip(),
        }

    return lookup


def enrich_transactions_with_coa(
    mapped_df: pd.DataFrame,
    coa_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add Chart of Accounts details to mapped transactions.

    Parameters
    ----------
    mapped_df:
        Transactions after rule engine mapping.

    coa_df:
        Chart of Accounts DataFrame.

    Returns
    -------
    pd.DataFrame
        Transactions enriched with COA information.
    """

    enriched_df = mapped_df.copy()

    if enriched_df.empty:
        return enriched_df

    coa_lookup = build_coa_lookup(coa_df)

    enriched_df["Account Number"] = ""
    enriched_df["Account Name"] = ""
    enriched_df["Account Type"] = ""
    enriched_df["Detail Type"] = ""
    enriched_df["COA Mapping Status"] = "Missing COA Mapping"

    for index, transaction in enriched_df.iterrows():
        gl_account = normalize_account_name(
            transaction.get("GL Account", "")
        )

        if not gl_account:
            continue

        coa_details = coa_lookup.get(gl_account)

        if coa_details is None:
            continue

        enriched_df.at[index, "Account Number"] = coa_details["Account Number"]
        enriched_df.at[index, "Account Name"] = coa_details["Account Name"]
        enriched_df.at[index, "Account Type"] = coa_details["Account Type"]
        enriched_df.at[index, "Detail Type"] = coa_details["Detail Type"]
        enriched_df.at[index, "COA Mapping Status"] = "Mapped"

    return enriched_df