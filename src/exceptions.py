class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass


class TextNotFound(Exception):
    """Вызывается, когда подстрока не была найдена в строке."""
    pass
