import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (
    BASE_DIR,
    DATETIME_FORMAT,
    RESULTS_DIR,
    PRETTY,
    FILE,
)


def control_output(results, cli_args):
    """Функция определения способа вывода результатов работы парсера."""

    output = cli_args.output
    if output == PRETTY:
        pretty_output(results)

    elif output == FILE:
        file_output(results, cli_args)

    else:
        default_output(results)


def default_output(results):
    """Функция вывода результатов в терминал построчно."""
    for row in results:
        print(*row)


def pretty_output(results):
    """Функция вывода результатов в виде таблицы в терминал."""

    table = PrettyTable()
    table.field_names = results[0]
    table.align = "l"
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    """Функция записи информации в файл с сохранением в папку results."""

    result_dir = BASE_DIR / RESULTS_DIR
    result_dir.mkdir(exist_ok=True)

    parse_mod = cli_args.mode
    now = dt.datetime.now()
    data_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f"{parse_mod}_{data_formatted}.csv"
    file_path = result_dir / file_name

    with open(file_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f, dialect="unix")
        writer.writerows(results)

    logging.info(f"Файл с результатами был сохранён: {file_path}")
