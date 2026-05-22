import re
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


def search_transactions(transactions: List[Dict[str, Any]], search_string: str) -> List[Dict[str, Any]]:
    """
    Выполняет поиск транзакций по описанию с использованием регулярного выражения.

    Поиск регистронезависимый. Если строка поиска содержит специальные символы регулярных выражений,
    они экранируются с помощью re.escape, чтобы искать буквальное вхождение.
    """
    if not search_string:
        return []
    pattern = re.compile(re.escape(search_string), re.IGNORECASE)
    result = []
    for tx in transactions:
        description = tx.get("description")
        if description and pattern.search(description):
            result.append(tx)
    return result


def count_operations_by_category(
        transactions: List[Dict[str, Any]], categories: List[str]
) -> Dict[str, int]:
    """
    Подсчитывает количество транзакций, относящихся к каждой категории.

    Категория определяется по вхождению строки категории (без учёта регистра)
    в поле 'description'. Если в описании есть несколько категорий, транзакция
    будет засчитана для каждой из них (мультиклассификация).
    """
    result = {category: 0 for category in categories}
    if not transactions or not categories:
        return result

    for tx in transactions:
        description = tx.get("description")
        if not description:
            continue
        desc_lower = description.lower()
        for category in categories:
            if category.lower() in desc_lower:
                result[category] += 1
    return result
