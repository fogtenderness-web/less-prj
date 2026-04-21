import json
from typing import List, Dict, Any
from pathlib import Path

def load_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает список транзакций из JSON-файла.

    Если файл не существует, пуст, содержит не список или некорректный JSON,
    возвращает пустой список.
    """
    path = Path(file_path)

    if not path.exists():
        return []

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

    if not isinstance(data, list):
        return []

    return data

def get_transaction_amount_in_rub(transaction: Dict[str, Any]) -> float:
    try:
        amount = float(transaction.get("operationAmount", {}).get("amount", 0))
    except (ValueError, TypeError):
        amount = 0.0

    currency = transaction.get("operationAmount", {}).get("currency", {}).get("code", "RUB")

    if currency == "RUB":
        return amount
    if currency not in ("USD", "EUR"):
        return 0.0

    from src.external_api import convert_currency
    return convert_currency(amount, currency, "RUB")