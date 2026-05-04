"""
conftest.py - централизованное хранилище фикстур для тестирования модулей:
- masks.py
- widget.py
- processing.py
-generators.py
"""

import pytest

# ========================
# processing.py
# ========================


@pytest.fixture
def transactions():
    """Список транзакций для тестирования"""
    return [
        {"id": 1, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
        {"id": 2, "state": "PENDING", "date": "2018-06-30T02:08:58.425572"},
        {"id": 3, "state": "EXECUTED", "date": "2019-04-04T23:20:05.206878"},
        {"id": 4, "state": "CANCELED", "date": "2020-01-15T10:15:30.123456"},
        {"id": 5, "state": "EXECUTED", "date": "2021-02-20T14:30:45.678901"},
    ]


@pytest.fixture
def empty_list():
    return []


@pytest.fixture
def no_state_list():
    """Список без ключа state"""
    return [
        {"id": 1, "date": "2019-07-03T18:35:29.512364"},
        {"id": 2, "date": "2018-06-30T02:08:58.425572"},
    ]


# ========================
# masks.py
# ========================


@pytest.fixture
def card_numbers():
    """Валидные номера карт (вход -> результат)"""
    return [
        ("1234 5678 9012 3456", "1234 56** **** 3456"),
        ("1234567890123456", "1234 56** **** 3456"),
        ("1234-5678-9012-3456", "1234 56** **** 3456"),
    ]


@pytest.fixture
def account_numbers():
    """Валидные номера счетов (вход -> результат)"""
    return [
        ("1234 5678 9012 3456 7890", "**7890"),
        ("12345678901234567890", "**7890"),
    ]


# ========================
# widget.py
# ========================


@pytest.fixture
def card_data():
    """Тестовые данные для карт"""
    return [
        ("Visa 1234567812345678", "Visa 1234 56** **** 5678"),
        ("MasterCard 1234567812345678", "MasterCard 1234 56** **** 5678"),
        ("Maestro 1234567812345678", "Maestro 1234 56** **** 5678"),
        ("Мир 1234567812345678", "Мир 1234 56** **** 5678"),
    ]


@pytest.fixture
def account_data():
    """Тестовые данные для счетов"""
    return [
        ("Счет 12345678901234567890", "Счет **7890"),
        ("Account 12345678901234567890", "Account **7890"),
    ]


@pytest.fixture
def invalid_data():
    """Некорректные данные (вход, сообщение об ошибке)"""
    return [
        ("Visa 123456789012345", "Номер карты должен содержать 16 цифр"),
        ("Счет 1234567890123456789", "Номер счёта должен содержать 20 цифр"),
        ("Visa Счет 1234567812345678", "неоднозначный ввод"),
        ("Unknown 1234567812345678", "Не удалось определить тип"),
        ("Visa Platinum", "не найден номер"),
    ]


@pytest.fixture
def dates():
    """Тестовые даты (вход -> результат)"""
    return [
        ("2019-07-03T18:35:29.512364", "03.07.2019"),
        ("2021-02-20T14:30:45", "20.02.2021"),
        ("2023-12-25T10:00:00", "25.12.2023"),
    ]


# ========================
# generators.py
# ========================


@pytest.fixture
def sample_transactions_for_generators():
    """Список транзакций для тестирования filter_by_currency и transaction_descriptions"""
    return [
        {
            "id": 939719570,
            "description": "Перевод организации",
            "operationAmount": {"amount": "9824.07", "currency": {"code": "USD"}},
        },
        {
            "id": 142264268,
            "description": "Перевод со счета на счет",
            "operationAmount": {"amount": "79114.93", "currency": {"code": "USD"}},
        },
        {
            "id": 873106923,
            "description": "Перевод со счета на счет",
            "operationAmount": {"amount": "43318.34", "currency": {"code": "EUR"}},
        },
        {
            "id": 594226727,
            "description": "Перевод организации",
            "operationAmount": {"amount": "67314.70", "currency": {"code": "RUB"}},
        },
        {
            "id": 615064591,
            "description": "Перевод с карты на карту",
            "operationAmount": {"amount": "77751.04", "currency": {"code": "USD"}},
        },
    ]


@pytest.fixture
def empty_transactions():
    return []


@pytest.fixture
def transactions_without_currency():
    """Транзакции с некорректной структурой валюты"""
    return [
        {"id": 1, "description": "Нет валюты", "operationAmount": {"amount": "100"}},
        {"id": 2, "description": "Нет operationAmount"},
        {"id": 3, "operationAmount": {"currency": "USD"}},
    ]


@pytest.fixture
def temp_log_file():
    """Создаёт временный файл для логов и удаляет после теста"""
    import tempfile

    fd, path = tempfile.mkstemp(suffix=".log")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)
