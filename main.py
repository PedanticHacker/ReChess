#!/usr/bin/env python3


from __future__ import annotations

from PySide6.QtCore import QLockFile

from rechess.ui import MainWindow
from rechess.utils import app_object, show_warning


def main() -> None:
    """Initialize app and lock it to be launched only once."""
    app: QApplication = app_object()
    main_window: MainWindow = MainWindow()
    lock_file: QLockFile = QLockFile("ReChess.lock")

    if not lock_file.tryLock(1):
        show_warning(main_window)

    main_window.showMaximized()
    app.exec()


if __name__ == "__main__":
    main()
