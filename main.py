#!/usr/bin/env python3


from __future__ import annotations

from platform import system

from PySide6.QtCore import QLockFile, QTimer

from rechess.ui import MainWindow
from rechess.utils import create_app, create_splash_screen, show_warning


def _initialize(main_window: MainWindow, splash_screen: QSplashScreen) -> None:
    main_window.showMaximized()
    splash_screen.finish(main_window)


def main() -> None:
    """Launch app with splash screen, lock it to launch only once."""
    is_macos: bool = system() == "Darwin"

    app: QApplication = create_app()
    splash_screen: QSplashScreen = create_splash_screen()

    main_window: MainWindow = MainWindow()
    lock_file: QLockFile = QLockFile("ReChess.lock")

    if not lock_file.tryLock(1):
        splash_screen.close()
        show_warning(main_window)
        return

    if is_macos:
        splash_screen.close()
        main_window.showMaximized()
    else:
        QTimer.singleShot(3000, lambda: _initialize(main_window, splash_screen))

    app.exec()


if __name__ == "__main__":
    main()
