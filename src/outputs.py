import csv
import logging
from datetime import datetime

from prettytable import PrettyTable

from constants import (BASE_DIR, DATETIME_FORMAT,
                       RESULTS_DIR, PRETTY_CASE, FILE_CASE)
from utils import get_dir_path

FILE_SAVED_PHRASE = 'Файл с результатами был сохранён: {file_path}'


def file_output(results, cli_args):
    results_dir = get_dir_path(BASE_DIR, RESULTS_DIR)
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now_formatted = datetime.now().strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect=csv.unix_dialect)
        writer.writerows(results)

    logging.info(FILE_SAVED_PHRASE.format(file_path=file_path))


def default_output(results, *args):
    for row in results:
        print(*row)


def pretty_output(results, *args):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


OUTPUT_TYPES = {
    PRETTY_CASE: pretty_output,
    FILE_CASE: file_output,
    None: default_output
}


def control_output(results, cli_args):
    OUTPUT_TYPES[cli_args.output](results, cli_args)
