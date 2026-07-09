"""
KPI card components for the financial dashboard.

Responsibilities:
- Render product-style KPI cards
- Display financial and mapping metrics
"""

from __future__ import annotations

from typing import Any
from html import escape

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
    tooltip: str | None = None,
) -> None:
    """
    Render one gradient KPI card with optional hover tooltip.

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

    tooltip:
        Optional hover text shown when the user hovers over the card.

    Returns
    -------
    None
        Renders HTML card.
    """

    tooltip_html = ""

    if tooltip:
        safe_tooltip = escape(tooltip).replace("\n", "<br>")
        tooltip_html = f'<div class="kpi-tooltip">{safe_tooltip}</div>'

    st.markdown(
        f"""
        <div class="kpi-card-wrapper">
            <div class="kpi-card {gradient_class}">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-note">{note}</div>
            </div>
            {tooltip_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

def get_metadata_count(
    metadata: dict[str, Any],
    possible_keys: list[str],
) -> int:
    """
    Safely get a count value from metadata.

    Parameters
    ----------
    metadata:
        Metadata dictionary detected from uploaded bank files.

    possible_keys:
        Possible key names where the value may exist.

    Returns
    -------
    int
        Count value.
    """

    for key in possible_keys:
        if key not in metadata:
            continue

        value = metadata.get(key)

        if value is None:
            return 0

        if isinstance(value, int):
            return value

        if isinstance(value, float):
            return int(value)

        if isinstance(value, (list, tuple, set)):
            return len(value)

        if isinstance(value, dict):
            return len(value)

        if isinstance(value, str):
            if not value.strip():
                return 0
            return 1

    return 0


def get_date_range_text(metadata: dict[str, Any]) -> str:
    """
    Build a readable statement date range from metadata.

    Parameters
    ----------
    metadata:
        Metadata dictionary detected from uploaded bank files.

    Returns
    -------
    str
        Date range text.
    """

    date_range = metadata.get("date_range")

    if isinstance(date_range, str) and date_range.strip():
        return date_range

    if isinstance(date_range, dict):
        start_date = (
            date_range.get("start_date")
            or date_range.get("min_date")
            or date_range.get("from")
        )
        end_date = (
            date_range.get("end_date")
            or date_range.get("max_date")
            or date_range.get("to")
        )

        if start_date and end_date:
            return f"{start_date} → {end_date}"

    start_date = (
        metadata.get("start_date")
        or metadata.get("min_date")
        or metadata.get("statement_start_date")
    )
    end_date = (
        metadata.get("end_date")
        or metadata.get("max_date")
        or metadata.get("statement_end_date")
    )

    if start_date and end_date:
        return f"{start_date} → {end_date}"

    return "Not detected"

def render_metadata_kpis(
    metadata: dict[str, Any],
    bank_df: pd.DataFrame | None = None,
) -> None:
    """
    Render detected metadata as product-style KPI cards.

    Parameters
    ----------
    metadata:
        Metadata dictionary detected from uploaded bank files.

    bank_df:
        Uploaded bank statement DataFrame. Used for hover details.

    Returns
    -------
    None
        Renders metadata KPI cards.
    """

    transactions = get_metadata_count(
        metadata,
        [
            "total_transactions",
            "transaction_count",
            "transactions",
            "rows",
            "row_count",
        ],
    )

    brands = get_metadata_count(
        metadata,
        [
            "brands",
            "brand",
            "detected_brands",
        ],
    )

    stores = get_metadata_count(
        metadata,
        [
            "stores",
            "store_ids",
            "detected_stores",
        ],
    )

    bank_accounts = get_metadata_count(
        metadata,
        [
            "bank_accounts",
            "accounts",
            "detected_bank_accounts",
        ],
    )

    date_range_text = get_date_range_text(metadata)

    brand_values = get_metadata_values(
        metadata,
        [
            "brands",
            "brand",
            "detected_brands",
        ],
    )

    if not brand_values:
        brand_values = get_unique_column_values(
            bank_df,
            [
                "Brand",
                "brand",
            ],
        )

    store_values = get_metadata_values(
        metadata,
        [
            "stores",
            "store_ids",
            "detected_stores",
        ],
    )

    if not store_values:
        store_values = get_unique_column_values(
            bank_df,
            [
                "Store ID",
                "Store",
                "store_id",
                "store",
            ],
        )

    bank_account_values = get_metadata_values(
        metadata,
        [
            "bank_accounts",
            "accounts",
            "detected_bank_accounts",
        ],
    )

    if not bank_account_values:
        bank_account_values = get_unique_column_values(
            bank_df,
            [
                "Bank Account",
                "Account",
                "bank_account",
                "account",
            ],
        )

    store_breakdown = get_store_transaction_breakdown(bank_df)

    transactions_tooltip = build_tooltip(
        "Transactions by Store",
        store_breakdown,
    )

    brands_tooltip = build_tooltip(
        "Detected Brands",
        brand_values,
    )

    stores_tooltip = build_tooltip(
        "Detected Stores",
        store_values,
    )

    bank_accounts_tooltip = build_tooltip(
        "Detected Bank Accounts",
        bank_account_values,
    )

    st.markdown(
        '<div class="section-title">Detected Data Summary</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_kpi_card(
            "Transactions",
            f"{transactions:,}",
            "Rows read from bank files",
            "gradient-blue",
            tooltip=transactions_tooltip,
        )

    with col2:
        render_kpi_card(
            "Brands",
            f"{brands:,}",
            "Detected from statements",
            "gradient-purple",
            tooltip=brands_tooltip,
        )

    with col3:
        render_kpi_card(
            "Stores",
            f"{stores:,}",
            "Detected store IDs",
            "gradient-green",
            tooltip=stores_tooltip,
        )

    with col4:
        render_kpi_card(
            "Bank Accounts",
            f"{bank_accounts:,}",
            "Detected bank accounts",
            "gradient-orange",
            tooltip=bank_accounts_tooltip,
        )

    st.markdown(
        f"""
        <div class="status-panel">
            <div class="status-title">Statement Date Range</div>
            <div class="status-subtitle">{date_range_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def get_metadata_values(
    metadata: dict[str, Any],
    possible_keys: list[str],
) -> list[str]:
    """
    Extract readable values from metadata.

    Parameters
    ----------
    metadata:
        Detected metadata dictionary.

    possible_keys:
        Possible metadata keys to search.

    Returns
    -------
    list[str]
        Unique readable values.
    """

    for key in possible_keys:
        if key not in metadata:
            continue

        value = metadata.get(key)

        if value is None:
            return []

        if isinstance(value, dict):
            return sorted(str(item) for item in value.keys())

        if isinstance(value, (list, tuple, set)):
            return sorted(str(item) for item in value)

        if isinstance(value, str):
            cleaned_value = value.strip()

            if not cleaned_value:
                return []

            if "," in cleaned_value:
                return sorted(
                    item.strip()
                    for item in cleaned_value.split(",")
                    if item.strip()
                )

            return [cleaned_value]

        return [str(value)]

    return []


def get_unique_column_values(
    df: pd.DataFrame | None,
    possible_columns: list[str],
) -> list[str]:
    """
    Extract unique values from the first matching DataFrame column.

    Parameters
    ----------
    df:
        Source DataFrame.

    possible_columns:
        Possible column names to search.

    Returns
    -------
    list[str]
        Unique non-empty values.
    """

    if df is None or df.empty:
        return []

    for column in possible_columns:
        if column not in df.columns:
            continue

        values = (
            df[column]
            .dropna()
            .astype(str)
            .str.strip()
        )

        values = values[
            (values != "")
            & (values.str.lower() != "nan")
            & (values.str.lower() != "none")
        ]

        return sorted(values.unique().tolist())

    return []


def get_store_transaction_breakdown(
    bank_df: pd.DataFrame | None,
) -> list[str]:
    """
    Count transactions by store.

    Parameters
    ----------
    bank_df:
        Uploaded bank statement DataFrame.

    Returns
    -------
    list[str]
        Store-wise transaction count text.
    """

    if bank_df is None or bank_df.empty:
        return []

    possible_store_columns = [
        "Store ID",
        "Store",
        "store_id",
        "store",
    ]

    for column in possible_store_columns:
        if column not in bank_df.columns:
            continue

        store_series = (
            bank_df[column]
            .dropna()
            .astype(str)
            .str.strip()
        )

        store_series = store_series[
            (store_series != "")
            & (store_series.str.lower() != "nan")
            & (store_series.str.lower() != "none")
        ]

        store_counts = store_series.value_counts()

        return [
            f"{store}: {count:,} transactions"
            for store, count in store_counts.items()
        ]

    return []


def build_tooltip(title: str, values: list[str]) -> str:
    """
    Build tooltip text from a title and list of values.

    Parameters
    ----------
    title:
        Tooltip title.

    values:
        Values to show inside the tooltip.

    Returns
    -------
    str
        Tooltip text.
    """

    if not values:
        return f"{title}\n- No values detected"

    value_lines = "\n".join(f"- {value}" for value in values)

    return f"{title}\n{value_lines}"

def render_status_chip(label: str, is_ready: bool) -> str:
    """
    Build one status chip as HTML.

    Parameters
    ----------
    label:
        Status label.

    is_ready:
        Whether the status is ready.

    Returns
    -------
    str
        HTML status chip.
    """

    if is_ready:
        return f'<span class="status-chip">✓ {label}</span>'

    return f'<span class="status-chip status-chip-warning">○ {label}</span>'


def render_financial_status_panel(
    uploaded_bank_files: list[Any] | None,
    uploaded_rules_file: Any,
    uploaded_coa_file: Any,
    results: dict[str, Any] | None,
) -> None:
    """
    Render financial report status panel.

    Parameters
    ----------
    uploaded_bank_files:
        Uploaded bank statement files.

    uploaded_rules_file:
        Uploaded bank feed rules file.

    uploaded_coa_file:
        Uploaded Chart of Accounts file.

    results:
        Financial pipeline result dictionary.

    Returns
    -------
    None
        Renders financial status panel.
    """

    bank_files_ready = bool(uploaded_bank_files)
    rules_ready = uploaded_rules_file is not None
    coa_ready = uploaded_coa_file is not None
    pipeline_ready = results is not None

    chips_html = " ".join(
        [
            render_status_chip("Bank Statements Loaded", bank_files_ready),
            render_status_chip("Rules Loaded", rules_ready),
            render_status_chip("COA Loaded", coa_ready),
            render_status_chip("Financial Pipeline Ready", pipeline_ready),
        ]
    )

    st.markdown(
        f"""
        <div class="status-panel">
            <div class="status-title">Financial Report Status</div>
            <div class="status-subtitle">
                Upload files, select scope, and generate the report.
            </div>
            {chips_html}
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