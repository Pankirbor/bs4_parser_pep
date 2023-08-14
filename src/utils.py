import logging

from requests import RequestException

from exceptions import ParserFindTagException


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = "utf-8"
        return response
    except RequestException:
        logging.exception(
            f"Ошибка ответа на запрос {url}",
            stack_info=True,
        )


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        err_msg = f"Не найден тег {tag} {attrs}"
        logging.exception(err_msg, stack_info=True)
        raise ParserFindTagException(err_msg)

    return searched_tag
