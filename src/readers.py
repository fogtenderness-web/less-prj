import csv
import logging
from pathlib import Path
from typing import List, Dict, Any
from openpyxl import load_workbook

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
    Читает CSV-файл и возвращает список словарей (каждая строка — dict).
    Первая строка считается заголовком.
    При ошибках возвращает пустой список.
    """
    path = Path(file_path)
    logger.info(f"Чтение CSV: {path}")
    if not path.exists():
        logger.warning(f"Файл не найден: {path}")
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            data = [row for row in reader]
    except Exception as e:
        logger.error(f"Ошибка чтения CSV: {e}")
        return []
    if not data:
        logger.warning("CSV-файл пуст или не содержит данных")
        return []
    logger.info(f"Загружено {len(data)} записей из CSV")
    return data


def read_xlsx(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает XLSX-файл и возвращает список словарей.
    Первая строка листа считается заголовком.
    При ошибках возвращает пустой список.
    """
    path = Path(file_path)
    logger.info(f"Чтение XLSX: {path}")
    if not path.exists():
        logger.warning(f"Файл не найден: {path}")
        return []
    try:
        wb = load_workbook(path, data_only=True)
        sheet = wb.active
        headers = [cell.value for cell in sheet[1] if cell.value is not None]
        if not headers:
            logger.warning("XLSX-файл не содержит заголовков")
            return []
        data = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if not any(row):  # пустая строка
                continue
            row_dict = {headers[i]: row[i] for i in range(len(headers))}
            data.append(row_dict)
    except Exception as e:
        logger.error(f"Ошибка чтения XLSX: {e}")
        return []
    if not data:
        logger.warning("XLSX-файл не содержит данных")
        return []
    logger.info(f"Загружено {len(data)} записей из XLSX")
    return data