import logging
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

# Настройка логгера
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

logger = logging.getLogger("file_readers")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)-8s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler = logging.FileHandler(log_dir / "file_readers.log", mode='w', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def read_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает CSV-файл и возвращает список словарей.
    Пустые ячейки заменяются на None. При любых
    ошибках (отсутствие файла, пустой файл, некорректный CSV) возвращается
    пустой список, а ошибка логируется.
    """
    path = Path(file_path)
    logger.info(f"Чтение CSV: {path}")
    if not path.exists():
        logger.warning(f"Файл не найден: {path}")
        return []
    try:
        df = pd.read_csv(path, delimiter=';', encoding='utf-8', dtype=str)
    except Exception as e:
        logger.error(f"Ошибка чтения CSV: {e}")
        return []
    if df.empty:
        logger.warning("CSV-файл пуст или не содержит данных")
        return []
    # Замена NaN на None (для JSON-совместимости)
    df = df.where(pd.notnull(df), None)
    data = df.to_dict(orient='records')
    logger.info(f"Загружено {len(data)} записей из CSV")
    return data


def read_xlsx(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает XLSX-файл и возвращает список словарей.
    Пустые ячейки преобразуются в None. При любых
    ошибках (файл не найден, пустой файл, повреждённый Excel) возвращается
    пустой список, ошибка логируется.
    """
    path = Path(file_path)
    logger.info(f"Чтение XLSX: {path}")
    if not path.exists():
        logger.warning(f"Файл не найден: {path}")
        return []
    try:
        df = pd.read_excel(path, engine='openpyxl', dtype=str)
    except Exception as e:
        logger.error(f"Ошибка чтения XLSX: {e}")
        return []
    if df.empty:
        logger.warning("XLSX-файл пуст или не содержит данных")
        return []
    # Замена NaN на None
    df = df.where(pd.notnull(df), None)
    data = df.to_dict(orient='records')
    logger.info(f"Загружено {len(data)} записей из XLSX")
    return data