from __future__ import annotations

from chess import svg
from PySide6.QtCore import Property
from PySide6.QtGui import QColor, QMouseEvent, QPaintEvent
from PySide6.QtSvgWidgets import QSvgWidget

from rechess.utils import setting_value


svg.XX = "<circle id='xx' r='4.5' cx='22.5' cy='22.5' stroke='#303030' fill='#e5e5e5'/>"


class Board(QSvgWidget):
    """SVG-based board with interactive pieces."""

    coord: Property = Property(
        QColor,
        lambda self: self._coord,
        lambda self, color: setattr(self, "_coord", color),
    )
    inner_border: Property = Property(
        QColor,
        lambda self: self._inner_border,
        lambda self, color: setattr(self, "_inner_border", color),
    )
    margin: Property = Property(
        QColor,
        lambda self: self._margin,
        lambda self, color: setattr(self, "_margin", color),
    )
    outer_border: Property = Property(
        QColor,
        lambda self: self._outer_border,
        lambda self, color: setattr(self, "_outer_border", color),
    )
    square_dark: Property = Property(
        QColor,
        lambda self: self._square_dark,
        lambda self, color: setattr(self, "_square_dark", color),
    )
    square_dark_lastmove: Property = Property(
        QColor,
        lambda self: self._square_dark_lastmove,
        lambda self, color: setattr(self, "_square_dark_lastmove", color),
    )
    square_light: Property = Property(
        QColor,
        lambda self: self._square_light,
        lambda self, color: setattr(self, "_square_light", color),
    )
    square_light_lastmove: Property = Property(
        QColor,
        lambda self: self._square_light_lastmove,
        lambda self, color: setattr(self, "_square_light_lastmove", color),
    )

    def __init__(self, game: Game) -> None:
        super().__init__()

        self._game: Game = game

        self._coord: QColor = QColor()
        self._inner_border: QColor = QColor()
        self._margin: QColor = QColor()
        self._outer_border: QColor = QColor()
        self._square_dark: QColor = QColor()
        self._square_dark_lastmove: QColor = QColor()
        self._square_light: QColor = QColor()
        self._square_light_lastmove: QColor = QColor()

    def _colors(self) -> dict[str, str]:
        """Return dictionary with color values for board elements."""
        return {
            "coord": self._coord.name(),
            "inner border": self._inner_border.name(),
            "margin": self._margin.name(),
            "outer border": self._outer_border.name(),
            "square dark": self._square_dark.name(),
            "square dark lastmove": self._square_dark_lastmove.name(),
            "square light": self._square_light.name(),
            "square light lastmove": self._square_light_lastmove.name(),
        }

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Locate square on mouse button press."""
        x: float = event.position().x()
        y: float = event.position().y()
        self._game.locate_square(x, y)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint current state of board."""
        svg_board = svg.board(
            arrows=self._game.arrows,
            board=self._game.board,
            check=self._game.king_in_check,
            colors=self._colors(),
            orientation=setting_value("board", "orientation"),
            squares=self._game.legal_moves,
        )
        self.load(svg_board.encode())

        super().paintEvent(event)
