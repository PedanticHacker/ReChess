#!/usr/bin/env python3


import sys

from PySide6.QtCore import QLockFile
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from rechess.gui import MainWindow
from rechess.utils import get_app_style, get_svg_icon


class AppSession(QApplication):
    """The app's session, locked to be launched only once."""

    def __init__(self) -> None:
        super().__init__()

        self._lock_file: QLockFile = QLockFile("ReChess.lock")

        if self._lock_file.tryLock(1):
            self.setApplicationName("ReChess")
            self.setDesktopFileName("ReChess")
            self.setApplicationVersion("1.0.0")
            self.setWindowIcon(get_svg_icon("logo"))
            self.setStyleSheet(get_app_style("general"))
        else:
            sys.exit()

    def launch(self) -> int:
        """Launch the app's session."""
        return self.exec()


def main() -> int:
    """Define the app's entry point."""
    app_session: AppSession = AppSession()

    main_window: MainWindow = MainWindow()
    main_window.show_maximized()

    return app_session.launch()


if __name__ == "__main__":
    main()
