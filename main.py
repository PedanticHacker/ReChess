#!/usr/bin/env python3


from PySide6.QtWidgets import QApplication

from rechess.gui import MainWindow
from rechess.utils import prepare_app


def main() -> None:
    """Prepare and launch ReChess GUI app."""
    app: QApplication = prepare_app()

    main_window: MainWindow = MainWindow()
    main_window.show_maximized()

    app.exec()


if __name__ == "__main__":
    main()
