from typing import List, Dict, Any, Iterator


def filter_by_currency(
    transactions: List[Dict[str, Any]], currency: str = "USD"
) -> Iterator[Dict[str, Any]]:
    """
    Принимает список транзакций и возвращает итератор,
    который выдает транзакции с указанной валютой (поле operationAmount.currency.code).
    """
    for transaction in transactions:
        try:
            if (
                transaction.get("operationAmount", {}).get("currency", {}).get("code")
                == currency
            ):
                yield transaction
        except AttributeError:
            continue


def transaction_descriptions(transactions: List[Dict[str, Any]]) -> Iterator[str]:
    """
    Принимает список транзакций и возвращает итератор,
    который по очереди выдает описания операций (ключ 'description').
    """
    for transaction in transactions:
        description = transaction.get("description")
        if description is not None:
            yield description


def card_number_generator(start: int, end: int) -> Iterator[str]:
    """
    Генерирует номера банковских карт в заданном диапазоне.

    Номер карты имеет формат XXXX XXXX XXXX XXXX, где X — цифра.
    Диапазон задаётся целыми числами от start до end включительно,
    которые интерпретируются как 16-значные числа с ведущими нулями.
    """
    for number in range(start, end + 1):
        card_str = f"{number:016d}"
        formatted = " ".join(card_str[i : i + 4] for i in range(0, 16, 4))
        yield formatted
