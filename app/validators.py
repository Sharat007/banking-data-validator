"""Banking data validation rules.

Each validator function takes a row dict and row index,
returns a list of error dicts (empty if valid).
"""

import collections
import re
from datetime import datetime
from typing import Any


def validate_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Run all validation rules against every row."""
    all_errors: list[dict[str, Any]] = []

    # First run global rules that may need to analyze all rows (e.g. duplicates)
    for global_rule in GLOBAL_RULES:
        all_errors.extend(global_rule(rows))

    for idx, row in enumerate(rows, start=1):
        for row_rule in RULES:
            errors = row_rule(row, idx)
            all_errors.extend(errors)
    return all_errors


def _error(row: int, column: str, message: str, severity: str = "error") -> dict[str, Any]:
    """Create a standardized error dict."""
    return {
        "row": row,
        "column": column,
        "message": message,
        "severity": severity,
    }


# --- Individual validation rules ---


def check_required_fields(row: dict[str, Any], idx: int) -> list[dict[str, Any]]:
    """Ensure critical fields are present and not empty."""
    required = ["account_number", "transaction_date", "amount"]
    errors: list[dict[str, Any]] = []
    for field in required:
        if field not in row:
            errors.append(_error(idx, field, f"Required field '{field}' is missing"))
        elif row[field] is None or str(row[field]).strip() == "":
            errors.append(_error(idx, field, f"Required field '{field}' is empty"))
    return errors


def check_duplicate_transactions(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Check for duplicate transactions based on account_number, date, and amount."""
    seen: collections.Counter[tuple[str, ...]] = collections.Counter()
    errors: list[dict[str, Any]] = []
    for idx, row in enumerate(rows, start=1):
        key = (
            str(row.get("account_number", "")).strip(),
            str(row.get("transaction_date", "")).strip(),
            str(row.get("amount", "")).strip(),
            str(row.get("currency", "")).strip(),
        )
        seen[key] += 1
        if seen[key] > 1:
            errors.append(
                _error(
                    idx,
                    "duplicate_check",
                    f"Duplicate transaction detected: {key}",
                    severity="warning",
                )
            )

    return errors


def check_account_number_format(row: dict[str, Any], idx: int) -> list[dict[str, Any]]:
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


def check_amount_is_numeric(row: dict[str, Any], idx: int) -> list[dict[str, Any]]:
    """Amount must be a valid number."""
    val = row.get("amount", "")
    if not val or str(val).strip() == "":
        return []
    try:
        float(str(val).strip().replace(",", ""))
    except ValueError:
        return [_error(idx, "amount", f"Not a valid number: '{val}'")]
    return []


def check_transaction_date_format(row: dict[str, Any], idx: int) -> list[dict[str, Any]]:
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


def check_currency_code(row: dict[str, Any], idx: int) -> list[dict[str, Any]]:
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
