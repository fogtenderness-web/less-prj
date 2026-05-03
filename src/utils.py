import json
from typing import List, Dict, Any
from pathlib import Path

# Настройка логгера
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

logger = logging.getLogger("utils")
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)-8s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

file_handler = logging.FileHandler(log_dir / "utils.log", mode='w', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def load_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает список транзакций из JSON-файла.

    Если файл не существует, пуст, содержит не список или некорректный JSON,
    возвращает пустой список.
    """

    path = Path(file_path)
    logger.info(f"Загрузка: {path}")
    if not path.exists():
        return []

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        logger.error(f"Ошибка чтения: {e}")
        return []

    if not isinstance(data, list):
        logger.warning(f"Не список (тип {type(data).__name__})")
        return []
    logger.info(f"Загружено {len(data)} транзакций")
    return data

def get_transaction_amount_in_rub(transaction: Dict[str, Any]) -> float:
    tx_id = transaction.get("id", "unknown")
    logger.info(f"Обработка транзакции {tx_id}")
    try:
        amount = float(transaction.get("operationAmount", {}).get("amount", 0))
    except (ValueError, TypeError):
        logger.error(f"Некорректная сумма в транзакции {tx_id}")
        amount = 0.0

    currency = transaction.get("operationAmount", {}).get("currency", {}).get("code", "RUB")

    if currency == "RUB":
        logger.info(f"Транзакция {tx_id} в рублях, сумма {amount}")
        return amount
    if currency not in ("USD", "EUR"):
        logger.warning(f"Транзакция {tx_id} имеет неподдерживаемую валюту {currency}")
        return 0.0
    logger.info(f"Конвертация {amount} {currency} для транзакции {tx_id}")

    from src.external_api import convert_currency
    try:
        result = convert_currency(amount, currency, "RUB")
        logger.info(f"Результат конвертации: {result} RUB")
        return result
    except (ValueError, ConnectionError) as e:
        logger.error(f"Ошибка конвертации: {e}")
        raise