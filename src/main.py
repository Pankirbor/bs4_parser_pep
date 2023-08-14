import re
import logging
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL
from outputs import control_output
from utils import get_response, find_tag


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, "whatsnew/")

    response = get_response(session, whats_new_url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, "lxml")

    # * поиск тега section с нужным id, получим список всех статей
    main_div = find_tag(soup, "section", attrs={"id": "what-s-new-in-python"})

    # Шаг 2-й: поиск внутри main_div следующего тега div с классом toctree-wrapper.
    # Здесь тоже нужен только первый элемент, используется метод find().
    div_with_ul = find_tag(main_div, "div", attrs={"class": "toctree-wrapper"})

    # Шаг 3-й: поиск внутри div_with_ul всех элементов списка li с классом toctree-l1.
    # Нужны все теги, поэтому используется метод find_all().
    sections_by_python = div_with_ul.find_all("li", attrs={"class": "toctree-l1"})

    results = [("Ссылка на статью", "Заголовок", "Редактор, автор")]
    # Печать первого найденного элемента.
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, "a")
        href = version_a_tag["href"]
        version_link = urljoin(whats_new_url, href)

        response_version = get_response(session, version_link)
        if response_version is None:
            continue

        # Загрузите все страницы со статьями. Используйте кеширующую сессию.
        soup_version = BeautifulSoup(response_version.text, "lxml")  # Сварите "супчик".
        h1 = find_tag(soup_version, "h1")  # Найдите в "супе" тег h1.
        dl2 = find_tag(soup_version, "dl")  # Найдите в "супе" тег dl.
        name_author = dl2.text.replace("\n", " ")
        results.append((version_link, h1.text, name_author))

    # # Печать списка с данными.
    # for row in results:
    #     # Распаковка каждого кортежа при печати при помощи звездочки.
    #     print(*row)
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return

    soup = BeautifulSoup(response.text, "lxml")
    sidebar = find_tag(soup, "div", attrs={"class": "sphinxsidebarwrapper"})
    ul_tags = sidebar.find_all("ul")
    for ul in ul_tags:
        # Проверка, есть ли искомый текст в содержимом тега.
        if "All versions" in ul.text:
            # Если текст найден, ищутся все теги <a> в этом списке.
            a_tags = ul.find_all("a")
            # Остановка перебора списков.
            break
    # Если нужный список не нашёлся,
    # вызывается исключение и выполнение программы прерывается.
    else:
        raise Exception("Ничего не нашлось")

    pattern = r"Python (?P<version>\d\.\d+) \((?P<status>.*)\)"
    result = [("Ссылка на документацию", "Версия", "Статус")]
    for a_tag in a_tags:
        link = a_tag["href"]
        comp = re.search(pattern, a_tag.text)
        if comp:
            version, status = comp.groups()
        else:
            version, status = a_tag.text, ""
        result.append((link, version, status))

    # for row in result:
    #     print(*row)
    return result


def download(session):
    # Вместо константы DOWNLOADS_URL, используйте переменную downloads_url.
    downloads_url = urljoin(MAIN_DOC_URL, "download.html")

    response = get_response(session, downloads_url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, "lxml")
    table = find_tag(soup, "table")
    pdf_a4_tag = find_tag(table, "a", {"href": re.compile(r".+pdf-a4\.zip$")})

    archive_url = urljoin(downloads_url, pdf_a4_tag["href"])
    filename = archive_url.split("/")[-1]

    downloads_dir = BASE_DIR / "downloads"

    # Создайте директорию.
    downloads_dir.mkdir(exist_ok=True)

    # Получите путь до архива, объединив имя файла с директорией.
    archive_path = downloads_dir / filename
    # Загрузка архива по ссылке.
    response_dowanload = get_response(session, archive_url)
    if response_dowanload is None:
        return

    # В бинарном режиме открывается файл на запись по указанному пути.
    with open(archive_path, "wb") as file:
        # Полученный ответ записывается в файл.
        file.write(response_dowanload.content)

    logging.info(f"Архив был загружен и сохранён: {archive_path}")


MODE_TO_FUNCTION = {
    "whats-new": whats_new,
    "latest-versions": latest_versions,
    "download": download,
}


def main():
    # * Запускаем функцию с конфигурацией логов.
    configure_logging()

    logging.info("Парсер запущен!")
    # Конфигурация парсера аргументов командной строки —
    # передача в функцию допустимых вариантов выбора.
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    # Считывание аргументов из командной строки.
    args = arg_parser.parse_args()

    logging.info(f"Аргументы командной строки: {args}")

    session = requests_cache.CachedSession()

    # Если был передан ключ '--clear-cache', то args.clear_cache == True.
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    # Поиск и вызов нужной функции по ключу словаря.
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        # передаём их в функцию вывода вместе с аргументами командной строки.
        control_output(results, args)

    logging.info("Парсер завершил работу.")


if __name__ == "__main__":
    main()
