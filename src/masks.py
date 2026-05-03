import logging
from pathlib import Path

# Настройка логгера
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

logger = logging.getLogger("masks")
logger.setLevel(logging.INFO)

# Формат для файла и консоли (единый)
formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)-8s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Вывод в файл (перезапись)
file_handler = logging.FileHandler(log_dir / "masks.log", mode='w', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Вывод в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def get_mask_card_number(card_number: str) -> str:
    """
    Маскирует номер банковской карты.
    Формат: XXXX XX** **** XXXX (видно первые 6 и последние 4 цифры, остальное — звёздочки).
    """
    logger.info(f"Маскировка карты: {card_number}")

    # Удаляем пробелы и другие символы, оставляем только цифры
    digits = "".join(filter(str.isdigit, card_number))

    # Проверяем длину номера карты (стандартно 16 цифр)
    if len(digits) != 16:
        raise ValueError("Номер карты должен содержать 16 цифр")

    # Формируем маску: первые 6 цифр + 6 звёздочек + последние 4 цифры
    masked = (
        digits[:6]  # Первые 6 цифр
        + "******"  # 6 звёздочек
        + digits[-4:]  # Последние 4 цифры
    )

    # Разбиваем на блоки по 4 символа с пробелами
    formatted = " ".join(masked[i : i + 4] for i in range(0, 16, 4))

    return formatted


def get_mask_account(account_number: str) -> str:
    """
    Маскирует номер банковского счёта.
    Формат: **XXXX (видно только последние 4 цифры, перед ними — две звёздочки).
    """
    logger.info(f"Маскировка счета: {account_number}")

    # Удаляем пробелы и другие символы, оставляем только цифры
    digits = "".join(filter(str.isdigit, account_number))

    # Проверяем длину номера счёта (стандартно 20 цифр)
    if len(digits) != 20:
        raise ValueError("Номер счёта должен содержать 20 цифр")

    # Заменяем цифры, кроме последних 4, на две звёздочки
    return f'**{digits[-4:]}'
