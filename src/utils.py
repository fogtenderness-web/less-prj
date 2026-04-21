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