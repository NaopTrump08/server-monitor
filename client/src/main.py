"""Server Monitor — application entry point (liquid-glass client)."""

import os
import sys


def main():
    # allow running both from src/ and as packaged exe
    here = __file__
    sys.path.insert(0, os.path.dirname(here))

    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication

    import app_log

    app_log.setup_logging()
    app_log.install_excepthook()

    from ui.main_window import MainWindow

    import logging

    log = logging.getLogger("main")

    app = QApplication(sys.argv)
    app.setApplicationName("Server Monitor")

    exe_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(here)
    meipass = getattr(sys, "_MEIPASS", "")
    icon_paths = [
        os.path.join(exe_dir, "resources", "icon.ico"),
        os.path.join(exe_dir, "resources", "icon.png"),
        os.path.join(meipass, "resources", "icon.ico"),
        os.path.join(meipass, "resources", "icon.png"),
        os.path.join(os.path.dirname(here), "..", "resources", "icon.ico"),
        os.path.join(os.path.dirname(here), "resources", "icon.ico"),
    ]
    for p in icon_paths:
        if os.path.exists(p):
            app.setWindowIcon(QIcon(p))
            break

    app.setStyle("Fusion")

    win = MainWindow()
    win.show()
    log.info("MainWindow shown, entering event loop")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
