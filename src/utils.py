import logging
from requests import RequestException

from bs4 import BeautifulSoup

from constants import EXPECTED_STATUS
from exceptions import ParserFindTagException, RequestSendError


def get_response(session, url):
    """Функция отправки запроса и обработки исключений."""

    try:
        response = session.get(url)
        response.encoding = "utf-8"

        return response

    except RequestException:
        raise RequestSendError(f"Ошибка ответа на запрос {url}")


def get_soup(session, url):
    """Функция получения результатов работы BeautifulSoup."""
    response = get_response(session, url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, "lxml")
    return soup


def find_tag(soup, tag, attrs=None):
    """Функция поиска тега и обработки исключений."""

    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        err_msg = f"Не найден тег {tag} {attrs}"
        logging.exception(err_msg, stack_info=True)
        raise ParserFindTagException(err_msg)

    return searched_tag


def status_mismatch(status_current_card, status):
    """Функция для вывявления различий в статусах."""

    if status_current_card not in EXPECTED_STATUS[status]:
        return True

    return False
