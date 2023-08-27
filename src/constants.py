from pathlib import Path

# константы путей
MAIN_DOC_URL = "https://docs.python.org/3/"
MAIN_PEPS_URL = "https://peps.python.org/"
BASE_DIR = Path(__file__).parent
LOGS_DIR = "logs"
LOG_FILE = BASE_DIR / "parser.log"
RESULTS_DIR = "results"

# для логгирования
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = "%d.%m.%Y %H:%M:%S"

# для вывода результата
DATETIME_FORMAT = "%Y-%m-%d_%H-%M-%S"
CHOICES = ("pretty", "file")
DOWNLOADS_DIR = "downloads"

EXPECTED_STATUS = {
    "A": ("Active", "Accepted"),
    "D": ("Deferred",),
    "F": ("Final",),
    "P": ("Provisional",),
    "R": ("Rejected",),
    "S": ("Superseded",),
    "W": ("Withdrawn",),
    "": ("Draft", "Active"),
}
