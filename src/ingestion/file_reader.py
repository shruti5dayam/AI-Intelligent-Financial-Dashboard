"""
File reading utilities for uploaded bank statements.

Responsibilities:
- Read uploaded Excel files
- Detect the correct header row automatically
- Combine multiple bank statements into one DataFrame
- Preserve the original source file name
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from config import EXPECTED_BANK_COLUMNS, HEADER_CANDIDATES


def score_header(df: pd.DataFrame, expected_columns: set[str]) -> int:
    """
    Score how many expected bank statement columns exist in a DataFrame.

    Parameters
    ----------
    df:
        Candidate DataFrame read from Excel.

    expected_columns:
        Expected lowercase column names.

    Returns
    -------
    int
        Number of expected columns found in the DataFrame.
    """

    actual_columns = {
        str(column).strip().lower()
        for column in df.columns
    }

    return len(actual_columns.intersection(expected_columns))


def read_excel_with_best_header(uploaded_file: Any) -> pd.DataFrame:
    """
    Read an uploaded Excel file using the best detected header row.

    Some bank statements may have the real header on row 0.
    Others may have a title row first, so the header may be on row 1 or row 2.

    This function tries multiple possible header rows and chooses the one
    that matches the expected bank columns best.

    Parameters
    ----------
    uploaded_file:
        Streamlit UploadedFile object.

    Returns
    -------
    pd.DataFrame
        DataFrame read using the most likely header row.

    Raises
    ------
    ValueError
        If the file cannot be read.
    """

    best_dataframe = None
    best_score = -1

    for header_row in HEADER_CANDIDATES:
        try:
            uploaded_file.seek(0)

            candidate_dataframe = pd.read_excel(
                uploaded_file,
                header=header_row,
                engine="openpyxl",
            )

            current_score = score_header(
                candidate_dataframe,
                EXPECTED_BANK_COLUMNS,
            )

            if current_score > best_score:
                best_score = current_score
                best_dataframe = candidate_dataframe.copy()

        except Exception:
            continue

    if best_dataframe is None:
        raise ValueError(f"Could not read Excel file: {uploaded_file.name}")

    return best_dataframe


def read_uploaded_bank_files(uploaded_files: list[Any]) -> pd.DataFrame:
    """
    Read and combine multiple uploaded bank statement files.

    Parameters
    ----------
    uploaded_files:
        List of Streamlit UploadedFile objects.

    Returns
    -------
    pd.DataFrame
        Combined bank statement DataFrame.

    Raises
    ------
    ValueError
        If no files are provided.
    """

    if not uploaded_files:
        raise ValueError("No bank statement files were uploaded.")

    bank_dataframes = []

    for uploaded_file in uploaded_files:
        bank_dataframe = read_excel_with_best_header(uploaded_file)

        # Keep track of which original file each row came from.
        # This helps with audit trail and debugging.
        bank_dataframe["Source File"] = uploaded_file.name

        bank_dataframes.append(bank_dataframe)

    return pd.concat(bank_dataframes, ignore_index=True)