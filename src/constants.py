from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_BASE_URL = 'https://peps.python.org/'

BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'parser.log'
DOWNLOADS_DIR = 'downloads'
RESULTS_DIR = 'results'

STARTUP_TEXT = 'Парсер запущен!'
FINISH_TEXT = 'Парсер завершил работу.'
MISMATCHED_STATUS_TEXT = 'Ошибка в статусах:'
NOT_FOUND_TEXT = 'Ничего не нашлось'

PRETTY_CASE = 'pretty'
FILE_CASE = 'file'

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
