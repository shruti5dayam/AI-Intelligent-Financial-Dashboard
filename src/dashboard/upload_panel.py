"""
Upload panel UI for the AI Intelligent Financial Dashboard.

Responsibilities:
- Display file upload widgets in the Streamlit sidebar
- Allow users to upload bank statements, rules, and chart of accounts
- Return uploaded files to the main app
"""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_upload_panel() -> tuple[list[Any], Any, Any]:
    """
    Render upload widgets in the sidebar.

    Returns
    -------
    tuple[list[Any], Any, Any]
        uploaded_bank_files:
            List of uploaded bank statement Excel files.

        uploaded_rules_file:
            Uploaded bank feed rules Excel file.

        uploaded_coa_file:
            Uploaded chart of accounts CSV file.
    """

    st.sidebar.header("1. Upload Files")

    uploaded_bank_files = st.sidebar.file_uploader(
        "Bank Statements (.xlsx)",
        type=["xlsx"],
        accept_multiple_files=True,
        help="Upload one or more bank statement Excel files.",
    )

    uploaded_rules_file = st.sidebar.file_uploader(
        "Bank Feed Rules (.xlsx)",
        type=["xlsx"],
        help="Upload the rule file used for GL mapping. This will be used in Day 2.",
    )

    uploaded_coa_file = st.sidebar.file_uploader(
        "Chart of Accounts (.csv)",
        type=["csv"],
        help="Upload the chart of accounts file. This will be used in Day 2.",
    )

    return uploaded_bank_files, uploaded_rules_file, uploaded_coa_file 