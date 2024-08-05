from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton


def _create_button(icon_name: str) -> QPushButton:
    """Create button from `icon_name`."""
    button = QPushButton(_svg_icon(icon_name), icon_name)
    button.setIconSize(QSize(56, 56))
    return button


def _svg_icon(file_name: str) -> QIcon:
    """Return SVG icon from `file_name`."""
    return QIcon(f"rechess/resources/icons/{file_name}.svg")


LOGO_ICON: QIcon = _svg_icon("logo")

BLACK_BISHOP_BUTTON: QPushButton = _create_button("black-bishop")
BLACK_KNIGHT_BUTTON: QPushButton = _create_button("black-knight")
BLACK_QUEEN_BUTTON: QPushButton = _create_button("black-queen")
BLACK_ROOK_BUTTON: QPushButton = _create_button("black-rook")
WHITE_BISHOP_BUTTON: QPushButton = _create_button("white-bishop")
WHITE_KNIGHT_BUTTON: QPushButton = _create_button("white-knight")
WHITE_QUEEN_BUTTON: QPushButton = _create_button("white-queen")
WHITE_ROOK_BUTTON: QPushButton = _create_button("white-rook")
