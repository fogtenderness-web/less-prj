import pytest
from src.generators import filter_by_currency, transaction_descriptions, card_number_generator

class TestFilterByCurrency:
    """Тестирование filter_by_currency"""

    def test_filter_usd(self, sample_transactions_for_generators):
        """Корректная фильтрация по USD"""
        usd_gen = filter_by_currency(sample_transactions_for_generators, "USD")
        usd_list = list(usd_gen)
        assert len(usd_list) == 3
        assert all(t["operationAmount"]["currency"]["code"] == "USD" for t in usd_list)
        assert [t["id"] for t in usd_list] == [939719570, 142264268, 615064591]

    def test_filter_eur(self, sample_transactions_for_generators):
        eur_gen = filter_by_currency(sample_transactions_for_generators, "EUR")
        eur_list = list(eur_gen)
        assert len(eur_list) == 1
        assert eur_list[0]["id"] == 873106923

    def test_filter_rub(self, sample_transactions_for_generators):
        rub_gen = filter_by_currency(sample_transactions_for_generators, "RUB")
        rub_list = list(rub_gen)
        assert len(rub_list) == 1
        assert rub_list[0]["id"] == 594226727

    def test_no_matching_currency(self, sample_transactions_for_generators):
        """Валюта отсутствует в транзакциях"""
        gen = filter_by_currency(sample_transactions_for_generators, "GBP")
        assert list(gen) == []

    def test_empty_list(self, empty_transactions):
        gen = filter_by_currency(empty_transactions, "USD")
        assert list(gen) == []

    def test_malformed_transactions(self, transactions_without_currency):
        """Некорректная структура валюты — не вызывают ошибку"""
        gen = filter_by_currency(transactions_without_currency, "USD")
        assert list(gen) == []

    def test_iterator_next(self, sample_transactions_for_generators):
        """Проверка работы итератора через next()"""
        gen = filter_by_currency(sample_transactions_for_generators, "USD")
        assert next(gen)["id"] == 939719570
        assert next(gen)["id"] == 142264268
        assert next(gen)["id"] == 615064591
        with pytest.raises(StopIteration):
            next(gen)

class TestTransactionDescriptions:
    """Тестирование transaction_descriptions"""

    def test_descriptions_list(self, sample_transactions_for_generators):
        """Возвращает описания всех транзакций"""
        gen = transaction_descriptions(sample_transactions_for_generators)
        expected = [
            "Перевод организации",
            "Перевод со счета на счет",
            "Перевод со счета на счет",
            "Перевод организации",
            "Перевод с карты на карту"
        ]
        assert list(gen) == expected

    def test_skip_missing_description(self):
        """Транзакции без описания или с None пропускаются"""
        transactions = [
            {"id": 1, "description": "Есть"},
            {"id": 2},
            {"id": 3, "description": None},
            {"id": 4, "description": "Тоже есть"}
        ]
        gen = transaction_descriptions(transactions)
        assert list(gen) == ["Есть", "Тоже есть"]

    def test_empty_list(self, empty_transactions):
        gen = transaction_descriptions(empty_transactions)
        assert list(gen) == []

    def test_single_transaction(self):
        transactions = [{"id": 1, "description": "Один"}]
        gen = transaction_descriptions(transactions)
        assert list(gen) == ["Один"]

    def test_iterator_next(self, sample_transactions_for_generators):
        gen = transaction_descriptions(sample_transactions_for_generators)
        assert next(gen) == "Перевод организации"
        assert next(gen) == "Перевод со счета на счет"
        assert next(gen) == "Перевод со счета на счет"
        assert next(gen) == "Перевод организации"
        assert next(gen) == "Перевод с карты на карту"
        with pytest.raises(StopIteration):
            next(gen)

class TestCardNumberGenerator:
    """Тестирование card_number_generator"""

    def test_range_1_to_5(self):
        gen = card_number_generator(1, 5)
        expected = [
            "0000 0000 0000 0001", "0000 0000 0000 0002", "0000 0000 0000 0003",
            "0000 0000 0000 0004", "0000 0000 0000 0005"
        ]
        assert list(gen) == expected

    def test_single_number(self):
        gen = card_number_generator(42, 42)
        assert list(gen) == ["0000 0000 0000 0042"]

    def test_max_value(self):
        gen = card_number_generator(9999999999999999, 9999999999999999)
        assert list(gen) == ["9999 9999 9999 9999"]

    def test_zero(self):
        gen = card_number_generator(0, 0)
        assert list(gen) == ["0000 0000 0000 0000"]

    def test_formatting(self):
        gen = card_number_generator(1234567890123456, 1234567890123456)
        assert next(gen) == "1234 5678 9012 3456"

    def test_start_greater_than_end(self):
        gen = card_number_generator(10, 5)
        assert list(gen) == []

    def test_range_leading_zeros(self):
        gen = card_number_generator(1, 3)
        assert list(gen) == [
            "0000 0000 0000 0001",
            "0000 0000 0000 0002",
            "0000 0000 0000 0003"
        ]

    def test_exhaustion(self):
        gen = card_number_generator(1, 1)
        assert next(gen) == "0000 0000 0000 0001"
        with pytest.raises(StopIteration):
            next(gen)