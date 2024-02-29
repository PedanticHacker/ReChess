#!/usr/bin/env python3.12


import sys

from PySide6.QtGui import QIcon
from PySide6.QtCore import QLockFile
from PySide6.QtWidgets import QApplication

from rechess.gui import MainWindow
from rechess import get_app_style, get_svg_icon


APP_NAME: str = "ReChess"
APP_VERSION: str = "1.0.0"
LOCK_FILE_NAME: str = "ReChess.lock"
LOGO_ICON: QIcon = get_svg_icon("logo")
GENERAL_STYLE: str = get_app_style("general")


class App(QApplication):
    """The app's session, locked to be launched only once."""

    def __init__(self) -> None:
        super().__init__()

        self.lock_file: QLockFile = QLockFile(LOCK_FILE_NAME)

        if self.lock_file.tryLock(1):
            self.setWindowIcon(LOGO_ICON)
            self.setStyleSheet(GENERAL_STYLE)
            self.setApplicationName(APP_NAME)
            self.setDesktopFileName(APP_NAME)
            self.setApplicationVersion(APP_VERSION)
        else:
            sys.exit()

    def launch(self) -> int:
        """Launch the app's session."""
        return self.exec()


def main() -> int:
    """Define the application entry point."""
    app: App = App()

    main_window: MainWindow = MainWindow()
    main_window.show_maximized()

    return app.launch()


if __name__ == "__main__":
    main()
