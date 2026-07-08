"""
Dashboard chart components.

Responsibilities:
- Render P&L breakdown chart
- Render mapping quality chart
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st


def render_pnl_chart(results: dict[str, Any]) -> None:
    """
    Render a P&L breakdown chart.

    Parameters
    ----------
    results:
        Pipeline result dictionary.

    Returns
    -------
    None
        Renders Streamlit chart.
    """

    pnl_df = results.get("pnl_df", pd.DataFrame())

    if pnl_df.empty:
        st.warning("No P&L chart data available.")
        return

    chart_df = pnl_df[
        pnl_df["Particulars"].isin(
            [
                "Income",
                "Cost of Goods Sold",
                "Expenses",
                "Net Income",
            ]
        )
    ].copy()

    chart_df["Amount"] = pd.to_numeric(
        chart_df["Amount"],
        errors="coerce",
    ).fillna(0.0)

    st.bar_chart(
        chart_df,
        x="Particulars",
        y="Amount",
    )


def render_mapping_quality_chart(results: dict[str, Any]) -> None:
    """
    Render mapping quality chart.

    Parameters
    ----------
    results:
        Pipeline result dictionary.

    Returns
    -------
    None
        Renders Streamlit chart.
    """

    validation_summary = results.get("validation_summary", {})

    chart_df = pd.DataFrame(
        [
            {
                "Status": "Mapped",
                "Count": validation_summary.get("mapped_transactions", 0),
            },
            {
                "Status": "Unmatched",
                "Count": validation_summary.get("unmatched_transactions", 0),
            },
            {
                "Status": "Missing COA",
                "Count": validation_summary.get("missing_coa_mappings", 0),
            },
        ]
    )

    st.bar_chart(
        chart_df,
        x="Status",
        y="Count",
    )


def render_dashboard_charts(results: dict[str, Any]) -> None:
    """
    Render dashboard chart section.

    Parameters
    ----------
    results:
        Pipeline result dictionary.

    Returns
    -------
    None
        Renders chart layout.
    """

    st.markdown('<div class="section-title">Financial Analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("P&L Breakdown")
        render_pnl_chart(results)

    with col2:
        st.subheader("Mapping Quality")
        render_mapping_quality_chart(results)