from datetime import datetime
import re

def get_date(date_string: str) -> str:
    """
    Преобразует строку с датой в формат ДД.ММ.ГГГГ.
    """
    date_obj = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f")
    return date_obj.strftime("%d.%m.%Y")


def mask_account_card(input_string: str) -> str:
    """
    Маскирует номер банковской карты или счёта в зависимости от типа.

    Для карт используется формат: XXXX XX** **** XXXX
    Для счетов используется формат: **XXXX (последние 4 цифры)
    """
    # Извлекаем все цифры из строки
    digits = ''.join(re.findall(r'\d', input_string))

    # Определяем тип по ключевым словам (без учёта регистра)
    input_lower = input_string.lower()

    is_card = any(
        keyword in input_lower
        for keyword in ['visa', 'mastercard', 'maestro', 'mir']
    )
    is_account = 'счёт' in input_lower or 'account' in input_lower

    # Проверяем, что распознан ровно один тип
    if not (is_card or is_account):
        raise ValueError("Не удалось определить тип: карта или счёт")
    if is_card and is_account:
        raise ValueError("Строка содержит признаки и карты, и счёта — неоднозначный ввод")

    # Выделяем часть строки до номера (тип продукта)
    number_start = re.search(r'\d', input_string)
    if number_start is None:
        raise ValueError("В строке не найден номер (цифры)")
    product_type = input_string[:number_start.start()].rstrip()

    # Применяем соответствующую логику маскировки
    if is_card:
        if len(digits) != 16:
            raise ValueError("Номер карты должен содержать 16 цифр")
        masked = digits[:6] + '******' + digits[-4:]
        masked_number = ' '.join(masked[i:i+4] for i in range(0, 16, 4))
    else:  # is_account
        if len(digits) != 20:
            raise ValueError("Номер счёта должен содержать 20 цифр")
        masked_number = f'**{digits[-4:]}'

    return f"{product_type} {masked_number}"
