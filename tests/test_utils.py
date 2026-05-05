import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from src.utils import load_transactions, get_transaction_amount_in_rub


class TestLoadTransactions:
    def test_valid_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            data = [{"id": 1, "amount": 100}]
            json.dump(data, tmp)
            tmp_path = tmp.name
        result = load_transactions(tmp_path)
        assert result == data
        Path(tmp_path).unlink()

    def test_file_not_found(self):
        assert load_transactions("nonexistent.json") == []

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp.write("")
            tmp_path = tmp.name
        result = load_transactions(tmp_path)
        assert result == []
        Path(tmp_path).unlink()

    def test_invalid_json(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp.write("not a json")
            tmp_path = tmp.name
        result = load_transactions(tmp_path)
        assert result == []
        Path(tmp_path).unlink()

    def test_not_a_list(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            json.dump({"key": "value"}, tmp)
            tmp_path = tmp.name
        result = load_transactions(tmp_path)
        assert result == []
        Path(tmp_path).unlink()


class TestGetTransactionAmountInRub:
    def test_rub_transaction(self):
        tx = {"id": 1, "operationAmount": {"amount": "100.50", "currency": {"code": "RUB"}}}
        assert get_transaction_amount_in_rub(tx) == 100.50

    @patch("src.external_api.convert_currency")
    def test_usd_transaction(self, mock_convert):
        mock_convert.return_value = 100.50 * 90.0
        tx = {"id": 2, "operationAmount": {"amount": "100.50", "currency": {"code": "USD"}}}
        assert get_transaction_amount_in_rub(tx) == 100.50 * 90.0

    @patch("src.external_api.convert_currency")
    def test_eur_transaction(self, mock_convert):
        mock_convert.return_value = 50.0 * 98.0
        tx = {"id": 3, "operationAmount": {"amount": "50.0", "currency": {"code": "EUR"}}}
        assert get_transaction_amount_in_rub(tx) == 50.0 * 98.0

    def test_unknown_currency(self):
        tx = {"id": 4, "operationAmount": {"amount": "100", "currency": {"code": "BTC"}}}
        assert get_transaction_amount_in_rub(tx) == 0.0

    def test_missing_amount(self):
        tx = {"id": 5, "operationAmount": {"currency": {"code": "USD"}}}
        assert get_transaction_amount_in_rub(tx) == 0.0   # amount=0, не идёт в API

    def test_invalid_amount_string(self):
        tx = {"id": 6, "operationAmount": {"amount": "not a number", "currency": {"code": "USD"}}}
        assert get_transaction_amount_in_rub(tx) == 0.0   # amount=0

    def test_missing_operation_amount(self):
        tx = {"id": 7}
        assert get_transaction_amount_in_rub(tx) == 0.0   # amount=0

    @patch("src.external_api.convert_currency")
    def test_conversion_error(self, mock_convert):
        mock_convert.side_effect = ValueError("API error")
        tx = {"id": 8, "operationAmount": {"amount": "10", "currency": {"code": "USD"}}}
        with pytest.raises(ValueError, match="API error"):
            get_transaction_amount_in_rub(tx)

    @patch("src.external_api.convert_currency")
    def test_conversion_connection_error(self, mock_convert):
        mock_convert.side_effect = ConnectionError("Network error")
        tx = {"id": 9, "operationAmount": {"amount": "10", "currency": {"code": "USD"}}}
        with pytest.raises(ConnectionError, match="Network error"):
            get_transaction_amount_in_rub(tx)
