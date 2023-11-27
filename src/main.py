import logging
import re
from collections import defaultdict
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, DOWNLOADS_DIR, EXPECTED_STATUS, FINISH_TEXT,
                       MAIN_DOC_URL, MISMATCHED_STATUS_TEXT, NOT_FOUND_TEXT,
                       PEP_BASE_URL, STARTUP_TEXT)
from outputs import control_output
from exceptions import TextNotFound
from utils import find_tag, get_dir_path, get_soup

ARCHIVE_SAVED = 'Архив был загружен и сохранён: {archive_path}'
STATUS_ERROR = ('Страница: {0}'
                ' Статус в карточке: {1}'
                ' Ожидаемые статусы: {2}')
ARGS = 'Аргументы командной строки: {args}'
SOUP_ERROR = 'Ошибка: {error} URL: {link}'


def whats_new(session):
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    errors = []
    for a_tag in tqdm(
            get_soup(
                session, urljoin(MAIN_DOC_URL, 'whatsnew/')
            ).select(
                '#what-s-new-in-python div.toctree-wrapper li.toctree-l1 > a'
            )):
        version_link = urljoin(
            urljoin(MAIN_DOC_URL, 'whatsnew/'),
            a_tag['href']
        )
        try:
            soup = get_soup(session, version_link)
        except ConnectionError as error:
            errors.append(SOUP_ERROR.format(
                error=error, link=version_link
            ))
            continue
        results.append(
            (version_link,
             find_tag(soup, 'h1').text,
             find_tag(soup, 'dl').text.replace('\n', ' '))
        )
    list(map(logging.error, errors))
    return results


def latest_versions(session):
    soup = get_soup(session, MAIN_DOC_URL)
    if not soup:
        return
    ul_tags = soup.select('div.sphinxsidebarwrapper ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise TextNotFound(NOT_FOUND_TEXT)
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        text_matched = re.search(pattern, a_tag.text)
        if text_matched:
            version, status = text_matched.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (a_tag['href'], version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    pdf_a4_link = get_soup(session, downloads_url).select_one(
        'table.docutils'
        ' a[href$="pdf-a4.zip"]'
    )['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = get_dir_path(BASE_DIR, DOWNLOADS_DIR)
    downloads_dir.mkdir(exist_ok=True)
    response = session.get(archive_url)
    archive_path = downloads_dir / filename
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(ARCHIVE_SAVED.format(archive_path=archive_path))


def pep(session):
    soup = get_soup(session, PEP_BASE_URL)
    table_tags = soup.select('#index-by-category table.pep-zero-table')
    results = defaultdict(lambda: 0)
    error_statuses = [MISMATCHED_STATUS_TEXT]
    error_connections = []
    for table in tqdm(table_tags):
        tr_tags = table.tbody.find_all('tr')
        for tr in tr_tags:
            page_link = urljoin(PEP_BASE_URL, tr.a['href'])
            try:
                page_soup = get_soup(session, page_link)
            except ConnectionError as error:
                error_connections.append(SOUP_ERROR.format(
                    error=error, link=page_link
                ))
                continue
            page_section_tag = find_tag(page_soup,
                                        'section',
                                        {'id': 'pep-content'})
            actual_status = page_section_tag.find(
                string='Status'
            ).parent.find_next_sibling().string

            preview_status = tr.abbr.text[1:]
            if actual_status not in EXPECTED_STATUS[preview_status]:
                error_statuses.append(
                    STATUS_ERROR.format(
                        page_link,
                        actual_status,
                        EXPECTED_STATUS[preview_status]
                    )
                )
            results[actual_status] += 1
    list(map(logging.error, error_connections))
    list(map(logging.error, error_statuses))
    return [
        ('Статус', 'Количество'),
        *results.items(),
        ('Всего', sum(results.values())),
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(STARTUP_TEXT)
    logging.info(ARGS.format(args=args))

    try:
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()

        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)

        if results is not None:
            control_output(results, args)
        logging.info(FINISH_TEXT)
    except Exception as error:
        logging.error(error)


if __name__ == '__main__':
    main()
