from pathlib import Path

# paths
MAIN_DOC_URL = "https://docs.python.org/3/"
MAIN_PEPS_URL = "https://peps.python.org/"
BASE_DIR = Path(__file__).parent
LOGS_DIR = "logs"
LOG_FILE = BASE_DIR / "parser.log"
RESULTS_DIR = "results"

# logging
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = "%d.%m.%Y %H:%M:%S"

# output.py
DATETIME_FORMAT = "%Y-%m-%d_%H-%M-%S"
DOWNLOADS_DIR = "downloads"
PRETTY = "pretty"
FILE = "file"

# pep.py
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
