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
from exceptions import ParserFindTagException
from outputs import control_output, file_output
from utils import find_tag, get_dir_path, get_soup

ARCHIVE_SAVED_PHRASE = 'Архив был загружен и сохранён: {archive_path}'
STATUS_ERROR_PHRASE = ('\nСтраница: {0}'
                       '\nСтатус в карточке: {1}'
                       '\nОжидаемые статусы: {2}')
ARGS_PHRASE = 'Аргументы командной строки: {args}'


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')

    soup = get_soup(session, whats_new_url)

    sections_by_python = soup.select(
        '#what-s-new-in-python div.toctree-wrapper li.toctree-l1'
    )

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        version_link = urljoin(whats_new_url, version_a_tag['href'])
        soup = get_soup(session, version_link)
        results.append(
            (version_link,
             find_tag(soup, 'h1').text,
             find_tag(soup, 'dl').text.replace('\n', ' '))
        )

    return results


def latest_versions(session):
    soup = get_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise LookupError(NOT_FOUND_TEXT)

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
    soup = get_soup(session, downloads_url)

    pdf_a4_link = soup.select_one('table.docutils'
                                  ' a[href$="pdf-a4.zip"]')['href']

    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]

    downloads_dir = get_dir_path(BASE_DIR, DOWNLOADS_DIR)
    downloads_dir.mkdir(exist_ok=True)

    response = session.get(archive_url)
    archive_path = downloads_dir / filename

    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(ARCHIVE_SAVED_PHRASE.format(archive_path=archive_path))


def pep(session):
    soup = get_soup(session, PEP_BASE_URL)

    section_tag = find_tag(soup, 'section', {
        'id': 'index-by-category'})
    table_tags = section_tag.find_all('table', {'class': 'pep-zero-table'})

    results = defaultdict(lambda: 0)
    error_statuses = []

    for table in tqdm(table_tags):
        tr_tags = table.tbody.find_all('tr')
        for tr in tr_tags:
            page_link = urljoin(PEP_BASE_URL, tr.a['href'])
            page_soup = get_soup(session, page_link)
            page_section_tag = find_tag(page_soup,
                                        'section',
                                        {'id': 'pep-content'})
            actual_status = page_section_tag.find(
                string='Status'
            ).parent.find_next_sibling().string

            preview_status = tr.abbr.text[1:]
            if actual_status not in EXPECTED_STATUS[preview_status]:
                error_statuses.append(
                    (page_link, actual_status, EXPECTED_STATUS[preview_status])
                )

            results[actual_status] += 1
    if error_statuses:
        logging.error(MISMATCHED_STATUS_TEXT)
        for error in error_statuses:
            logging.error(STATUS_ERROR_PHRASE.format(*error))
    return [
        ('Статус', 'Количество'),
        *results.items(),
        ('Total', sum(results.values())),
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info(STARTUP_TEXT)

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(ARGS_PHRASE.format(args=args))

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    try:
        results = MODE_TO_FUNCTION[parser_mode](session)

        if parser_mode == 'pep':
            file_output(results, args)
        elif results is not None:
            control_output(results, args)
        logging.info(FINISH_TEXT)
    except (LookupError, ParserFindTagException, ConnectionError) as error:
        logging.error(error)


if __name__ == '__main__':
    main()
