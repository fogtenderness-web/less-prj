"""
Главный модуль программы для работы с банковскими транзакциями.
"""

import sys
from typing import Any, Dict, List

from src.processing import filter_by_state, search_transactions, sort_by_date
from src.readers import read_csv, read_xlsx
from src.utils import load_transactions
from src.widget import get_date, mask_account_card


def main() -> None:
    """Основная логика программы."""
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("Выберите необходимый пункт меню:")
    print("1. Получить информацию о транзакциях из JSON-файла")
    print("2. Получить информацию о транзакциях из CSV-файла")
    print("3. Получить информацию о транзакциях из XLSX-файла")

    choice = input("Ваш выбор: ").strip()
    data: List[Dict[str, Any]] = []

    if choice == "1":
        file_path = input("Введите путь к JSON-файлу: ").strip()
        print("Для обработки выбран JSON-файл.")
        data = load_transactions(file_path)
    elif choice == "2":
        file_path = input("Введите путь к CSV-файлу (разделитель ;): ").strip()
        print("Для обработки выбран CSV-файл.")
        data = read_csv(file_path)
    elif choice == "3":
        file_path = input("Введите путь к XLSX-файлу: ").strip()
        print("Для обработки выбран XLSX-файл.")
        data = read_xlsx(file_path)
    else:
        print("Неверный выбор. Завершение программы.")
        sys.exit(1)

    if not data:
        print("Не удалось загрузить транзакции. Проверьте путь к файлу и его содержимое.")
        return

    print(f"Загружено {len(data)} транзакций.")

    # --- Выбор статуса с проверкой ---
    valid_statuses = {"EXECUTED", "CANCELED", "PENDING"}
    while True:
        print("\nВведите статус, по которому необходимо выполнить фильтрацию.")
        print("Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING")
        status = input("Ваш выбор: ").strip().upper()
        if status in valid_statuses:
            break
        print(f"Статус операции \"{status}\" недоступен.")

    filtered = filter_by_state(data, status)
    print(f"Операции отфильтрованы по статусу \"{status}\"")
    print(f"Найдено {len(filtered)} транзакций.")

    # --- Сортировка по дате ---
    sort_choice = input("\nОтсортировать операции по дате? Да/Нет: ").strip().lower()
    if sort_choice in ["да", "yes", "y", "д"]:
        order = input("Отсортировать по возрастанию или по убыванию? ").strip().lower()
        reverse = order in ["убыванию", "убыв", "desc", "убывание"]
        filtered = sort_by_date(filtered, reverse=reverse)

    # --- Фильтр только рублёвых транзакций ---
    rub_only = input("\nВыводить только рублевые транзакции? Да/Нет: ").strip().lower()
    if rub_only in ["да", "yes", "y", "д"]:
        filtered = [
            tx for tx in filtered
            if tx.get("operationAmount", {}).get("currency", {}).get("code") == "RUB"
        ]

    # --- Фильтр по слову в описании ---
    word_filter = input(
        "\nОтфильтровать список транзакций по определенному слову в описании? Да/Нет: ").strip().lower()
    if word_filter in ["да", "yes", "y", "д"]:
        word = input("Введите слово для поиска: ").strip()
        if word:
            filtered = search_transactions(filtered, word)

    # --- Вывод результата ---
    if not filtered:
        print("\nНе найдено ни одной транзакции, подходящей под ваши условия фильтрации")
        return

    print("\nРаспечатываю итоговый список транзакций...\n")
    print(f"Всего банковских операций в выборке: {len(filtered)}\n")

    for tx in filtered:
        date_str = tx.get("date", "")
        date = get_date(date_str) if date_str else "Дата неизвестна"
        description = tx.get("description", "Описание отсутствует")

        # Сумма и валюта
        operation_amount = tx.get("operationAmount", {})
        amount = operation_amount.get("amount", "0")
        currency = operation_amount.get("currency", {}).get("code", "")
        if currency == "RUB":
            amount_str = f"{amount} руб."
        else:
            amount_str = f"{amount} {currency}"

        # Маскировка счетов/карт
        from_acc = tx.get("from", "")
        to_acc = tx.get("to", "")
        from_masked = mask_account_card(from_acc) if from_acc else "Нет данных"
        to_masked = mask_account_card(to_acc) if to_acc else "Нет данных"

        # Формируем строку перевода (from -> to)
        if from_masked != "Нет данных" and to_masked != "Нет данных":
            transfer_str = f"{from_masked} -> {to_masked}"
        elif from_masked != "Нет данных":
            transfer_str = from_masked
        elif to_masked != "Нет данных":
            transfer_str = to_masked
        else:
            transfer_str = ""

        print(f"{date} {description}")
        if transfer_str:
            print(transfer_str)
        print(f"Сумма: {amount_str}\n")


if __name__ == "__main__":
    main()
