import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT


def control_output(results, cli_args):
    output = cli_args.output
    if output == "pretty":
        # Вывод в формате PrettyTable.
        pretty_output(results)

    elif output == "file":
        file_output(results, cli_args)

    else:
        # Вывод по умолчанию.
        default_output(results)


def default_output(results):
    # Печатаем список results построчно.
    for row in results:
        print(*row)


def pretty_output(results):
    # Инициализируем объект PrettyTable.
    table = PrettyTable()
    # В качестве заголовков устанавливаем первый элемент списка.
    table.field_names = results[0]
    # Выравниваем всю таблицу по левому краю.
    table.align = "l"
    # Добавляем все строки, начиная со второй (с индексом 1).
    table.add_rows(results[1:])
    # Печатаем таблицу.
    print(table)


def file_output(results, cli_args):
    # Сформируйте путь до директории results.
    results_dir = BASE_DIR / "results"
    # Создайте директорию.
    results_dir.mkdir(exist_ok=True)

    parse_mod = cli_args.mode
    now = dt.datetime.now()
    data_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f"{parse_mod}_{data_formatted}.csv"
    file_path = results_dir / file_name

    with open(file_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f, dialect="unix")
        writer.writerows(results)

    logging.info(f"Файл с результатами был сохранён: {file_path}")
