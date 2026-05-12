import pytest
import pandas as pd
import tempfile
from pathlib import Path
from src.file_readers import read_csv, read_xlsx


class TestReadCSV:
    def test_valid_csv(self):
        """Чтение корректного CSV-файла (разделитель ;)"""
        data = pd.DataFrame({
            "id": [1, 2],
            "amount": [100.50, 200.75],
            "currency": ["USD", "EUR"]
        })
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as tmp:
            tmp_path = tmp.name
        data.to_csv(tmp_path, sep=';', index=False, encoding='utf-8')
        result = read_csv(tmp_path)
        assert len(result) == 2
        assert result[0] == {"id": "1", "amount": "100.5", "currency": "USD"}
        assert result[1] == {"id": "2", "amount": "200.75", "currency": "EUR"}
        Path(tmp_path).unlink()

    def test_file_not_found(self):
        result = read_csv("nonexistent.csv")
        assert result == []

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            tmp_path = tmp.name
        # Файл пустой
        result = read_csv(tmp_path)
        assert result == []
        Path(tmp_path).unlink()

    def test_only_headers(self):
        data = pd.DataFrame(columns=["id", "amount", "currency"])
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            tmp_path = tmp.name
        data.to_csv(tmp_path, sep=';', index=False, encoding='utf-8')
        result = read_csv(tmp_path)
        assert result == []   # нет строк данных
        Path(tmp_path).unlink()


class TestReadXLSX:
    def test_valid_xlsx(self):
        """Чтение корректного XLSX-файла"""
        data = pd.DataFrame({
            "id": [1, 2],
            "amount": [100.50, 200.75],
            "currency": ["USD", "EUR"]
        })
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            tmp_path = tmp.name
        data.to_excel(tmp_path, index=False, engine='openpyxl')
        result = read_xlsx(tmp_path)
        assert len(result) == 2
        # pandas читает числа как int/float, но мы в функции преобразовали в строки (dtype=str)
        # Проверяем, что значения стали строками (как в CSV)
        assert result[0] == {"id": "1", "amount": "100.5", "currency": "USD"}
        assert result[1] == {"id": "2", "amount": "200.75", "currency": "EUR"}
        Path(tmp_path).unlink()

    def test_file_not_found(self):
        result = read_xlsx("nonexistent.xlsx")
        assert result == []

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            tmp_path = tmp.name
        # Создаём пустой файл (без листов)
        with open(tmp_path, 'wb'):
            pass
        result = read_xlsx(tmp_path)
        assert result == []
        Path(tmp_path).unlink()

    def test_only_headers(self):
        data = pd.DataFrame(columns=["id", "amount", "currency"])
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            tmp_path = tmp.name
        data.to_excel(tmp_path, index=False, engine='openpyxl')
        result = read_xlsx(tmp_path)
        assert result == []
        Path(tmp_path).unlink()


# Опционально: тесты на реальные файлы (если они существуют)
def test_real_csv_file():
    csv_path = "data/transactions.csv"
    if not Path(csv_path).exists():
        pytest.skip("Реальный CSV-файл не найден")
    data = read_csv(csv_path)
    assert len(data) > 0
    assert "id" in data[0]


def test_real_xlsx_file():
    xlsx_path = "data/transactions_excel.xlsx"
    if not Path(xlsx_path).exists():
        pytest.skip("Реальный XLSX-файл не найден")
    data = read_xlsx(xlsx_path)
    assert len(data) > 0
    assert "id" in data[0]