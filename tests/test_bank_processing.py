import pytest
from src.masks import get_mask_card_number, get_mask_account
from src.widget import mask_account_card, get_date
from src.processing import filter_by_state, sort_by_date


# ========================
# Тесты для processing.py
# ========================

class TestProcessing:
    """Тесты фильтрации и сортировки транзакций"""

    def test_filter_by_state_executed(self, transactions):
        """Фильтрация транзакций со статусом EXECUTED"""
        result = filter_by_state(transactions)
        assert len(result) == 3
        assert all(item["state"] == "EXECUTED" for item in result)
        assert [item["id"] for item in result] == [1, 3, 5]

    def test_filter_by_state_pending(self, transactions):
        """Фильтрация транзакций со статусом PENDING"""
        result = filter_by_state(transactions, state="PENDING")
        assert len(result) == 1
        assert result[0]["id"] == 2
        assert result[0]["state"] == "PENDING"

    def test_filter_by_state_canceled(self, transactions):
        """Фильтрация транзакций со статусом CANCELED"""
        result = filter_by_state(transactions, state="CANCELED")
        assert len(result) == 1
        assert result[0]["id"] == 4
        assert result[0]["state"] == "CANCELED"

    def test_filter_by_state_unknown(self, transactions):
        """Фильтрация по несуществующему статусу возвращает пустой список"""
        result = filter_by_state(transactions, state="UNKNOWN")
        assert result == []

    def test_filter_empty_list(self, empty_list):
        """Фильтрация пустого списка"""
        result = filter_by_state(empty_list)
        assert result == []

    def test_filter_no_state_key(self, no_state_list):
        """Элементы без ключа state не попадают в результат"""
        result = filter_by_state(no_state_list)
        assert result == []

    def test_sort_by_date_descending(self, transactions):
        """Сортировка по дате по убыванию (от новых к старым)"""
        result = sort_by_date(transactions)
        dates = [item["date"] for item in result]
        assert dates == [
            "2021-02-20T14:30:45.678901",
            "2020-01-15T10:15:30.123456",
            "2019-07-03T18:35:29.512364",
            "2019-04-04T23:20:05.206878",
            "2018-06-30T02:08:58.425572",
        ]

    def test_sort_by_date_ascending(self, transactions):
        """Сортировка по дате по возрастанию (от старых к новым)"""
        result = sort_by_date(transactions, reverse=False)
        dates = [item["date"] for item in result]
        assert dates == [
            "2018-06-30T02:08:58.425572",
            "2019-04-04T23:20:05.206878",
            "2019-07-03T18:35:29.512364",
            "2020-01-15T10:15:30.123456",
            "2021-02-20T14:30:45.678901",
        ]

    def test_sort_empty_list(self, empty_list):
        """Сортировка пустого списка"""
        result = sort_by_date(empty_list)
        assert result == []


# ========================
# Тесты для masks.py
# ========================

class TestMasks:
    """Тесты маскировки номеров карт и счетов"""

    @pytest.mark.parametrize("card_input, expected", [
        ("1234 5678 9012 3456", "1234 56** **** 3456"),
        ("1234567890123456", "1234 56** **** 3456"),
        ("1234-5678-9012-3456", "1234 56** **** 3456"),
    ])
    def test_get_mask_card_number_valid(self, card_input, expected):
        """Тест маскировки валидных номеров карт"""
        assert get_mask_card_number(card_input) == expected

    def test_get_mask_card_number_invalid_length(self):
        """Ошибка при некорректной длине номера карты"""
        with pytest.raises(ValueError, match="Номер карты должен содержать 16 цифр"):
            get_mask_card_number("123456789012345")

    @pytest.mark.parametrize("account_input, expected", [
        ("1234 5678 9012 3456 7890", "**7890"),
        ("12345678901234567890", "**7890"),
    ])
    def test_get_mask_account_valid(self, account_input, expected):
        """Тест маскировки валидных номеров счетов"""
        assert get_mask_account(account_input) == expected

    def test_get_mask_account_invalid_length(self):
        """Ошибка при некорректной длине номера счета"""
        with pytest.raises(ValueError, match="Номер счёта должен содержать 20 цифр"):
            get_mask_account("1234567890123456789")


# ========================
# Тесты для widget.py
# ========================

class TestWidget:
    """Тесты расширенных функций виджета"""

    @pytest.mark.parametrize("card_input, expected", [
        ("Visa 1234567812345678", "Visa 1234 56** **** 5678"),
        ("MasterCard 1234567812345678", "MasterCard 1234 56** **** 5678"),
        ("Maestro 1234567812345678", "Maestro 1234 56** **** 5678"),
        ("Мир 1234567812345678", "Мир 1234 56** **** 5678"),
    ])
    def test_mask_account_card_card(self, card_input, expected):
        """Тест маскировки карт с автоматическим определением типа"""
        assert mask_account_card(card_input) == expected

    @pytest.mark.parametrize("account_input, expected", [
        ("Счет 12345678901234567890", "Счет **7890"),
        ("Account 12345678901234567890", "Account **7890"),
    ])
    def test_mask_account_card_account(self, account_input, expected):
        """Тест маскировки счетов с автоматическим определением типа"""
        assert mask_account_card(account_input) == expected

    @pytest.mark.parametrize("invalid_input, error_msg", [
        ("Visa 123456789012345", "Номер карты должен содержать 16 цифр"),
        ("Счет 1234567890123456789", "Номер счёта должен содержать 20 цифр"),
        ("Visa Счет 1234567812345678", "неоднозначный ввод"),
        ("Unknown 1234567812345678", "Не удалось определить тип"),
        ("Visa Platinum", "не найден номер"),
    ])
    def test_mask_account_card_invalid(self, invalid_input, error_msg):
        """Тест обработки некорректных входных данных"""
        with pytest.raises(ValueError, match=error_msg):
            mask_account_card(invalid_input)

    @pytest.mark.parametrize("date_input, expected", [
        ("2019-07-03T18:35:29.512364", "03.07.2019"),
        ("2021-02-20T14:30:45", "20.02.2021"),
        ("2023-12-25T10:00:00", "25.12.2023"),
    ])
    def test_get_date_valid(self, date_input, expected):
        """Тест преобразования валидных дат"""
        assert get_date(date_input) == expected

    def test_get_date_invalid(self):
        """Ошибка при некорректном формате даты"""
        with pytest.raises(ValueError):
            get_date("03.07.2019")


# ========================
# Тесты для покрытия дополнительных ветвей кода
# ========================

class TestEdgeCases:
    """Тесты граничных случаев"""

    def test_filter_by_state_with_none(self):
        """Фильтрация списка с None значениями"""
        data = [
            {"id": 1, "state": None, "date": "2019-07-03"},
            {"id": 2, "state": "EXECUTED", "date": "2020-01-01"},
        ]
        result = filter_by_state(data)
        assert len(result) == 1
        assert result[0]["id"] == 2

    def test_sort_by_date_equal_dates(self):
        """Сортировка с одинаковыми датами"""
        data = [
            {"id": 1, "date": "2020-01-01T12:00:00"},
            {"id": 2, "date": "2020-01-01T12:00:00"},
            {"id": 3, "date": "2019-01-01T12:00:00"},
        ]
        result = sort_by_date(data)
        assert len(result) == 3
        # Первые два элемента имеют одинаковую дату
        assert result[0]["date"] == "2020-01-01T12:00:00"
        assert result[1]["date"] == "2020-01-01T12:00:00"
        assert result[2]["date"] == "2019-01-01T12:00:00"

    def test_mask_card_with_lowercase(self):
        """Маскировка карты в нижнем регистре"""
        result = mask_account_card("maestro 1234567812345678")
        assert result == "maestro 1234 56** **** 5678"

    def test_mask_card_with_extra_text(self):
        """Маскировка карты с дополнительным текстом"""
        result = mask_account_card("Visa Platinum Premium 1234567812345678")
        assert result == "Visa Platinum Premium 1234 56** **** 5678"

    def test_mask_account_with_lowercase(self):
        """Маскировка счета в нижнем регистре"""
        result = mask_account_card("счет 12345678901234567890")
        assert result == "счет **7890"

    def test_get_card_number_with_non_digits(self):
        """Номер карты с нецифровыми символами"""
        result = get_mask_card_number("12a34 56b78 90c12 34d56")
        assert result == "1234 56** **** 3456"