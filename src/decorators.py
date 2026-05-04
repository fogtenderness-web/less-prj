import functools
from typing import Optional, Any, Callable
import traceback


def log(filename: Optional[str] = None) -> Callable:
    """
    Декоратор для логирования вызовов функций.
    Логирует начало и конец выполнения, результат или ошибку.
    Если указан filename, логи пишутся в файл, иначе в консоль.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Формируем строку с именем функции и аргументами
            args_repr = ", ".join(repr(a) for a in args)
            kwargs_repr = ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items())
            all_args = ", ".join(filter(None, [args_repr, kwargs_repr]))
            func_name = func.__name__
            start_msg = f"Вызов функции {func_name} с аргументами ({all_args})"

            # Логируем начало
            if filename:
                with open(filename, "a", encoding="utf-8") as f:
                    f.write(start_msg + "\n")
            else:
                print(start_msg)

            try:
                result = func(*args, **kwargs)
                end_msg = f"Функция {func_name} завершилась успешно. Результат: {repr(result)}"
                if filename:
                    with open(filename, "a", encoding="utf-8") as f:
                        f.write(end_msg + "\n")
                else:
                    print(end_msg)
                return result
            except Exception as e:
                error_msg = f"Функция {func_name} завершилась ошибкой {type(e).__name__}. Входные параметры: ({all_args})"
                if filename:
                    with open(filename, "a", encoding="utf-8") as f:
                        f.write(error_msg + "\n")
                else:
                    print(error_msg)
                raise  # пробрасываем исключение дальше

        return wrapper

    return decorator
