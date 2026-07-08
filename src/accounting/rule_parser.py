"""
Rule parser for Bank Feed Rules.

Responsibilities:
- Safely parse JSON stored inside Excel rule columns
- Convert each rule row into a structured Python dictionary
- Extract searchable keywords from rule conditions
- Extract mapped GL account name from rule actions
- Preserve rule name for audit trail

Current supported rule JSON shape:

Rule Conditions:
{
    "ruleConditions": [
        {"ruleType": 10, "value": "1"},
        {"ruleType": 1, "value": "ORIG CO NAME:Cash Connect"}
    ],
    "isAndRule": true
}

Rule Outputs:
{
    "ruleActions": [
        {"actionType": 0, "value": "Sales"},
        {"actionType": 3, "value": "DD14"}
    ]
}
"""

from __future__ import annotations

import ast
import json
from typing import Any

import pandas as pd


RULE_NAME_COLUMN = "Rule Name"
RULE_CONDITIONS_COLUMN = "Rule Conditions"
RULE_OUTPUTS_COLUMN = "Rule Outputs"

# In the current CloFast/bank-feed rule JSON:
# actionType 0 stores the mapped GL/account/category name.
ACCOUNT_ACTION_TYPE = 0

# In the current rule condition JSON:
# ruleType 1 stores searchable text such as memo/payee keywords.
KEYWORD_RULE_TYPE = 1


IGNORED_KEYWORDS = {
    "",
    "and",
    "or",
    "contains",
    "equals",
    "equal",
    "memo",
    "payee",
    "description",
    "payment",
    "deposit",
    "field",
    "operator",
    "value",
    "type",
    "condition",
    "conditions",
    "rules",
    "rule",
    "all",
    "any",
}


def load_json_value(value: Any) -> Any:
    """
    Safely convert a JSON-like Excel value into a Python object.

    Parameters
    ----------
    value:
        Value from Excel. It may be JSON text, Python-like dict text,
        dict, list, blank, or NaN.

    Returns
    -------
    Any
        Parsed Python object. Usually dict or list.
        Returns empty dict if parsing fails.
    """

    if value is None:
        return {}

    if isinstance(value, (dict, list)):
        return value

    if pd.isna(value):
        return {}

    value_text = str(value).strip()

    if not value_text:
        return {}

    try:
        return json.loads(value_text)
    except json.JSONDecodeError:
        pass

    try:
        return ast.literal_eval(value_text)
    except (ValueError, SyntaxError):
        return {}


def normalize_text(value: Any) -> str:
    """
    Normalize a value into lowercase searchable text.

    Parameters
    ----------
    value:
        Any input value.

    Returns
    -------
    str
        Lowercase stripped string.
    """

    if value is None:
        return ""

    return str(value).strip().lower()


def clean_keyword(value: Any) -> str:
    """
    Clean a rule keyword.

    Parameters
    ----------
    value:
        Raw keyword value from rule conditions.

    Returns
    -------
    str
        Clean lowercase keyword.
    """

    keyword = normalize_text(value)

    if keyword in IGNORED_KEYWORDS:
        return ""

    # Ignore pure numbers like "1" from ruleType 10.
    if keyword.isdigit():
        return ""

    return keyword


def extract_keywords_from_rule_conditions(conditions: dict[str, Any]) -> list[str]:
    """
    Extract keywords from the known CloFast ruleConditions structure.

    Parameters
    ----------
    conditions:
        Parsed Rule Conditions JSON.

    Returns
    -------
    list[str]
        Unique lowercase keywords.
    """

    keywords = []

    rule_conditions = conditions.get("ruleConditions", [])

    if not isinstance(rule_conditions, list):
        return keywords

    for condition in rule_conditions:
        if not isinstance(condition, dict):
            continue

        rule_type = condition.get("ruleType")
        value = condition.get("value")

        # ruleType 1 is the useful transaction text keyword.
        if rule_type != KEYWORD_RULE_TYPE:
            continue

        keyword = clean_keyword(value)

        if keyword and keyword not in keywords:
            keywords.append(keyword)

    return keywords


def walk_json_values(value: Any) -> list[str]:
    """
    Recursively collect string values from a JSON-like object.

    This is used as a fallback when the JSON shape is not the expected
    ruleConditions/ruleActions format.

    Parameters
    ----------
    value:
        Dict, list, string, number, or any JSON-like value.

    Returns
    -------
    list[str]
        List of string values found inside the object.
    """

    values = []

    if isinstance(value, dict):
        for nested_value in value.values():
            values.extend(walk_json_values(nested_value))

    elif isinstance(value, list):
        for item in value:
            values.extend(walk_json_values(item))

    elif isinstance(value, str):
        values.append(value)

    elif isinstance(value, (int, float)):
        values.append(str(value))

    return values


def extract_keywords(conditions: Any) -> list[str]:
    """
    Extract searchable keywords from Rule Conditions JSON.

    Parameters
    ----------
    conditions:
        Parsed Rule Conditions JSON.

    Returns
    -------
    list[str]
        Unique lowercase keywords used for transaction matching.
    """

    if isinstance(conditions, dict):
        keywords = extract_keywords_from_rule_conditions(conditions)

        if keywords:
            return keywords

    # Fallback for unknown JSON shapes.
    keywords = []

    for value in walk_json_values(conditions):
        keyword = clean_keyword(value)

        if keyword and keyword not in keywords:
            keywords.append(keyword)

    return keywords


def extract_transaction_direction(conditions: Any) -> str:
    """
    Extract transaction direction from rule conditions.

    Parameters
    ----------
    conditions:
        Parsed Rule Conditions JSON.

    Returns
    -------
    str
        Payment, Deposit, or Any.
    """

    condition_text = " ".join(
        normalize_text(value)
        for value in walk_json_values(conditions)
    )

    if "payment" in condition_text:
        return "Payment"

    if "deposit" in condition_text:
        return "Deposit"

    return "Any"


def extract_account_name_from_rule_actions(outputs: dict[str, Any]) -> str:
    """
    Extract mapped account name from known ruleActions structure.

    Parameters
    ----------
    outputs:
        Parsed Rule Outputs JSON.

    Returns
    -------
    str
        Mapped GL account name.
    """

    rule_actions = outputs.get("ruleActions", [])

    if not isinstance(rule_actions, list):
        return ""

    for action in rule_actions:
        if not isinstance(action, dict):
            continue

        action_type = action.get("actionType")

        if action_type != ACCOUNT_ACTION_TYPE:
            continue

        account_name = str(action.get("value", "")).strip()

        if account_name:
            return account_name

    return ""


def extract_account_name(outputs: Any) -> str:
    """
    Extract mapped GL account name from Rule Outputs JSON.

    Parameters
    ----------
    outputs:
        Parsed Rule Outputs JSON.

    Returns
    -------
    str
        Account name found in outputs, or empty string.
    """

    if not outputs:
        return ""

    if isinstance(outputs, dict):
        account_name = extract_account_name_from_rule_actions(outputs)

        if account_name:
            return account_name

    return ""


def parse_rule(rule_row: pd.Series) -> dict[str, Any]:
    """
    Parse one rules DataFrame row into a structured rule dictionary.

    Parameters
    ----------
    rule_row:
        One row from the rules DataFrame.

    Returns
    -------
    dict[str, Any]
        Structured rule dictionary.
    """

    conditions = load_json_value(rule_row.get(RULE_CONDITIONS_COLUMN))
    outputs = load_json_value(rule_row.get(RULE_OUTPUTS_COLUMN))

    return {
        "rule_name": str(rule_row.get(RULE_NAME_COLUMN, "")).strip(),
        "conditions": conditions,
        "outputs": outputs,
        "keywords": extract_keywords(conditions),
        "transaction_direction": extract_transaction_direction(conditions),
        "account_name": extract_account_name(outputs),
    }


def parse_rules(rules_df: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Parse all rules from a rules DataFrame.

    Parameters
    ----------
    rules_df:
        DataFrame read from the Bank Feed Rules Excel file.

    Returns
    -------
    list[dict[str, Any]]
        List of structured rule dictionaries.
    """

    parsed_rules = []

    if rules_df.empty:
        return parsed_rules

    for _, rule_row in rules_df.iterrows():
        parsed_rule = parse_rule(rule_row)

        if not parsed_rule["rule_name"]:
            continue

        if not parsed_rule["account_name"]:
            continue

        if not parsed_rule["keywords"]:
            continue

        parsed_rules.append(parsed_rule)

    return parsed_rules