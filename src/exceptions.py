class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""

    pass


class VersionsNotFound(Exception):
    """Не найден список с версиями Python"""

    pass
