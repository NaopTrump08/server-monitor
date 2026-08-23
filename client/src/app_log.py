"""Application-wide logging helper.

Writes logs to the user config directory so issues on end-user machines
can be diagnosed. Also installs a global excepthook that records any
uncaught exception (including exceptions swallowed by Qt slots).
"""

import logging
import os
import sys
import traceback

from config import config_dir

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
_FILENAME = "app.log"


def log_path():
    return os.path.join(config_dir(), _FILENAME)


def setup_logging(level=logging.INFO):
    try:
        d = config_dir()
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, _FILENAME)
    except OSError:
        path = os.path.join(os.path.expanduser("~"), _FILENAME)

    root = logging.getLogger()
    root.setLevel(level)

    fh = logging.FileHandler(path, encoding="utf-8")
    fh.setFormatter(logging.Formatter(LOG_FORMAT))
    root.addHandler(fh)

    sh = logging.StreamHandler(sys.stderr)
    sh.setFormatter(logging.Formatter(LOG_FORMAT))
    root.addHandler(sh)

    root.info("=== ServerMonitor started (log file: %s) ===", path)
    return path


def install_excepthook():
    def hook(exc_type, exc_value, exc_tb):
        logging.getLogger("excepthook").critical(
            "Uncaught exception:\n%s", "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        )
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)

    sys.excepthook = hook
