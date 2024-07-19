#!/usr/bin/env python3


import sys

from PySide6.QtCore import QLockFile
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from rechess.gui import MainWindow
from rechess.utils import app_style, svg_icon


class ReChess(QApplication):
    """ReChess GUI app, locked to be launched only once."""

    def __init__(self) -> None:
        super().__init__()

        self._lock_file: QLockFile = QLockFile("ReChess.lock")

        if self._lock_file.tryLock(1):
            self.setStyle("fusion")
            self.setApplicationName("ReChess")
            self.setDesktopFileName("ReChess")
            self.setApplicationVersion("1.0.0")
            self.setWindowIcon(svg_icon("logo"))
            self.setStyleSheet(app_style("general"))
        else:
            sys.exit()

    def launch(self) -> None:
        """Launch ReChess GUI app."""
        self.exec()


def main() -> None:
    """Define entry point for ReChess GUI app."""
    re_chess: ReChess = ReChess()

    main_window: MainWindow = MainWindow()
    main_window.show_maximized()

    re_chess.launch()


if __name__ == "__main__":
    main()
