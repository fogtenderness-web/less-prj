from typing import List, Dict, Any, Iterator


def filter_by_currency(transactions: List[Dict[str, Any]], currency: str = "USD") -> Iterator[Dict[str, Any]]:
    """
    Принимает список транзакций и возвращает итератор,
    который выдает транзакции с указанной валютой (поле operationAmount.currency.code).
    """
    for transaction in transactions:
        # Извлекаем код валюты из структуры operationAmount.currency.code
        try:
            if transaction.get("operationAmount", {}).get("currency", {}).get("code") == currency:
                yield transaction
        except AttributeError:
            # Если структура не соответствует ожидаемой, пропускаем транзакцию
            continue