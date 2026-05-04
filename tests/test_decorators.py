import pytest
import os
import tempfile
from src.decorators import log


# Вспомогательные функции для тестирования
@log()
def success_func(a, b):
    return a + b


@log()
def error_func(x, y):
    raise ValueError("Test error")


@log(filename="test_log.txt")
def success_with_file(a, b):
    return a * b


@log(filename="test_log.txt")
def error_with_file(x):
    raise RuntimeError("Something wrong")


class TestLogDecorator:
    """Тестирование декоратора log"""

    def test_log_to_console_success(self, capsys):
        """Успешный вызов – логи в консоль"""
        result = success_func(3, 5)
        captured = capsys.readouterr()
        assert result == 8
        assert "Вызов функции success_func с аргументами (3, 5)" in captured.out
        assert "Функция success_func завершилась успешно. Результат: 8" in captured.out

    def test_log_to_console_error(self, capsys):
        """Ошибочный вызов – логи в консоль с информацией об ошибке"""
        with pytest.raises(ValueError, match="Test error"):
            error_func(10, 20)
        captured = capsys.readouterr()
        assert "Вызов функции error_func с аргументами (10, 20)" in captured.out
        assert (
            "Функция error_func завершилась ошибкой ValueError. Входные параметры: (10, 20)"
            in captured.out
        )

    def test_log_to_file_success(self):
        """Успешный вызов – логи в файл"""
        test_file = "test_log.txt"
        # Удаляем файл перед тестом, если существует
        if os.path.exists(test_file):
            os.remove(test_file)

        result = success_with_file(4, 3)
        assert result == 12

        # Проверяем содержимое файла
        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Вызов функции success_with_file с аргументами (4, 3)" in content
        assert "Функция success_with_file завершилась успешно. Результат: 12" in content

        # Очистка
        os.remove(test_file)

    def test_log_to_file_error(self):
        """Ошибочный вызов – логи ошибки в файл"""
        test_file = "test_log.txt"
        if os.path.exists(test_file):
            os.remove(test_file)

        with pytest.raises(RuntimeError, match="Something wrong"):
            error_with_file(42)

        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Вызов функции error_with_file с аргументами (42)" in content
        assert (
            "Функция error_with_file завершилась ошибкой RuntimeError. Входные параметры: (42)"
            in content
        )

        os.remove(test_file)

    def test_multiple_calls_to_same_file(self):
        """Несколько вызовов – логи дописываются в файл"""
        test_file = "test_log_multi.txt"
        if os.path.exists(test_file):
            os.remove(test_file)

        @log(filename=test_file)
        def add(x, y):
            return x + y

        add(1, 2)
        add(3, 4)

        with open(test_file, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        assert len(lines) == 4  # 2 вызова * 2 строки (начало + конец)
        assert "Вызов функции add с аргументами (1, 2)" in lines[0]
        assert "Результат: 3" in lines[1]
        assert "Вызов функции add с аргументами (3, 4)" in lines[2]
        assert "Результат: 7" in lines[3]

        os.remove(test_file)

    def test_args_and_kwargs(self, capsys):
        """Передача именованных аргументов"""

        @log()
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        result = greet("Alice", greeting="Hi")
        assert result == "Hi, Alice!"
        captured = capsys.readouterr()
        assert (
            "Вызов функции greet с аргументами ('Alice', greeting='Hi')" in captured.out
        )
        assert "Результат: 'Hi, Alice!'" in captured.out

    def test_no_filename_and_exception_raised(self, capsys):
        """Исключение пробрасывается, логирование ошибки в консоль"""

        @log()
        def divide(a, b):
            return a / b

        with pytest.raises(ZeroDivisionError):
            divide(5, 0)
        captured = capsys.readouterr()
        assert "Вызов функции divide с аргументами (5, 0)" in captured.out
        assert (
            "Функция divide завершилась ошибкой ZeroDivisionError. Входные параметры: (5, 0)"
            in captured.out
        )
