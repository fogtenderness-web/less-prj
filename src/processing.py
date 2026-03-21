from datetime import datetime
from typing import Any, Dict, List


def filter_by_state(
    data: List[Dict[str, Any]], state: str = "EXECUTED"
) -> List[Dict[str, Any]]:
    """
    Фильтрует список словарей по значению ключа 'state'.

    Параметры:
        data: список словарей для фильтрации (каждый может содержать ключ 'state').
        state: значение для фильтрации (по умолчанию 'EXECUTED').

    Возвращает:
        Новый список словарей, где 'state' совпадает с указанным значением.
    """
    return [item for item in data if item.get("state") == state]


def sort_by_date(
    data: List[Dict[str, Any]], reverse: bool = True
) -> List[Dict[str, Any]]:
    """
    Сортирует список словарей по дате (ключ 'date') в указанном порядке.

    Даты должны быть в формате ISO 8601 (например, '2019-07-03T18:35:29.512364').

    Параметры:
        data: список словарей с ключом 'date' в формате ISO 8601.
        reverse: порядок сортировки (True — убывание, от новых к старым; False — возрастание).

    Возвращает:
        Новый отсортированный список словарей.
    """

    def parse_date(date_str: str) -> datetime:
        return datetime.fromisoformat(date_str)

    return sorted(data, key=lambda item: parse_date(item["date"]), reverse=reverse)
