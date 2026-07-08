"""
Report scope selection panel for the AI Intelligent Financial Dashboard.

Responsibilities:
- Build filter dropdowns from detected metadata
- Allow user to choose bank account, brand, store, and period
- Return selected report scope to the main app
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from config import ALL_OPTION, PERIOD_TYPES


def build_filter_options(values: list[str]) -> list[str]:
    """
    Add the default 'All' option to a list of filter values.

    Parameters
    ----------
    values:
        List of detected metadata values.

    Returns
    -------
    list[str]
        Filter options starting with 'All'.
    """

    return [ALL_OPTION] + values


def render_scope_panel(metadata: dict[str, Any]) -> dict[str, str]:
    """
    Render report scope filters in the sidebar.

    Parameters
    ----------
    metadata:
        Dictionary returned by metadata.detector.detect_metadata().

    Returns
    -------
    dict[str, str]
        Dictionary containing the selected report scope.
    """

    st.sidebar.header("2. Report Scope")

    selected_bank_account = st.sidebar.selectbox(
        "Bank Account",
        build_filter_options(metadata.get("bank_accounts", [])),
    )

    selected_brand = st.sidebar.selectbox(
        "Brand",
        build_filter_options(metadata.get("brands", [])),
    )

    selected_store_id = st.sidebar.selectbox(
        "Store ID",
        build_filter_options(metadata.get("store_ids", [])),
    )

    report_period_type = st.sidebar.selectbox(
        "Report Period Type",
        PERIOD_TYPES,
    )

    selected_month = ALL_OPTION
    selected_quarter = ALL_OPTION

    if report_period_type == "Month":
        selected_month = st.sidebar.selectbox(
            "Month",
            build_filter_options(metadata.get("months", [])),
        )

    elif report_period_type == "Quarter":
        selected_quarter = st.sidebar.selectbox(
            "Quarter",
            build_filter_options(metadata.get("quarters", [])),
        )

    return {
        "bank_account": selected_bank_account,
        "brand": selected_brand,
        "store_id": selected_store_id,
        "period_type": report_period_type,
        "month": selected_month,
        "quarter": selected_quarter,
    }