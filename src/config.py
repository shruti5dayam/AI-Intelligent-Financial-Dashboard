"""
Configuration constants for AI Intelligent Financial Dashboard.

This file stores values that are used across the application.
Keeping them here avoids repeating hardcoded values in multiple files.
"""

from pathlib import Path


# ---------------------------------------------------------
# APP DISPLAY SETTINGS
# ---------------------------------------------------------

APP_TITLE = "AI Intelligent Financial Dashboard"

APP_CAPTION = (
    "Upload bank statements, detect metadata, select reporting scope, "
    "and generate financial reports."
)


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"

OUTPUT_DIR = BASE_DIR / "output"
REPORTS_DIR = OUTPUT_DIR / "reports"


# ---------------------------------------------------------
# BANK STATEMENT CONFIGURATION
# ---------------------------------------------------------

EXPECTED_BANK_COLUMNS = {
    "date",
    "payee",
    "account",
    "memo",
    "payment",
    "deposit",
    "store",
    "balance",
}

HEADER_CANDIDATES = (0, 1, 2)
# ---------------------------------------------------------
# BANK ACCOUNT DETECTION CONFIGURATION
# ---------------------------------------------------------

US_BANK_NAME_KEYWORDS = [
    "chase",
    "jp morgan",
    "jpmorgan",
    "bank of america",
    "boa",
    "wells fargo",
    "citibank",
    "citi",
    "capital one",
    "us bank",
    "u.s. bank",
    "pnc",
    "truist",
    "td bank",
    "citizens",
    "regions",
    "keybank",
    "bmo",
    "fifth third",
    "huntington",
    "m&t bank",
    "first citizens",
]

BANK_ACCOUNT_TYPE_KEYWORDS = [
    "checking",
    "savings",
    "operating",
    "business checking",
    "merchant account",
]

# ---------------------------------------------------------
# REPORT FILTER DEFAULTS
# ---------------------------------------------------------

ALL_OPTION = "All"

PERIOD_TYPES = [
    "All",
    "Month",
    "Quarter",
]