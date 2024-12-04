#!/usr/bin/env python3


import sys

from PySide6.QtCore import QLockFile
from PySide6.QtWidgets import QApplication, QMessageBox

from rechess.ui import MainWindow
from rechess.utils import app_object


def main() -> None:
    """Initialize app and lock it to be launched only once."""
    app: QApplication = app_object()
    main_window: MainWindow = MainWindow()
    lock_file: QLockFile = QLockFile("ReChess.lock")

    if not lock_file.tryLock(1):
        QMessageBox.warning(main_window, "Warning", "ReChess is already running.")
        main_window.destruct()
        sys.exit()

    app.exec()


if __name__ == "__main__":
    main()
