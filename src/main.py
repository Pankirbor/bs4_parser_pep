import re
import logging
from collections import defaultdict
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, DOWNLOADS_DIR, MAIN_DOC_URL, MAIN_PEPS_URL
from exceptions import VersionsNotFound
from outputs import control_output
from utils import get_response, get_soup, find_tag, status_mismatch


def whats_new(session):
    """Функция для парсинга страницы документации
    с последними обновлениями."""

    whats_new_url = urljoin(MAIN_DOC_URL, "whatsnew/")

    soup = get_soup(session, whats_new_url)
    if soup is None:
        return

    main_div = find_tag(soup, "section", attrs={"id": "what-s-new-in-python"})
    div_with_ul = find_tag(main_div, "div", attrs={"class": "toctree-wrapper"})
    sections_by_python = div_with_ul.find_all(
        "li",
        attrs={"class": "toctree-l1"},
    )

    results = [
        ("Ссылка на статью", "Заголовок", "Редактор, Автор"),
    ]

    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, "a")
        href = version_a_tag["href"]
        version_link = urljoin(whats_new_url, href)

        soup_version = get_soup(session, version_link)
        if soup_version is None:
            continue

        h1 = find_tag(soup_version, "h1")
        dl2 = find_tag(soup_version, "dl")
        name_author = dl2.text.replace("\n", " ")
        results.append((version_link, h1.text, name_author))

    return results


def latest_versions(session):
    """Функция для получения таблицы с ссылками на
    все доступные документации Python.
    """
    soup = get_soup(session, MAIN_DOC_URL)
    if soup is None:
        return

    sidebar = find_tag(soup, "div", attrs={"class": "sphinxsidebarwrapper"})
    ul_tags = sidebar.find_all("ul")
    for ul in ul_tags:
        if "All versions" in ul.text:
            a_tags = ul.find_all("a")
            break

    else:
        err_msg = "Список версий Python на странице не найден."
        logging.exception(err_msg, stack_info=True)
        raise VersionsNotFound(err_msg)

    pattern = r"Python (?P<version>\d\.\d+) \((?P<status>.*)\)"
    result = [
        ("Ссылка на документацию", "Версия", "Статус"),
    ]
    for a_tag in a_tags:
        link = a_tag["href"]
        comp = re.search(pattern, a_tag.text)
        if comp:
            version, status = comp.groups()
        else:
            version, status = a_tag.text, ""
        result.append((link, version, status))

    return result


def download(session):
    """Функция для загрузки файла с документацией Python."""

    downloads_url = urljoin(MAIN_DOC_URL, "download.html")

    soup = get_soup(session, downloads_url)
    if soup is None:
        return

    table = find_tag(soup, "table")
    pdf_a4_tag = find_tag(table, "a", {"href": re.compile(r".+pdf-a4\.zip$")})

    archive_url = urljoin(downloads_url, pdf_a4_tag["href"])
    filename = archive_url.split("/")[-1]

    download_dir = BASE_DIR / DOWNLOADS_DIR
    download_dir.mkdir(exist_ok=True)
    archive_path = download_dir / filename

    response_dowanload = get_response(session, archive_url)
    if response_dowanload is None:
        return

    with open(archive_path, "wb") as file:
        file.write(response_dowanload.content)

    logging.info(f"Архив был загружен и сохранён: {archive_path}")


def pep(session):
    """Функция парсинга всех разделов PEP для подсчета
    общего количества документов и различных статусов."""

    soup = get_soup(session, MAIN_PEPS_URL)
    if soup is None:
        return

    table_index = find_tag(soup, "section", {"id": "numerical-index"})

    table_body = find_tag(table_index, "tbody")
    table_rows = table_body.find_all("tr")
    rows_status = [find_tag(row, "abbr").text[1:] for row in table_rows]
    peps_href = [find_tag(row, "a")["href"] for row in table_rows]

    counts_per_status = defaultdict(int)

    for status, href in zip(rows_status, peps_href):
        link_pep = urljoin(MAIN_PEPS_URL, href)

        soup_card = get_soup(session, link_pep)
        if soup_card is None:
            logging.info(f"Ссылка на {link_pep} вернула None")
            continue

        pep_card = find_tag(soup_card, "dl")

        status_row_sibling = pep_card.select('dt:-soup-contains("Status")')[0]
        status_current_card = status_row_sibling.find_next_sibling("dd").text

        # проверяем соответствие статусов
        status_mismatch(status_current_card, status, link_pep)

        counts_per_status[status_current_card] += 1

    result = [("Status", "Count")] + list(counts_per_status.items())
    result.append(("Total", sum(counts_per_status.values())))
    return result


MODE_TO_FUNCTION = {
    "whats-new": whats_new,
    "latest-versions": latest_versions,
    "download": download,
    "pep": pep,
}


def main():
    """Основная функция для работы с парсером в различных режимах."""
    configure_logging()

    logging.info("Парсер запущен!")
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()

    logging.info(f"Аргументы командной строки: {args}")

    session = requests_cache.CachedSession()

    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)

    logging.info("Парсер завершил работу.")


if __name__ == "__main__":
    main()
