import logging
from pathlib import Path
from typing import Any, Dict, List, cast

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
    data = df.to_dict(orient='records')
    for row in data:
        for k, v in list(row.items()):
            if pd.isna(v):
                row[k] = None
    # Приводим ключи к строкам
    data = [{str(k): v for k, v in row.items()} for row in data]
    logger.info(f"Загружено {len(data)} записей из CSV")
    return cast(List[Dict[str, Any]], data)


def read_xlsx(file_path: str) -> List[Dict[str, Any]]:
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
    data = df.to_dict(orient='records')
    for row in data:
        for k, v in list(row.items()):
            if pd.isna(v):
                row[k] = None
    data = [{str(k): v for k, v in row.items()} for row in data]
    logger.info(f"Загружено {len(data)} записей из XLSX")
    return cast(List[Dict[str, Any]], data)
