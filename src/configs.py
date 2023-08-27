import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import BASE_DIR, DT_FORMAT, LOGS_DIR, LOG_FORMAT, CHOICES, LOG_FILE


def configure_argument_parser(available_modes):
    """Конфигуратор для парсинга аргуметнов командной строки."""

    parser = argparse.ArgumentParser(description="Парсер документации Python")
    parser.add_argument(
        "mode",
        choices=available_modes,
        help="Режимы работы парсера",
    )
    parser.add_argument(
        "-c",
        "--clear-cache",
        action="store_true",
        help="Очистка кеша",
    )
    parser.add_argument(
        "-o",
        "--output",
        choices=CHOICES,
        help="Дополнительные способы вывода данных",
    )
    return parser


def configure_logging():
    """Функция конфигурации логгирования."""

    log_dir = BASE_DIR / LOGS_DIR
    log_dir.mkdir(exist_ok=True)

    rotating_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10**6,
        backupCount=5,
    )

    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler()),
    )
