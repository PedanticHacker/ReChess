#!/usr/bin/env python3


import sys

from PySide6.QtCore import QLockFile
from PySide6.QtWidgets import QApplication

from rechess.gui import MainWindow
from rechess.utils import initialize_app


def main() -> None:
    """Initialize app and lock it to be launched only once."""
    lock_file: QLockFile = QLockFile("ReChess.lock")

    if not lock_file.tryLock(1):
        sys.exit()

    app: QApplication = initialize_app()

    main_window: MainWindow = MainWindow()
    main_window.show_maximized()

    app.exec()


# Launch app
if __name__ == "__main__":
    main()
