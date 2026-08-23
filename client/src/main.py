"""Server Monitor — application entry point."""

import sys


def main():
    # allow running both from src/ and as packaged exe
    here = __file__
    import os

    sys.path.insert(0, os.path.dirname(here))

    from PySide6.QtWidgets import QApplication

    import app_log

    app_log.setup_logging()
    app_log.install_excepthook()

    from ui.theme import STYLE_SHEET
    from ui.main_window import MainWindow

    import logging

    log = logging.getLogger("main")

    app = QApplication(sys.argv)
    app.setApplicationName("Server Monitor")
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE_SHEET)

    win = MainWindow()
    log.info("MainWindow constructed")
    win.show()
    log.info("MainWindow shown, entering event loop")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
