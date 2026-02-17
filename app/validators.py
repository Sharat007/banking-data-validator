"""Banking data validation rules.

Each validator function takes a row dict and row index,
returns a list of error dicts (empty if valid).
"""

import re
from datetime import datetime
from typing import Any
import collections


def validate_rows(rows: list[dict[str, Any]]) -> list[dict]:
    """Run all validation rules against every row."""
    all_errors: list[dict] = []

    # First run global rules that may need to analyze all rows (e.g. duplicates)
    for rule in GLOBAL_RULES:
        all_errors.extend(rule(rows))

    for idx, row in enumerate(rows, start=1):
        for rule in RULES:
            errors = rule(row, idx)
            all_errors.extend(errors)
    return all_errors


def _error(row: int, column: str, message: str, severity: str = "error") -> dict:
    """Create a standardized error dict."""
    return {
        "row": row,
        "column": column,
        "message": message,
        "severity": severity,
    }


# --- Individual validation rules ---


def check_required_fields(row: dict, idx: int) -> list[dict]:
    """Ensure critical fields are present and not empty."""
    required = ["account_number", "transaction_date", "amount"]
    errors: list[dict] = []
    for field in required:
        if field not in row:
            errors.append(_error(idx, field, f"Required field '{field}' is missing"))
        elif row[field] is None or str(row[field]).strip() == "":
            errors.append(_error(idx, field, f"Required field '{field}' is empty"))
    return errors


def check_duplicate_transactions(rows: list[dict[str, Any]]) -> list[dict]:
    """Check for duplicate transactions based on account_number, date, and amount."""
    seen = collections.Counter()
    for idx, row in enumerate(rows, start=1):
        key = (
            str(row.get("account_number", "")).strip(),
            str(row.get("transaction_date", "")).strip(),
            str(row.get("amount", "")).strip(),
        )
        seen[key] += 1
        if seen[key] > 1:
            return [
                _error(
                    idx,
                    "duplicate_check",
                    f"Duplicate transaction detected: {key}",
                    severity="warning",
                )
            ]

    return []


def check_account_number_format(row: dict, idx: int) -> list[dict]:
    """Account numbers should be 8-12 digits."""
    val = row.get("account_number", "")
    if not val or str(val).strip() == "":
        return []  # handled by required check
    val = str(val).strip()
    if not re.match(r"^\d{8,12}$", val):
        return [
            _error(
                idx,
                "account_number",
                f"Invalid format: '{val}' (expected 8-12 digits)",
            )
        ]
    return []


def check_amount_is_numeric(row: dict, idx: int) -> list[dict]:
    """Amount must be a valid number."""
    val = row.get("amount", "")
    if not val or str(val).strip() == "":
        return []
    try:
        float(str(val).strip().replace(",", ""))
    except ValueError:
        return [_error(idx, "amount", f"Not a valid number: '{val}'")]
    return []


def check_transaction_date_format(row: dict, idx: int) -> list[dict]:
    """Transaction date should be a valid YYYY-MM-DD date."""
    val = row.get("transaction_date", "")
    if not val or str(val).strip() == "":
        return []
    val = str(val).strip()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", val):
        return [
            _error(
                idx,
                "transaction_date",
                f"Invalid date format: '{val}' (expected YYYY-MM-DD)",
            )
        ]
    try:
        datetime.strptime(val, "%Y-%m-%d")
    except ValueError:
        return [
            _error(
                idx,
                "transaction_date",
                f"Invalid date: '{val}' is not a real calendar date",
            )
        ]
    return []


def check_currency_code(row: dict, idx: int) -> list[dict]:
    """Currency code should be a 3-letter ISO code if present."""
    val = row.get("currency", "")
    if not val or str(val).strip() == "":
        return []
    val = str(val).strip()
    if not re.match(r"^[A-Z]{3}$", val):
        return [
            _error(
                idx,
                "currency",
                f"Invalid currency code: '{val}' (expected 3-letter ISO like USD, EUR)",
                severity="warning",
            )
        ]
    return []


# Register all rules
RULES = [
    check_required_fields,
    check_account_number_format,
    check_amount_is_numeric,
    check_transaction_date_format,
    check_currency_code,
]

GLOBAL_RULES = [check_duplicate_transactions]
