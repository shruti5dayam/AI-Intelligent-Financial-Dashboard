"""
Chart of Accounts reader.

Responsibilities:
- Read uploaded Chart of Accounts CSV file
- Validate required COA columns
- Return a clean pandas DataFrame
"""

from __future__ import annotations

from typing import Any

import pandas as pd


EXPECTED_COA_COLUMNS = {
    "account number",
    "account name",
    "account type",
    "detail type",
}


def read_coa_file(uploaded_file: Any) -> pd.DataFrame:
    """
    Read an uploaded Chart of Accounts CSV file.

    Parameters
    ----------
    uploaded_file:
        Streamlit UploadedFile object for the COA CSV file.

    Returns
    -------
    pd.DataFrame
        Chart of Accounts DataFrame.

    Raises
    ------
    ValueError
        If the file is missing, unreadable, or required columns are missing.
    """

    if uploaded_file is None:
        raise ValueError("No Chart of Accounts file was uploaded.")

    uploaded_file.seek(0)

    try:
        coa_df = pd.read_csv(uploaded_file)
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        coa_df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
    except Exception as error:
        raise ValueError(f"Could not read Chart of Accounts file: {error}") from error

    missing_columns = find_missing_coa_columns(coa_df)

    if missing_columns:
        raise ValueError(
            f"Missing required Chart of Accounts columns: {missing_columns}"
        )

    return clean_coa_dataframe(coa_df)


def find_missing_coa_columns(df: pd.DataFrame) -> list[str]:
    """
    Find missing required Chart of Accounts columns.

    Parameters
    ----------
    df:
        Chart of Accounts DataFrame.

    Returns
    -------
    list[str]
        Missing column names.
    """

    actual_columns = {
        str(column).strip().lower()
        for column in df.columns
    }

    return sorted(
        column
        for column in EXPECTED_COA_COLUMNS
        if column not in actual_columns
    )


def clean_coa_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean Chart of Accounts text fields.

    Parameters
    ----------
    df:
        Raw Chart of Accounts DataFrame.

    Returns
    -------
    pd.DataFrame
        Cleaned Chart of Accounts DataFrame.
    """

    cleaned_df = df.copy()

    text_columns = [
        "Account number",
        "Account name",
        "Account type",
        "Detail type",
    ]

    for column in text_columns:
        if column in cleaned_df.columns:
            cleaned_df[column] = (
                cleaned_df[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    return cleaned_df