"""
Financial processing pipeline.

Responsibilities:
- Apply selected report scope filters
- Parse bank feed rules
- Apply GL mapping rules to transactions
- Enrich mapped transactions with Chart of Accounts details
- Validate mapped transactions
- Generate Trial Balance
- Generate Profit & Loss
- Return all outputs needed by the dashboard
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from accounting.coa_lookup import enrich_transactions_with_coa
from accounting.pnl_generator import generate_pnl
from accounting.rule_engine import apply_rules
from accounting.rule_parser import parse_rules
from accounting.trial_balance import generate_trial_balance
from accounting.validators import (
    get_missing_coa_transactions,
    get_unmatched_transactions,
    validate_transactions,
)
from config import ALL_OPTION
from metadata.detector import add_metadata_columns


def filter_by_report_scope(
    bank_df: pd.DataFrame,
    report_scope: dict[str, str],
) -> pd.DataFrame:
    """
    Filter bank transactions based on the selected report scope.

    Parameters
    ----------
    bank_df:
        Bank statement DataFrame with metadata columns.

    report_scope:
        Dictionary containing selected filters such as brand, store, month,
        and quarter.

    Returns
    -------
    pd.DataFrame
        Filtered bank statement DataFrame.
    """

    filtered_df = bank_df.copy()

    if filtered_df.empty:
        return filtered_df

    selected_brand = report_scope.get("brand", ALL_OPTION)
    selected_store_id = report_scope.get("store_id", ALL_OPTION)
    selected_bank_account = report_scope.get("bank_account", ALL_OPTION)
    period_type = report_scope.get("period_type", ALL_OPTION)
    selected_month = report_scope.get("month", ALL_OPTION)
    selected_quarter = report_scope.get("quarter", ALL_OPTION)

    if selected_brand != ALL_OPTION and "Brand" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["Brand"] == selected_brand
        ].copy()

    if selected_store_id != ALL_OPTION and "Store ID" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["Store ID"] == selected_store_id
        ].copy()

    # Important:
    # We only filter by bank account if a true Bank Account column exists.
    # In your current bank statement, the Account column mostly contains
    # GL/category names such as Food Purchases, Adfund, etc.
    # So we do not use Account as a bank-account filter here.
    if (
        selected_bank_account != ALL_OPTION
        and "Bank Account" in filtered_df.columns
    ):
        filtered_df = filtered_df[
            filtered_df["Bank Account"] == selected_bank_account
        ].copy()

    if (
        period_type == "Month"
        and selected_month != ALL_OPTION
        and "Period" in filtered_df.columns
    ):
        filtered_df = filtered_df[
            filtered_df["Period"] == selected_month
        ].copy()

    if (
        period_type == "Quarter"
        and selected_quarter != ALL_OPTION
        and "Quarter" in filtered_df.columns
    ):
        filtered_df = filtered_df[
            filtered_df["Quarter"] == selected_quarter
        ].copy()

    return filtered_df.reset_index(drop=True)


def build_pipeline_result(
    filtered_bank_df: pd.DataFrame,
    enriched_transactions_df: pd.DataFrame,
    trial_balance_df: pd.DataFrame,
    pnl_df: pd.DataFrame,
    validation_summary: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a standard result dictionary for the dashboard.

    Parameters
    ----------
    filtered_bank_df:
        Bank transactions after report scope filtering.

    enriched_transactions_df:
        Final transactions after rule mapping and COA enrichment.

    trial_balance_df:
        Generated Trial Balance DataFrame.

    pnl_df:
        Generated Profit & Loss DataFrame.

    validation_summary:
        Dictionary containing pipeline validation metrics.

    Returns
    -------
    dict[str, Any]
        Standard pipeline result object.
    """

    unmatched_df = get_unmatched_transactions(enriched_transactions_df)
    missing_coa_df = get_missing_coa_transactions(enriched_transactions_df)

    return {
        "filtered_bank_df": filtered_bank_df,
        "mapped_transactions_df": enriched_transactions_df,
        "trial_balance_df": trial_balance_df,
        "pnl_df": pnl_df,
        "unmatched_df": unmatched_df,
        "missing_coa_df": missing_coa_df,
        "validation_summary": validation_summary,
    }


def run_financial_pipeline(
    bank_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    coa_df: pd.DataFrame,
    report_scope: dict[str, str],
) -> dict[str, Any]:
    """
    Run the full financial reporting pipeline.

    Parameters
    ----------
    bank_df:
        Uploaded bank statement DataFrame.

    rules_df:
        Bank Feed Rules DataFrame.

    coa_df:
        Chart of Accounts DataFrame.

    report_scope:
        Selected reporting filters from the dashboard.

    Returns
    -------
    dict[str, Any]
        Pipeline outputs used by the dashboard.
    """

    bank_with_metadata_df = add_metadata_columns(bank_df)

    filtered_bank_df = filter_by_report_scope(
        bank_with_metadata_df,
        report_scope,
    )

    parsed_rules = parse_rules(rules_df)

    parsed_rules_count = len(parsed_rules)
    rules_with_keywords_count = sum(
        1
        for rule in parsed_rules
        if rule.get("keywords")
    )

    rules_columns = list(rules_df.columns)
    raw_rules_rows = len(rules_df)

    sample_rule_conditions = []
    sample_rule_outputs = []

    if "Rule Conditions" in rules_df.columns:
        sample_rule_conditions = (
            rules_df["Rule Conditions"]
            .head(3)
            .astype(str)
            .tolist()
        )

    if "Rule Outputs" in rules_df.columns:
        sample_rule_outputs = (
            rules_df["Rule Outputs"]
            .head(3)
            .astype(str)
            .tolist()
    )

    mapped_transactions_df = apply_rules(
        filtered_bank_df,
        parsed_rules,
    )

    enriched_transactions_df = enrich_transactions_with_coa(
        mapped_transactions_df,
        coa_df,
    )

    validation_summary = validate_transactions(enriched_transactions_df)

    validation_summary["filtered_transactions"] = len(filtered_bank_df)
    validation_summary["raw_rules_rows"] = raw_rules_rows
    validation_summary["rules_columns"] = rules_columns
    validation_summary["parsed_rules_count"] = parsed_rules_count
    validation_summary["rules_with_keywords_count"] = rules_with_keywords_count
    validation_summary["sample_rule_conditions"] = sample_rule_conditions
    validation_summary["sample_rule_outputs"] = sample_rule_outputs

    trial_balance_df = generate_trial_balance(enriched_transactions_df)

    pnl_df = generate_pnl(trial_balance_df)

    return build_pipeline_result(
        filtered_bank_df=filtered_bank_df,
        enriched_transactions_df=enriched_transactions_df,
        trial_balance_df=trial_balance_df,
        pnl_df=pnl_df,
        validation_summary=validation_summary,
    )