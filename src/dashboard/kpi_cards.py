"""
KPI card components for the financial dashboard.

Responsibilities:
- Render product-style KPI cards
- Display financial and mapping metrics
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st


def format_money(value: float) -> str:
    """
    Format a numeric value as money.

    Parameters
    ----------
    value:
        Numeric value.

    Returns
    -------
    str
        Money-formatted string.
    """

    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return "$0.00"


def get_pnl_amount(pnl_df: pd.DataFrame, particular: str) -> float:
    """
    Get one amount from the P&L report.

    Parameters
    ----------
    pnl_df:
        Profit & Loss DataFrame.

    particular:
        Particular name such as Income or Net Income.

    Returns
    -------
    float
        Matching amount.
    """

    if pnl_df.empty:
        return 0.0

    matching_row = pnl_df[
        pnl_df["Particulars"].astype(str).str.lower()
        == particular.lower()
    ]

    if matching_row.empty:
        return 0.0

    amount = pd.to_numeric(
        matching_row.iloc[0]["Amount"],
        errors="coerce",
    )

    if pd.isna(amount):
        return 0.0

    return float(amount)


def render_kpi_card(
    label: str,
    value: str,
    note: str,
    gradient_class: str,
) -> None:
    """
    Render one gradient KPI card.

    Parameters
    ----------
    label:
        KPI label.

    value:
        KPI value.

    note:
        Small supporting text.

    gradient_class:
        CSS gradient class name.

    Returns
    -------
    None
        Renders HTML card.
    """

    st.markdown(
        f"""
        <div class="kpi-card {gradient_class}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_financial_kpis(results: dict[str, Any]) -> None:
    """
    Render financial KPI cards.

    Parameters
    ----------
    results:
        Pipeline result dictionary.

    Returns
    -------
    None
        Renders Streamlit KPI cards.
    """

    pnl_df = results.get("pnl_df", pd.DataFrame())

    income = get_pnl_amount(pnl_df, "Income")
    cogs = get_pnl_amount(pnl_df, "Cost of Goods Sold")
    expenses = get_pnl_amount(pnl_df, "Expenses")
    net_income = get_pnl_amount(pnl_df, "Net Income")

    st.markdown('<div class="section-title">Executive Summary</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_kpi_card(
            "Income",
            format_money(income),
            "Total mapped income",
            "gradient-green",
        )

    with col2:
        render_kpi_card(
            "COGS",
            format_money(cogs),
            "Cost of goods sold",
            "gradient-orange",
        )

    with col3:
        render_kpi_card(
            "Expenses",
            format_money(expenses),
            "Operating expenses",
            "gradient-pink",
        )

    with col4:
        render_kpi_card(
            "Net Income",
            format_money(net_income),
            "Income after costs",
            "gradient-purple",
        )


def render_mapping_kpis(results: dict[str, Any]) -> None:
    """
    Render mapping quality KPI cards.

    Parameters
    ----------
    results:
        Pipeline result dictionary.

    Returns
    -------
    None
        Renders mapping KPI cards.
    """

    validation_summary = results.get("validation_summary", {})

    total_transactions = validation_summary.get("total_transactions", 0)
    mapped_transactions = validation_summary.get("mapped_transactions", 0)
    unmatched_transactions = validation_summary.get("unmatched_transactions", 0)
    mapping_percentage = validation_summary.get("mapping_percentage", 0.0)

    st.markdown('<div class="section-title">Mapping Quality</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_kpi_card(
            "Transactions",
            f"{total_transactions:,}",
            "Rows processed",
            "gradient-blue",
        )

    with col2:
        render_kpi_card(
            "Mapped",
            f"{mapped_transactions:,}",
            "Rule matched",
            "gradient-green",
        )

    with col3:
        render_kpi_card(
            "Unmatched",
            f"{unmatched_transactions:,}",
            "Needs review",
            "gradient-pink",
        )

    with col4:
        render_kpi_card(
            "Mapping %",
            f"{mapping_percentage:.2f}%",
            "Automation rate",
            "gradient-purple",
        )