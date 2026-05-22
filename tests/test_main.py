import pytest
from unittest.mock import patch
from src.main import main

class TestMain:
    @patch("builtins.print")
    @patch("builtins.input")
    @patch("src.main.load_transactions")
    def test_invalid_menu_choice(self, mock_load, mock_input, mock_print):
        mock_input.side_effect = ["4"]
        with pytest.raises(SystemExit):
            main()
        mock_load.assert_not_called()
        mock_print.assert_any_call("Неверный выбор. Завершение программы.")

    @patch("builtins.print")
    @patch("builtins.input")
    @patch("src.main.load_transactions")
    def test_load_data_failed(self, mock_load, mock_input, mock_print):
        mock_input.side_effect = ["1", "data/empty.json"]
        mock_load.return_value = []
        main()
        mock_load.assert_called_once_with("data/empty.json")
        mock_print.assert_any_call(
            "Не удалось загрузить транзакции. Проверьте путь к файлу и его содержимое."
        )

    @patch("builtins.print")
    @patch("builtins.input")
    @patch("src.main.load_transactions")
    @patch("src.main.filter_by_state")
    @patch("src.main.sort_by_date")
    @patch("src.main.search_transactions")
    @patch("src.main.mask_account_card")
    @patch("src.main.get_date")
    def test_full_flow_no_extra_filters(
        self,
        mock_get_date,
        mock_mask_card,
        mock_search,
        mock_sort,
        mock_filter,
        mock_load,
        mock_input,
        mock_print,
    ):
        mock_input.side_effect = [
            "1", "data/valid.json",
            "EXECUTED",
            "нет", "нет", "нет"
        ]
        mock_load.return_value = [{"id": 1, "state": "EXECUTED"}]
        tx = {
            "date": "2021-01-01T00:00:00",
            "description": "Тест",
            "operationAmount": {"amount": "100", "currency": {"code": "USD"}},
            "from": "Visa 1234567812345678",
            "to": "Счет 12345678901234567890",
        }
        mock_filter.return_value = [tx]
        mock_get_date.return_value = "01.01.2021"
        mock_mask_card.side_effect = lambda x: "Visa 1234 56** **** 5678" if "Visa" in x else "Счет **7890"
        main()
        mock_load.assert_called_once_with("data/valid.json")
        mock_filter.assert_called_once()
        mock_sort.assert_not_called()
        mock_search.assert_not_called()
        mock_print.assert_any_call("01.01.2021 Тест")
        mock_print.assert_any_call("Visa 1234 56** **** 5678 -> Счет **7890")
        mock_print.assert_any_call("Сумма: 100 USD")

    @patch("builtins.print")
    @patch("builtins.input")
    @patch("src.main.load_transactions")
    @patch("src.main.filter_by_state")
    @patch("src.main.sort_by_date")
    def test_status_invalid_loop(self, mock_sort, mock_filter, mock_load, mock_input, mock_print):
        mock_input.side_effect = [
            "1", "data/valid.json",
            "test", "CANCELED",
            "нет", "нет", "нет"
        ]
        mock_load.return_value = [{"id": 1, "state": "CANCELED"}]
        mock_filter.return_value = [{"id": 1, "state": "CANCELED"}]
        main()
        mock_print.assert_any_call('Статус операции "test" недоступен.')
        mock_filter.assert_called_once()
        args, _ = mock_filter.call_args
        assert args[1] == "CANCELED"

    @patch("builtins.print")
    @patch("builtins.input")
    @patch("src.main.load_transactions")
    @patch("src.main.filter_by_state")
    @patch("src.main.sort_by_date")
    def test_sort_by_date_descending(self, mock_sort, mock_filter, mock_load, mock_input, mock_print):
        mock_input.side_effect = [
            "1", "data/valid.json",
            "EXECUTED",
            "да", "по убыванию",
            "нет", "нет"
        ]
        mock_load.return_value = [{"id": 1}]
        mock_filter.return_value = [{"id": 1}]
        mock_sort.return_value = [{"id": 1}]
        main()
        mock_sort.assert_called_once()
        _, kwargs = mock_sort.call_args
        assert kwargs.get("reverse") is True

    @patch("builtins.print")
    @patch("builtins.input")
    @patch("src.main.load_transactions")
    @patch("src.main.filter_by_state")
    @patch("src.main.search_transactions")
    def test_filter_by_word(self, mock_search, mock_filter, mock_load, mock_input, mock_print):
        mock_input.side_effect = [
            "1", "data/valid.json",
            "EXECUTED",
            "нет", "нет",
            "да", "перевод"
        ]
        mock_load.return_value = [{"id": 1, "description": "Перевод организации"}]
        mock_filter.return_value = [{"id": 1, "description": "Перевод организации"}]
        mock_search.return_value = [{"id": 1, "description": "Перевод организации"}]
        main()
        mock_search.assert_called_once()
        args, _ = mock_search.call_args
        assert args[1] == "перевод"

    @patch("builtins.print")
    @patch("builtins.input")
    @patch("src.main.load_transactions")
    @patch("src.main.filter_by_state")
    def test_empty_result(self, mock_filter, mock_load, mock_input, mock_print):
        mock_input.side_effect = [
            "1", "data/valid.json",
            "EXECUTED",
            "нет", "нет", "нет"
        ]
        mock_load.return_value = [{"id": 1, "state": "EXECUTED"}]
        mock_filter.return_value = []
        main()
        mock_print.assert_any_call(
            "Не найдено ни одной транзакции, подходящей под ваши условия фильтрации"
        )

    @patch("builtins.print")
    @patch("builtins.input")
    @patch("src.main.read_csv")
    @patch("src.main.filter_by_state")
    def test_csv_source(self, mock_filter, mock_read_csv, mock_input, mock_print):
        mock_input.side_effect = [
            "2", "data/test.csv",
            "EXECUTED",
            "нет", "нет", "нет"
        ]
        mock_read_csv.return_value = [{"id": 1}]
        mock_filter.return_value = [{"id": 1}]
        main()
        mock_read_csv.assert_called_once_with("data/test.csv")

    @patch("builtins.print")
    @patch("builtins.input")
    @patch("src.main.read_xlsx")
    @patch("src.main.filter_by_state")
    def test_xlsx_source(self, mock_filter, mock_read_xlsx, mock_input, mock_print):
        mock_input.side_effect = [
            "3", "data/test.xlsx",
            "EXECUTED",
            "нет", "нет", "нет"
        ]
        mock_read_xlsx.return_value = [{"id": 1}]
        mock_filter.return_value = [{"id": 1}]
        main()
        mock_read_xlsx.assert_called_once_with("data/test.xlsx")

    @patch("builtins.print")
    @patch("builtins.input")
    @patch("src.main.load_transactions")
    @patch("src.main.filter_by_state")
    def test_rub_filter(self, mock_filter, mock_load, mock_input, mock_print):
        mock_input.side_effect = [
            "1", "data/valid.json",
            "EXECUTED",
            "нет",
            "да",
            "нет"
        ]
        mock_load.return_value = [
            {"id": 1, "operationAmount": {"currency": {"code": "RUB"}}},
            {"id": 2, "operationAmount": {"currency": {"code": "USD"}}},
        ]
        mock_filter.return_value = mock_load.return_value.copy()
        main()
        mock_print.assert_any_call("Всего банковских операций в выборке: 1")