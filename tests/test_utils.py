import pytest
import json
import tempfile
from pathlib import Path
from src.utils import load_transactions

class TestLoadTransactions:
    """Тесты для функции load_transactions"""

    def test_valid_file(self):
        """Корректный файл со списком транзакций"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            data = [{"id": 1, "amount": 100}, {"id": 2, "amount": 200}]
            json.dump(data, tmp)
            tmp_path = tmp.name

        result = load_transactions(tmp_path)
        assert result == data
        Path(tmp_path).unlink()

    def test_file_not_found(self):
        """Несуществующий файл"""
        result = load_transactions("nonexistent.json")
        assert result == []

    def test_empty_file(self):
        """Пустой файл"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp.write("")
            tmp_path = tmp.name

        result = load_transactions(tmp_path)
        assert result == []
        Path(tmp_path).unlink()

    def test_invalid_json(self):
        """Некорректный JSON"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp.write("not a json")
            tmp_path = tmp.name

        result = load_transactions(tmp_path)
        assert result == []
        Path(tmp_path).unlink()

    def test_not_a_list(self):
        """JSON содержит не список (например, словарь)"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            json.dump({"key": "value"}, tmp)
            tmp_path = tmp.name

        result = load_transactions(tmp_path)
        assert result == []
        Path(tmp_path).unlink()

    def test_real_data_file(self):
        """Тест с реальным файлом data/operations.json (если существует)"""
        # Если файл есть в проекте, проверяем, что он читается и возвращает список
        from pathlib import Path
        data_file = Path(__file__).parent.parent / "data" / "operations.json"
        if data_file.exists():
            result = load_transactions(str(data_file))
            assert isinstance(result, list)
            if result:
                assert "id" in result[0]
        else:
            pytest.skip("Файл data/operations.json не найден")