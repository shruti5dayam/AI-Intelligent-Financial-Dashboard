"""
Metadata summary panel for the AI Intelligent Financial Dashboard.

Responsibilities:
- Display detected transaction count
- Display detected brands
- Display detected stores
- Display detected bank accounts
- Display detected date range
- Display detailed detected values in an expandable section
"""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_metadata_panel(metadata: dict[str, Any]) -> None:
    """
    Render detected metadata summary on the main dashboard page.

    Parameters
    ----------
    metadata:
        Dictionary returned by metadata.detector.detect_metadata().

    Returns
    -------
    None
        This function renders Streamlit UI elements directly.
    """

    st.subheader("Detected Metadata")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Transactions",
            metadata.get("transaction_count", 0),
        )

    with col2:
        st.metric(
            "Brands",
            len(metadata.get("brands", [])),
        )

    with col3:
        st.metric(
            "Stores",
            len(metadata.get("store_ids", [])),
        )

    with col4:
        st.metric(
            "Bank Accounts",
            len(metadata.get("bank_accounts", [])),
        )

    st.markdown("### Statement Date Range")

    min_date = metadata.get("min_date")
    max_date = metadata.get("max_date")

    if min_date and max_date:
        st.info(f"{min_date} → {max_date}")
    else:
        st.warning("No valid transaction dates were detected.")

    with st.expander("View detected values", expanded=False):
        st.write("**Source Files:**", metadata.get("source_files", []))
        st.write("**Brands:**", metadata.get("brands", []))
        st.write("**Store IDs:**", metadata.get("store_ids", []))
        st.write("**Bank Accounts:**", metadata.get("bank_accounts", []))
        st.write("**Months:**", metadata.get("months", []))
        st.write("**Quarters:**", metadata.get("quarters", []))