#!/usr/bin/env python3


from __future__ import annotations

from PySide6.QtCore import QLockFile

from rechess.ui import MainWindow
from rechess.utils import create_app, create_splash_screen, show_warning


def main() -> None:
    """Initialize app and lock it to be launched only once."""
    app: QApplication = create_app()
    splash_screen: QSplashScreen = create_splash_screen()

    main_window: MainWindow = MainWindow()
    lock_file: QLockFile = QLockFile("ReChess.lock")

    if not lock_file.tryLock(1):
        splash_screen.close()
        show_warning(main_window)

    main_window.showMaximized()
    splash_screen.finish(main_window)

    app.exec()


if __name__ == "__main__":
    main()
