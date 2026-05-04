import pytest
from unittest.mock import patch, Mock
from src.external_api import convert_currency


class TestConvertCurrency:
    @patch("src.external_api.API_KEY", "fake_key")
    @patch("src.external_api.requests.get")
    def test_convert_usd_to_rub(self, mock_get):
        """Успешная конвертация USD → RUB"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "rates": {"RUB": 90.5}}
        mock_get.return_value = mock_response
        result = convert_currency(100.5, "USD", "RUB")
        assert result == pytest.approx(100.5 * 90.5)

    @patch("src.external_api.API_KEY", "fake_key")
    @patch("src.external_api.requests.get")
    def test_convert_eur_to_usd(self, mock_get):
        """Успешная конвертация EUR → USD"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "rates": {"USD": 1.12}}
        mock_get.return_value = mock_response
        result = convert_currency(50, "EUR", "USD")
        assert result == 50 * 1.12

    def test_same_currency(self):
        """Конвертация из валюты в ту же валюту — без вызова API"""
        assert convert_currency(100, "RUB", "RUB") == 100
        assert convert_currency(50, "USD", "USD") == 50

    @patch("src.external_api.API_KEY", None)
    def test_missing_api_key(self):
        """Отсутствует API_KEY в .env"""
        with pytest.raises(ValueError, match="API key not found. Set API_KEY in .env"):
            convert_currency(10, "USD", "RUB")

    @patch("src.external_api.API_KEY", "fake_key")
    @patch("src.external_api.requests.get")
    def test_api_request_failure(self, mock_get):
        """Ошибка сети при запросе к API"""
        mock_get.side_effect = ConnectionError("Network error")
        with pytest.raises(ConnectionError, match="Failed to fetch exchange rate"):
            convert_currency(10, "USD", "RUB")

    @patch("src.external_api.API_KEY", "fake_key")
    @patch("src.external_api.requests.get")
    def test_api_unsuccessful_response(self, mock_get):
        """API вернул success=False"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": False,
            "error": {"info": "Invalid API key"},
        }
        mock_get.return_value = mock_response
        with pytest.raises(ValueError, match="API error: Invalid API key"):
            convert_currency(10, "USD", "RUB")

    @patch("src.external_api.API_KEY", "fake_key")
    @patch("src.external_api.requests.get")
    def test_missing_rub_rate(self, mock_get):
        """В ответе API нет курса RUB"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "rates": {"EUR": 0.9}}
        mock_get.return_value = mock_response
        with pytest.raises(ValueError, match="Rate for RUB not found"):
            convert_currency(10, "USD", "RUB")
