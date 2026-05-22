import pytest
from unittest.mock import patch, MagicMock
from src.main import main


class TestMain:
    @patch("builtins.print")
    @patch("builtins.input")
    @patch("main.load_transactions")
    def test_invalid_menu_choice(self, mock_load, mock_input, mock_print):
        """Неверный выбор пункта меню -> завершение."""
        mock_input.side_effect = ["4"]
        with pytest.raises(SystemExit):
            main()
        mock_load.assert_not_called()
        mock_print.assert_any_call("Неверный выбор. Завершение программы.")

    @patch("builtins.print")
    @patch("builtins.input")
    @patch("main.load_transactions")
    def test_load_data_failed(self, mock_load, mock_input, mock_print):
        """Загрузка данных вернула пустой список."""
        mock_input.side_effect = ["1", "data/empty.json"]
        mock_load.return_value = []
        main()
        mock_load.assert_called_once_with("data/empty.json")
        mock_print.assert_any_call(
            "Не удалось загрузить транзакции. Проверьте путь к файлу и его содержимое."
        )

    @patch("builtins.print")
    @patch("builtins.input")
    @patch("main.load_transactions")
    @patch("main.filter_by_state")
    @patch("main.sort_by_date")
    @patch("main.search_transactions")
    @patch("main.mask_account_card")
    @patch("main.get_date")
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
        """Полный сценарий без дополнительных фильтров (сортировка, рубль, поиск)."""
        mock_input.side_effect = [
            "1",                 # пункт меню
            "data/valid.json",   # путь к файлу
            "EXECUTED",          # статус
            "нет",               # сортировка по дате?
            "нет",               # только рублёвые?
            "нет",               # поиск по слову?
        ]
        mock_load.return_value = [{"id": 1, "state": "EXECUTED"}]
        mock_filter.return_value = [{"id": 1, "state": "EXECUTED"}]

        # Настройка моков для вывода
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

        # Проверяем вызовы
        mock_load.assert_called_once_with("data/valid.json")
        mock_filter.assert_called_once()
        mock_sort.assert_not_called()
        mock_search.assert_not_called()
        # Проверяем вывод
        mock_print.assert_any_call("01.01.2021 Тест")
        mock_print.assert_any_call("Visa 1234 56** **** 5678 -> Счет **7890")
        mock_print.assert_any_call("Сумма: 100 USD")

    @patch("builtins.print")
    @patch("builtins.input")
    @patch("main.load_transactions")
    @patch("main.filter_by_state")
    @patch("main.sort_by_date")
    def test_status_invalid_loop(self, mock_sort, mock_filter, mock_load, mock_input, mock_print):
        """Пользователь вводит неверный статус несколько раз, затем верный."""
        mock_input.side_effect = [
            "1", "data/valid.json",
            "test",      # неверный
            "CANCELED",  # верный
            "нет", "нет", "нет"
        ]
        mock_load.return_value = [{"id": 1, "state": "CANCELED"}]
        mock_filter.return_value = [{"id": 1, "state": "CANCELED"}]

        main()

        mock_print.assert_any_call('Статус операции "test" недоступен.')
        mock_filter.assert_called_once()
        # Проверяем, что фильтр вызван с правильным статусом
        args, _ = mock_filter.call_args
        assert args[1] == "CANCELED"

    @patch("builtins.print")
    @patch("builtins.input")
    @patch("main.load_transactions")
    @patch("main.filter_by_state")
    @patch("main.sort_by_date")
    def test_sort_by_date_descending(self, mock_sort, mock_filter, mock_load, mock_input, mock_print):
        """Сортировка по убыванию."""
        mock_input.side_effect = [
            "1", "data/valid.json",
            "EXECUTED",
            "да",                # сортировать
            "по убыванию",       # направление
            "нет", "нет"
        ]
        mock_load.return_value = [{"id": 1}]
        mock_filter.return_value = [{"id": 1}]
        # Мокаем функцию сортировки, чтобы вернула список как есть
        mock_sort.return_value = [{"id": 1}]

        main()
        mock_sort.assert_called_once()
        args, kwargs = mock_sort.call_args
        assert kwargs.get("reverse") is True

    @patch("builtins.print")
    @patch("builtins.input")
    @patch("main.load_transactions")
    @patch("main.filter_by_state")
    @patch("main.search_transactions")
    def test_filter_by_word(self, mock_search, mock_filter, mock_load, mock_input, mock_print):
        """Фильтр по слову в описании."""
        mock_input.side_effect = [
            "1", "data/valid.json",
            "EXECUTED",
            "нет", "нет",
            "да",                # поиск по слову
            "перевод"
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
    @patch("main.load_transactions")
    @patch("main.filter_by_state")
    def test_empty_result(self, mock_filter, mock_load, mock_input, mock_print):
        """Пустая выборка после фильтрации -> сообщение."""
        mock_input.side_effect = [
            "1", "data/valid.json",
            "EXECUTED",
            "нет", "нет", "нет"
        ]
        mock_load.return_value = [{"id": 1, "state": "EXECUTED"}]
        mock_filter.return_value = []   # пустой список

        main()
        mock_print.assert_any_call(
            "Не найдено ни одной транзакции, подходящей под ваши условия фильтрации"
        )

    @patch("builtins.print")
    @patch("builtins.input")
    @patch("main.read_csv")
    @patch("main.filter_by_state")
    def test_csv_source(self, mock_filter, mock_read_csv, mock_input, mock_print):
        """Выбор CSV-файла."""
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
    @patch("main.read_xlsx")
    @patch("main.filter_by_state")
    def test_xlsx_source(self, mock_filter, mock_read_xlsx, mock_input, mock_print):
        """Выбор XLSX-файла."""
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
    @patch("main.load_transactions")
    @patch("main.filter_by_state")
    def test_rub_filter(self, mock_filter, mock_load, mock_input, mock_print):
        """Фильтр только рублёвых транзакций."""
        mock_input.side_effect = [
            "1", "data/valid.json",
            "EXECUTED",
            "нет",         # сортировка
            "да",          # только рублёвые
            "нет"          # поиск по слову
        ]
        mock_load.return_value = [
            {"id": 1, "operationAmount": {"currency": {"code": "RUB"}}},
            {"id": 2, "operationAmount": {"currency": {"code": "USD"}}},
        ]
        mock_filter.return_value = mock_load.return_value.copy()

        main()
        # После фильтрации по рублям должно остаться только id 1
        mock_print.assert_any_call("Всего банковских операций в выборке: 1")