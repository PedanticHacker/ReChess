#!/usr/bin/env python3


from __future__ import annotations

from PySide6.QtCore import QLockFile, QTimer

from rechess.ui import MainWindow
from rechess.utils import create_app, create_splash_screen, show_warning


def _initialize(splash_screen: QSplashScreen, main_window: MainWindow) -> None:
    main_window.showMaximized()
    splash_screen.finish(main_window)


def main() -> None:
    """Launch app with splash screen, lock it to launch only once."""
    app: QApplication = create_app()
    splash_screen: QSplashScreen = create_splash_screen()

    main_window: MainWindow = MainWindow()
    lock_file: QLockFile = QLockFile("ReChess.lock")

    if not lock_file.tryLock(1):
        splash_screen.close()
        show_warning(main_window)
        return

    QTimer.singleShot(3000, lambda: _initialize(splash_screen, main_window))

    app.exec()


if __name__ == "__main__":
    main()
