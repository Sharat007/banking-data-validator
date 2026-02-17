"""Tests for the /validate endpoint."""

import io

from fastapi.testclient import TestClient

from tests.conftest import client


def _upload_csv(client: TestClient, content: str, filename: str = "test.csv"):
    """Helper to upload CSV content to the validate endpoint."""
    return client.post(
        "/validate",
        files={"file": (filename, io.BytesIO(content.encode()), "text/csv")},
    )


class TestValidateEndpoint:
    """Tests for POST /validate."""

    def test_valid_csv_returns_no_errors(self, client: TestClient):
        csv = "account_number,transaction_date,amount,currency\n12345678,2024-01-15,100.50,USD\n"
        resp = _upload_csv(client, csv)
        data = resp.json()
        assert resp.status_code == 200
        assert data["valid"] is True
        assert data["errors_found"] == 0
        assert data["total_rows"] == 1

    def test_missing_required_field_amount(self, client: TestClient):
        csv = "account_number,transaction_date,amount\n12345678,2024-01-15,\n"
        resp = _upload_csv(client, csv)
        data = resp.json()
        assert data["valid"] is False
        assert any(e["column"] == "amount" for e in data["errors"])

    def test_invalid_account_number_format(self, client: TestClient):
        csv = "account_number,transaction_date,amount\nABC,2024-01-15,100\n"
        resp = _upload_csv(client, csv)
        data = resp.json()
        assert data["valid"] is False
        assert any(e["column"] == "account_number" for e in data["errors"])

    def test_invalid_date_format(self, client: TestClient):
        csv = "account_number,transaction_date,amount\n12345678,01-15-2024,100\n"
        resp = _upload_csv(client, csv)
        data = resp.json()
        assert data["valid"] is False
        assert any(e["column"] == "transaction_date" for e in data["errors"])

    def test_non_numeric_amount(self, client: TestClient):
        csv = "account_number,transaction_date,amount\n12345678,2024-01-15,abc\n"
        resp = _upload_csv(client, csv)
        data = resp.json()
        assert data["valid"] is False
        assert any(e["column"] == "amount" for e in data["errors"])

    def test_invalid_currency_code(self, client: TestClient):
        csv = "account_number,transaction_date,amount,currency\n12345678,2024-01-15,100,us\n"
        resp = _upload_csv(client, csv)
        data = resp.json()
        assert data["valid"] is False
        assert any(e["column"] == "currency" for e in data["errors"])

    def test_rejects_non_csv_file(self, client: TestClient):
        resp = client.post(
            "/validate",
            files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
        )
        assert resp.status_code == 400

    def test_empty_csv_returns_400(self, client: TestClient):
        resp = _upload_csv(client, "account_number,transaction_date,amount\n")
        assert resp.status_code == 400

    def test_multiple_errors_in_one_row(self, client: TestClient):
        csv = "account_number,transaction_date,amount\nBAD,not-a-date,xyz\n"
        resp = _upload_csv(client, csv)
        data = resp.json()
        assert data["errors_found"] >= 3

    def test_multiple_rows_mixed_valid_invalid(self, client: TestClient):
        csv = (
            "account_number,transaction_date,amount\n"
            "12345678,2024-01-15,100\n"
            "BAD,2024-01-15,100\n"
            "12345678,2024-01-15,200\n"
        )
        resp = _upload_csv(client, csv)
        data = resp.json()
        assert data["total_rows"] == 3
        assert data["valid"] is False
        assert all(e["row"] == 2 for e in data["errors"])

    def test_non_utf8_file_returns_400(self, client: TestClient):
        resp = client.post(
            "/validate",
            files={"file": ("test.csv", io.BytesIO(b"\xff\xfe"), "text/csv")},
        )
        assert resp.status_code == 400
        assert resp.json()["error"] == "File must be UTF-8 encoded"

    def test_missing_required_column_detected(self, client: TestClient):
        csv = "transaction_date,amount\n2024-01-15,100\n"
        resp = _upload_csv(client, csv)
        data = resp.json()
        assert data["valid"] is False
        assert any(
            e["column"] == "account_number" and "missing" in e["message"]
            for e in data["errors"]
        )

    def test_impossible_date_rejected(self, client: TestClient):
        csv = "account_number,transaction_date,amount\n12345678,2024-02-30,100\n"
        resp = _upload_csv(client, csv)
        data = resp.json()
        assert data["valid"] is False
        assert any(
            e["column"] == "transaction_date" and "not a real" in e["message"]
            for e in data["errors"]
        )

    def test_csv_duplicate_transactions(self, client: TestClient):
        csv = (
            "account_number,transaction_date,amount,currency\n"
            "12345678,2024-01-15,100.50,USD\n"
            "12345678,2024-01-15,100.50,USD\n"
        )
        resp = _upload_csv(client, csv)
        data = resp.json()
        assert data["valid"] is False
        assert any(
            e["row"] == 2 and "Duplicate transaction detected" in e["message"]
            for e in data["errors"]
        )

    def test_csv_unique_transactions(self, client: TestClient):
        csv = (
            "account_number,transaction_date,amount,currency\n"
            "12345678,2024-01-15,100.50,USD\n"
            "12345678,2024-01-15,101.50,USD\n"
        )
        resp = _upload_csv(client, csv)
        data = resp.json()
        assert data["valid"] is True
        assert data["errors_found"] == 0
        assert data["total_rows"] == 2
        
    def test_csv_multiple_duplicate_transactions(self, client: TestClient):
        csv = (
            "account_number,transaction_date,amount,currency\n"
            "12345678,2024-01-15,100.50,USD\n"
            "12345678,2024-01-15,100.50,USD\n"
            "12345678,2024-01-15,100.50,USD\n"
        )
        resp = _upload_csv(client, csv)
        data = resp.json()
        dup_errors = [e for e in data["errors"] if "Duplicate" in e["message"]]
        assert len(dup_errors) == 2  # rows 2 and 3
