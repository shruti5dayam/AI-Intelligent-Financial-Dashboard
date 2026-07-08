"""
Rule engine for GL Mapping.

Responsibilities:
- Build searchable text for each bank transaction
- Calculate transaction amount
- Detect transaction direction: Payment, Deposit, or Unknown
- Apply parsed rules to bank transactions
- Assign GL Account, Rule Name, Mapping Status, and Confidence Score
"""

from __future__ import annotations

from typing import Any

import pandas as pd


PAYMENT_COLUMN = "Payment"
DEPOSIT_COLUMN = "Deposit"


def normalize_text(value: Any) -> str:
    """
    Convert any value into lowercase searchable text.

    Parameters
    ----------
    value:
        Any value from a transaction field.

    Returns
    -------
    str
        Lowercase stripped text.
    """

    if value is None:
        return ""

    return str(value).strip().lower()


def safe_numeric(value: Any) -> float:
    """
    Convert a value to float safely.

    Parameters
    ----------
    value:
        Any numeric-looking value.

    Returns
    -------
    float
        Converted float. Returns 0.0 if conversion fails.
    """

    numeric_value = pd.to_numeric(value, errors="coerce")

    if pd.isna(numeric_value):
        return 0.0

    return float(numeric_value)


def calculate_transaction_amount(transaction: pd.Series) -> float:
    """
    Calculate signed transaction amount.

    Accounting convention used here:
    - Deposits are positive
    - Payments are negative

    Parameters
    ----------
    transaction:
        One bank transaction row.

    Returns
    -------
    float
        Signed transaction amount.
    """

    payment = safe_numeric(transaction.get(PAYMENT_COLUMN, 0.0))
    deposit = safe_numeric(transaction.get(DEPOSIT_COLUMN, 0.0))

    if deposit != 0:
        return deposit

    if payment != 0:
        return -abs(payment)

    return 0.0


def get_transaction_direction(transaction: pd.Series) -> str:
    """
    Determine whether a transaction is a Payment, Deposit, or Unknown.

    Parameters
    ----------
    transaction:
        One bank transaction row.

    Returns
    -------
    str
        Payment, Deposit, or Unknown.
    """

    payment = safe_numeric(transaction.get(PAYMENT_COLUMN, 0.0))
    deposit = safe_numeric(transaction.get(DEPOSIT_COLUMN, 0.0))

    if deposit != 0:
        return "Deposit"

    if payment != 0:
        return "Payment"

    return "Unknown"


def build_transaction_text(transaction: pd.Series) -> str:
    """
    Build searchable transaction text from common bank statement fields.

    Parameters
    ----------
    transaction:
        One bank transaction row.

    Returns
    -------
    str
        Combined lowercase searchable text.
    """

    searchable_columns = [
        "Payee",
        "Memo",
        "Account",
        "Store",
        "Source File",
    ]

    text_parts = []

    for column in searchable_columns:
        if column in transaction.index:
            text_parts.append(normalize_text(transaction.get(column)))

    return " ".join(text_parts)


def rule_direction_matches(rule: dict[str, Any], transaction_direction: str) -> bool:
    """
    Check whether a rule applies to the transaction direction.

    Parameters
    ----------
    rule:
        Parsed rule dictionary.

    transaction_direction:
        Payment, Deposit, or Unknown.

    Returns
    -------
    bool
        True if direction matches.
    """

    rule_direction = rule.get("transaction_direction", "Any")

    if rule_direction == "Any":
        return True

    return rule_direction == transaction_direction


def score_rule_match(rule: dict[str, Any], transaction_text: str) -> float:
    """
    Score how well a rule matches a transaction.

    Parameters
    ----------
    rule:
        Parsed rule dictionary.

    transaction_text:
        Searchable transaction text.

    Returns
    -------
    float
        Match score between 0.0 and 1.0.
    """

    keywords = rule.get("keywords", [])

    if not keywords:
        return 0.0

    matched_keywords = [
        keyword
        for keyword in keywords
        if normalize_text(keyword) in transaction_text
    ]

    if not matched_keywords:
        return 0.0

    return len(matched_keywords) / len(keywords)


def find_best_rule_match(
    transaction: pd.Series,
    parsed_rules: list[dict[str, Any]],
) -> tuple[dict[str, Any] | None, float]:
    """
    Find the best matching rule for a transaction.

    Parameters
    ----------
    transaction:
        One bank transaction row.

    parsed_rules:
        List of parsed rule dictionaries.

    Returns
    -------
    tuple[dict[str, Any] | None, float]
        Best matching rule and confidence score.
    """

    transaction_text = build_transaction_text(transaction)
    transaction_direction = get_transaction_direction(transaction)

    best_rule = None
    best_score = 0.0

    for rule in parsed_rules:
        if not rule_direction_matches(rule, transaction_direction):
            continue

        score = score_rule_match(rule, transaction_text)

        if score > best_score:
            best_score = score
            best_rule = rule

    return best_rule, best_score


def apply_rules(
    bank_df: pd.DataFrame,
    parsed_rules: list[dict[str, Any]],
) -> pd.DataFrame:
    """
    Apply parsed rules to all bank transactions.

    Parameters
    ----------
    bank_df:
        Bank statement DataFrame.

    parsed_rules:
        List of parsed rule dictionaries.

    Returns
    -------
    pd.DataFrame
        Bank transactions with GL mapping columns added.
    """

    if bank_df.empty:
        return bank_df.copy()

    mapped_df = bank_df.copy()

    mapped_df["Amount"] = mapped_df.apply(
        calculate_transaction_amount,
        axis=1,
    )

    mapped_df["Transaction Direction"] = mapped_df.apply(
        get_transaction_direction,
        axis=1,
    )

    mapped_df["GL Account"] = ""
    mapped_df["Rule Name"] = "Unmatched"
    mapped_df["Mapping Status"] = "Unmatched"
    mapped_df["Confidence Score"] = 0.0

    for index, transaction in mapped_df.iterrows():
        best_rule, confidence_score = find_best_rule_match(
            transaction,
            parsed_rules,
        )

        if best_rule is None:
            continue

        mapped_df.at[index, "GL Account"] = best_rule.get("account_name", "")
        mapped_df.at[index, "Rule Name"] = best_rule.get("rule_name", "")
        mapped_df.at[index, "Mapping Status"] = "Mapped"
        mapped_df.at[index, "Confidence Score"] = round(confidence_score, 4)

    return mapped_df