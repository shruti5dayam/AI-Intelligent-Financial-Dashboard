"""
Rules reader for Bank Feed Rules.

Responsibilities:
- Read uploaded rules Excel file
- Detect the correct header row
- Validate required rule columns
"""

from __future__ import annotations

from typing import Any

import pandas as pd


EXPECTED_RULE_COLUMNS = {
    "rule name",
    "rule conditions",
    "rule outputs",
}

RULE_HEADER_CANDIDATES = (0, 1, 2)


def score_rule_header(df: pd.DataFrame) -> int:
    """
    Score how many expected rule columns exist in a DataFrame.

    Parameters
    ----------
    df:
        Candidate DataFrame read from Excel.

    Returns
    -------
    int
        Number of expected rule columns found.
    """

    actual_columns = {
        str(column).strip().lower()
        for column in df.columns
    }

    return len(actual_columns.intersection(EXPECTED_RULE_COLUMNS))


def read_rules_file(uploaded_file: Any) -> pd.DataFrame:
    """
    Read an uploaded Bank Feed Rules Excel file.

    Parameters
    ----------
    uploaded_file:
        Streamlit UploadedFile object for the rules Excel file.

    Returns
    -------
    pd.DataFrame
        Rules DataFrame.

    Raises
    ------
    ValueError
        If the file cannot be read or required columns are missing.
    """

    if uploaded_file is None:
        raise ValueError("No bank feed rules file was uploaded.")

    best_dataframe = None
    best_score = -1

    for header_row in RULE_HEADER_CANDIDATES:
        try:
            uploaded_file.seek(0)

            candidate_dataframe = pd.read_excel(
                uploaded_file,
                header=header_row,
                engine="openpyxl",
            )

            current_score = score_rule_header(candidate_dataframe)

            if current_score > best_score:
                best_score = current_score
                best_dataframe = candidate_dataframe.copy()

        except Exception:
            continue

    if best_dataframe is None:
        raise ValueError("Could not read the bank feed rules file.")

    missing_columns = find_missing_rule_columns(best_dataframe)

    if missing_columns:
        raise ValueError(
            f"Missing required rule columns: {missing_columns}"
        )

    best_dataframe = normalize_rule_columns(best_dataframe)

    return best_dataframe


def find_missing_rule_columns(df: pd.DataFrame) -> list[str]:
    """
    Find missing required rule columns.

    Parameters
    ----------
    df:
        Rules DataFrame.

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
        for column in EXPECTED_RULE_COLUMNS
        if column not in actual_columns
    )

def normalize_rule_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename rule columns to the exact names expected by the parser.

    Parameters
    ----------
    df:
        Raw rules DataFrame.

    Returns
    -------
    pd.DataFrame
        Rules DataFrame with standardized column names.
    """

    column_mapping = {}

    for column in df.columns:
        normalized_column = str(column).strip().lower()

        if normalized_column == "rule name":
            column_mapping[column] = "Rule Name"

        elif normalized_column == "rule conditions":
            column_mapping[column] = "Rule Conditions"

        elif normalized_column == "rule outputs":
            column_mapping[column] = "Rule Outputs"

    return df.rename(columns=column_mapping)