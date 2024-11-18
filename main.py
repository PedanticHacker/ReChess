#!/usr/bin/env python3


import sys

from PySide6.QtCore import QLockFile
from PySide6.QtWidgets import QApplication, QMessageBox, QWidget

from rechess.ui import MainWindow
from rechess.utils import initialize_app


def main() -> None:
    """Initialize app and lock it to be launched only once."""
    lock_file: QLockFile = QLockFile("ReChess.lock")

    if not lock_file.tryLock(1):
        initialize_app()
        QMessageBox.warning(QWidget(), "Warning", "ReChess is already running.")
        sys.exit(1)

    app: QApplication = initialize_app()
    MainWindow()
    app.exec()


if __name__ == "__main__":
    main()
