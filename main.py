#!/usr/bin/env python3


from __future__ import annotations

from PySide6.QtCore import QLockFile, QTimer

from rechess.ui import MainWindow
from rechess.utils import create_app, create_splash_screen, initialize, show_warning


def main() -> None:
    """Launch app with splash screen, lock it to launch only once."""
    app: QApplication = create_app()
    main_window: MainWindow = MainWindow()
    lock_file: QLockFile = QLockFile("ReChess.lock")
    splash_screen: QSplashScreen = create_splash_screen()

    if not lock_file.tryLock(1):
        splash_screen.close()
        show_warning(main_window)
        return

    QTimer.singleShot(3000, lambda: initialize(splash_screen, main_window))

    app.exec()


if __name__ == "__main__":
    main()
