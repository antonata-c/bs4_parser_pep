from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import ParserFindTagException

RESPONSE_ERROR_PHRASE = ('Возникла ошибка при загрузке страницы {url}'
                         'Ошибка: {error}')

TAG_NOT_FOUND_PHRASE = 'Не найден тег {tag} {attrs}'


def get_response(session, url, encoding='utf-8'):
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException as error:
        raise ConnectionError(RESPONSE_ERROR_PHRASE.format(url=url,
                                                           error=error))


def get_soup(session, url):
    response = get_response(session, url)
    if response is None:
        return
    return BeautifulSoup(response.text, 'lxml')


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        raise ParserFindTagException(TAG_NOT_FOUND_PHRASE.format(
            tag=tag, attrs=attrs
        ))
    return searched_tag


def get_dir_path(base, directory):
    return base / directory
