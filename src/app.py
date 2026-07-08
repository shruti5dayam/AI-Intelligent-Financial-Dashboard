"""
AI Intelligent Financial Dashboard.

Day 2 version:
- Upload bank statements
- Detect metadata
- Build report filters automatically
- Read rules and Chart of Accounts
- Run deterministic GL Mapping pipeline
- Generate Trial Balance and Profit & Loss
- Show mapped, unmatched, and missing COA transactions
"""

from __future__ import annotations

import io

import pandas as pd
import streamlit as st

from config import APP_CAPTION, APP_TITLE
from dashboard.metadata_panel import render_metadata_panel
from dashboard.scope_panel import render_scope_panel
from dashboard.upload_panel import render_upload_panel
from ingestion.coa_reader import read_coa_file
from ingestion.file_reader import read_uploaded_bank_files
from ingestion.rules_reader import read_rules_file
from metadata.detector import add_metadata_columns, detect_metadata
from pipeline.financial_pipeline import run_financial_pipeline


PIPELINE_RESULTS_KEY = "financial_pipeline_results"


def make_display_safe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert DataFrame columns into a Streamlit-friendly display format.

    Parameters
    ----------
    df:
        DataFrame to prepare for display.

    Returns
    -------
    pd.DataFrame
        Display-safe DataFrame.
    """

    display_df = df.copy()

    for column in display_df.columns:
        if pd.api.types.is_datetime64_any_dtype(display_df[column]):
            display_df[column] = display_df[column].dt.strftime("%Y-%m-%d")

    return display_df


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


def dataframe_to_excel_bytes(df: pd.DataFrame, sheet_name: str) -> bytes:
    """
    Convert a DataFrame into Excel bytes for download.

    Parameters
    ----------
    df:
        DataFrame to export.

    sheet_name:
        Excel sheet name.

    Returns
    -------
    bytes
        Excel file content.
    """

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)

    buffer.seek(0)
    return buffer.getvalue()


def get_pnl_amount(pnl_df: pd.DataFrame, particular: str) -> float:
    """
    Get one amount from the P&L report.

    Parameters
    ----------
    pnl_df:
        Profit & Loss DataFrame.

    particular:
        Particular name such as Income, Expenses, or Net Income.

    Returns
    -------
    float
        Matching P&L amount.
    """

    if pnl_df.empty:
        return 0.0

    matching_row = pnl_df[
        pnl_df["Particulars"].astype(str).str.lower()
        == particular.lower()
    ]

    if matching_row.empty:
        return 0.0

    value = pd.to_numeric(
        matching_row.iloc[0]["Amount"],
        errors="coerce",
    )

    if pd.isna(value):
        return 0.0

    return float(value)


def render_uploaded_file_status(
    uploaded_rules_file,
    uploaded_coa_file,
) -> None:
    """
    Show upload status for rules and Chart of Accounts files.

    Parameters
    ----------
    uploaded_rules_file:
        Uploaded rules Excel file.

    uploaded_coa_file:
        Uploaded Chart of Accounts CSV file.

    Returns
    -------
    None
        Renders status messages in the sidebar.
    """

    st.sidebar.header("3. File Status")

    if uploaded_rules_file is not None:
        st.sidebar.success("Rules file uploaded")
    else:
        st.sidebar.warning("Rules file required for Day 2 report generation.")

    if uploaded_coa_file is not None:
        st.sidebar.success("Chart of Accounts uploaded")
    else:
        st.sidebar.warning("Chart of Accounts required for Day 2 report generation.")


def render_pipeline_kpis(results: dict) -> None:
    """
    Render financial and validation KPI cards.

    Parameters
    ----------
    results:
        Pipeline result dictionary.

    Returns
    -------
    None
        Renders Streamlit KPI cards.
    """

    validation_summary = results.get("validation_summary", {})
    pnl_df = results.get("pnl_df", pd.DataFrame())

    income = get_pnl_amount(pnl_df, "Income")
    cogs = get_pnl_amount(pnl_df, "Cost of Goods Sold")
    expenses = get_pnl_amount(pnl_df, "Expenses")
    net_income = get_pnl_amount(pnl_df, "Net Income")

    st.subheader("Executive Summary")

    fin_col1, fin_col2, fin_col3, fin_col4 = st.columns(4)

    with fin_col1:
        st.metric("Income", format_money(income))

    with fin_col2:
        st.metric("COGS", format_money(cogs))

    with fin_col3:
        st.metric("Expenses", format_money(expenses))

    with fin_col4:
        st.metric("Net Income", format_money(net_income))

    st.subheader("Mapping Quality")

    map_col1, map_col2, map_col3, map_col4 = st.columns(4)

    with map_col1:
        st.metric(
            "Transactions",
            validation_summary.get("total_transactions", 0),
        )

    with map_col2:
        st.metric(
            "Mapped",
            validation_summary.get("mapped_transactions", 0),
        )

    with map_col3:
        st.metric(
            "Unmatched",
            validation_summary.get("unmatched_transactions", 0),
        )

    with map_col4:
        st.metric(
            "Mapping %",
            f"{validation_summary.get('mapping_percentage', 0.0):.2f}%",
        )

    with st.expander("Debug: Pipeline Internals", expanded=False):
        st.json(validation_summary)


def render_pipeline_results(results: dict) -> None:
    """
    Render pipeline outputs in dashboard tabs.

    Parameters
    ----------
    results:
        Pipeline result dictionary.

    Returns
    -------
    None
        Renders Streamlit UI.
    """

    render_pipeline_kpis(results)

    pnl_df = results.get("pnl_df", pd.DataFrame())
    trial_balance_df = results.get("trial_balance_df", pd.DataFrame())
    mapped_transactions_df = results.get(
        "mapped_transactions_df",
        pd.DataFrame(),
    )
    unmatched_df = results.get("unmatched_df", pd.DataFrame())
    missing_coa_df = results.get("missing_coa_df", pd.DataFrame())

    tab_pnl, tab_tb, tab_transactions, tab_unmatched, tab_missing_coa = st.tabs(
        [
            "Profit & Loss",
            "Trial Balance",
            "Mapped Transactions",
            "Unmatched",
            "Missing COA",
        ]
    )

    with tab_pnl:
        st.subheader("Profit & Loss")

        if pnl_df.empty:
            st.warning("No P&L data available.")
        else:
            st.dataframe(
                make_display_safe(pnl_df).style.format(
                    {"Amount": "{:,.2f}"}
                ),
                width="stretch",
                hide_index=True,
            )

            st.download_button(
                "Download P&L Excel",
                data=dataframe_to_excel_bytes(pnl_df, "Profit and Loss"),
                file_name="profit_and_loss.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
            )

    with tab_tb:
        st.subheader("Trial Balance")

        if trial_balance_df.empty:
            st.warning("No Trial Balance data available.")
        else:
            st.dataframe(
                make_display_safe(trial_balance_df).style.format(
                    {"Amount": "{:,.2f}"}
                ),
                width="stretch",
                hide_index=True,
            )

            st.download_button(
                "Download Trial Balance Excel",
                data=dataframe_to_excel_bytes(
                    trial_balance_df,
                    "Trial Balance",
                ),
                file_name="trial_balance.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
            )

    with tab_transactions:
        st.subheader("Mapped Transactions")

        if mapped_transactions_df.empty:
            st.warning("No mapped transaction data available.")
        else:
            st.dataframe(
                make_display_safe(mapped_transactions_df),
                width="stretch",
                hide_index=True,
            )

    with tab_unmatched:
        st.subheader("Unmatched Transactions")
        st.metric("Unmatched Count", len(unmatched_df))

        if unmatched_df.empty:
            st.success("No unmatched transactions.")
        else:
            st.dataframe(
                make_display_safe(unmatched_df),
                width="stretch",
                hide_index=True,
            )

    with tab_missing_coa:
        st.subheader("Missing COA Mappings")
        st.metric("Missing COA Count", len(missing_coa_df))

        if missing_coa_df.empty:
            st.success("No missing COA mappings.")
        else:
            st.dataframe(
                make_display_safe(missing_coa_df),
                width="stretch",
                hide_index=True,
            )


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🤖",
    layout="wide",
)

st.title(f"🤖 {APP_TITLE}")
st.caption(APP_CAPTION)


uploaded_bank_files, uploaded_rules_file, uploaded_coa_file = render_upload_panel()

render_uploaded_file_status(
    uploaded_rules_file=uploaded_rules_file,
    uploaded_coa_file=uploaded_coa_file,
)


if not uploaded_bank_files:
    st.info(
        "Upload one or more bank statements to detect metadata and build "
        "report filters automatically."
    )
    st.stop()


try:
    bank_df = read_uploaded_bank_files(uploaded_bank_files)
    bank_df = add_metadata_columns(bank_df)
    metadata = detect_metadata(bank_df)

except Exception as error:
    st.error(f"Could not read uploaded bank statements: {error}")
    st.stop()


render_metadata_panel(metadata)

report_scope = render_scope_panel(metadata)


st.subheader("Selected Report Scope")
st.json(report_scope)


with st.expander("Preview Uploaded Bank Data", expanded=False):
    preview_df = make_display_safe(bank_df.head(50))

    st.dataframe(
        preview_df,
        width="stretch",
        hide_index=True,
    )


st.divider()

run_button = st.sidebar.button(
    "📊 Generate Financial Report",
    type="primary",
    width="stretch",
)

clear_button = st.sidebar.button(
    "🧹 Clear Results",
    width="stretch",
)


if clear_button:
    st.session_state.pop(PIPELINE_RESULTS_KEY, None)
    st.rerun()


if run_button:
    if uploaded_rules_file is None:
        st.error("Please upload the Bank Feed Rules file.")
        st.stop()

    if uploaded_coa_file is None:
        st.error("Please upload the Chart of Accounts file.")
        st.stop()

    try:
        with st.spinner("Reading rules and Chart of Accounts..."):
            rules_df = read_rules_file(uploaded_rules_file)
            coa_df = read_coa_file(uploaded_coa_file)

        with st.spinner("Generating financial report..."):
            results = run_financial_pipeline(
                bank_df=bank_df,
                rules_df=rules_df,
                coa_df=coa_df,
                report_scope=report_scope,
            )

        st.session_state[PIPELINE_RESULTS_KEY] = results
        st.success("Financial report generated successfully.")

    except Exception as error:
        st.error(f"Financial report generation failed: {error}")
        st.stop()


results = st.session_state.get(PIPELINE_RESULTS_KEY)

if results:
    render_pipeline_results(results)
else:
    st.subheader("Day 2 Status")
    st.info(
        "Upload bank statements, rules, and Chart of Accounts. "
        "Select the report scope, then click Generate Financial Report."
    )