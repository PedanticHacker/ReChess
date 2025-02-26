from __future__ import annotations

from chess import svg
from PySide6.QtCore import Property, QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPaintEvent
from PySide6.QtSvg import QSvgRenderer
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
        """Initialize board with game instance."""
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

        self._is_dragging: bool = False
        self._piece_dragged_from_square: int | None = None
        self._dragged_piece: Piece | None = None
        self._dragged_piece_from_current_x_position: float | None = None
        self._dragged_piece_from_current_y_position: float | None = None
        self._square_size: float = 70.0

        self._is_animating: bool = False
        self._animation_timer: QTimer = QTimer(self)
        self._animation_timer.timeout.connect(self._animate_piece_return)
        self._animation_start_position: QPointF | None = None
        self._animation_end_position: QPointF | None = None
        self._animation_current_position: QPointF | None = None
        self._animation_steps: int = 10
        self._animation_current_step: int = 0

        self._board_cache: dict[tuple, bytes] = {}
        self._piece_renderers: dict[str, QSvgRenderer] = {}

        self._game.move_played.connect(self._invalidate_cache)

    def _invalidate_cache(self) -> None:
        self._board_cache.clear()
        self.update()

    def _colors(self) -> dict[str, str]:
        """Return color values for board elements."""
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

    def _get_board_cache_key(self) -> tuple:
        board_fen: str = self._game.board.fen()
        highlights = self._game.legal_moves
        arrows = self._game.arrow
        check: int | None = self._game.king_in_check
        orientation: bool = setting_value("board", "orientation")
        colors = tuple(sorted(self._colors().items()))
        from_square: int | None = (
            self._piece_dragged_from_square
            if self._is_dragging or self._is_animating
            else None
        )
        animation_state: bool = self._is_animating

        return (
            board_fen,
            str(highlights),
            str(arrows),
            check,
            orientation,
            colors,
            from_square,
            animation_state,
        )

    def _get_square_center(self, square_index: int) -> QPointF:
        file: int = square_index % 8
        rank: int = square_index // 8

        if setting_value("board", "orientation"):
            x_position: float = 20.0 + (file * 70.0) + 35.0
            y_position: float = 20.0 + ((7 - rank) * 70.0) + 35.0
        else:
            x_position = 20.0 + ((7 - file) * 70.0) + 35.0
            y_position = 20.0 + (rank * 70.0) + 35.0

        return QPointF(x_position, y_position)

    def _start_return_animation(
        self, current_position: QPointF, target_square: int
    ) -> None:
        assert (
            self._piece_dragged_from_square is not None
        ), "Cannot animate without a source square"

        self._is_animating = True
        self._is_dragging = False
        self._animation_start_position = current_position
        self._animation_end_position = self._get_square_center(
            self._piece_dragged_from_square
        )
        self._animation_current_position = current_position
        self._animation_current_step = 0
        self._animation_timer.start(20)

    def _animate_piece_return(self) -> None:
        if self._animation_current_step >= self._animation_steps:
            self._animation_timer.stop()
            self._is_animating = False
            self._animation_start_position = None
            self._animation_end_position = None
            self._animation_current_position = None
            self._piece_dragged_from_square = None
            self._dragged_piece = None
            self._game.reset_squares()
            self.update()
            return

        self._animation_current_step += 1
        progress: float = self._animation_current_step / self._animation_steps
        progress = 1.0 - (1.0 - progress) * (1.0 - progress)

        if (
            self._animation_start_position is not None
            and self._animation_end_position is not None
        ):
            start_x = self._animation_start_position.x()
            start_y = self._animation_start_position.y()
            end_x = self._animation_end_position.x()
            end_y = self._animation_end_position.y()

            x_distance: float = end_x - start_x
            y_distance: float = end_y - start_y

            self._animation_current_position = QPointF(
                start_x + (x_distance * progress),
                start_y + (y_distance * progress),
            )

            self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press for piece selection."""
        if self._is_animating:
            return

        x_position: float = event.position().x()
        y_position: float = event.position().y()

        file, rank = self._game.locate_file_and_rank(x_position, y_position)
        square_index: int = rank * 8 + file

        if 0 <= square_index < 64:
            piece = self._game.board.piece_at(square_index)

            if piece and piece.color == self._game.board.turn:
                self._is_dragging = True
                self._piece_dragged_from_square = square_index
                self._dragged_piece = piece
                self._dragged_piece_from_current_x_position = x_position
                self._dragged_piece_from_current_y_position = y_position

                self._game.from_square = square_index
                self.update()
                return

        self._game.locate_square(x_position, y_position)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Update dragged piece position."""
        if self._is_animating:
            return

        if self._is_dragging:
            self._dragged_piece_from_current_x_position = event.position().x()
            self._dragged_piece_from_current_y_position = event.position().y()
            self.update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Complete drag operation and attempt move."""
        if self._is_animating:
            return

        if self._is_dragging and self._piece_dragged_from_square is not None:
            x_position: float = event.position().x()
            y_position: float = event.position().y()

            file, rank = self._game.locate_file_and_rank(x_position, y_position)
            target_square: int = rank * 8 + file

            if (
                0 <= target_square < 64
                and target_square != self._piece_dragged_from_square
            ):
                legal_move_targets: list[int] | None = self._game.legal_moves

                if legal_move_targets and target_square in legal_move_targets:
                    self._game.to_square = target_square
                    self._game.find_move(self._piece_dragged_from_square, target_square)

                    self._is_dragging = False
                    self._piece_dragged_from_square = None
                    self._dragged_piece = None
                    self._dragged_piece_from_current_x_position = None
                    self._dragged_piece_from_current_y_position = None

                    self._game.reset_squares()
                    self.update()
                else:
                    current_position: QPointF = QPointF(x_position, y_position)
                    self._start_return_animation(current_position, target_square)
            else:
                current_position = QPointF(x_position, y_position)
                self._start_return_animation(current_position, target_square)
        else:
            super().mouseReleaseEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint board and dragged piece if dragging."""
        cache_key: tuple = self._get_board_cache_key()

        if cache_key not in self._board_cache:
            marked_squares: list[int] | None = self._game.legal_moves

            if (
                self._is_dragging or self._is_animating
            ) and self._piece_dragged_from_square is not None:
                temporary_board = self._game.board.copy()
                temporary_board.set_piece_at(self._piece_dragged_from_square, None)

                svg_board: str = svg.board(
                    arrows=self._game.arrow,
                    board=temporary_board,
                    check=self._game.king_in_check,
                    colors=self._colors(),
                    orientation=setting_value("board", "orientation"),
                    squares=marked_squares,
                )
            else:
                svg_board = svg.board(
                    arrows=self._game.arrow,
                    board=self._game.board,
                    check=self._game.king_in_check,
                    colors=self._colors(),
                    orientation=setting_value("board", "orientation"),
                    squares=marked_squares,
                )

            self._board_cache[cache_key] = svg_board.encode()

            if len(self._board_cache) > 20:
                for old_key in list(self._board_cache.keys())[0:10]:
                    del self._board_cache[old_key]

        self.load(self._board_cache[cache_key])
        super().paintEvent(event)

        if (
            self._is_dragging
            and self._dragged_piece
            and self._dragged_piece_from_current_x_position is not None
            and self._dragged_piece_from_current_y_position is not None
        ):
            painter: QPainter = QPainter(self)

            piece_symbol: str = self._dragged_piece.symbol()
            if piece_symbol not in self._piece_renderers:
                piece_svg: str = svg.piece(self._dragged_piece)
                renderer: QSvgRenderer = QSvgRenderer()
                renderer.load(piece_svg.encode())
                self._piece_renderers[piece_symbol] = renderer

            renderer = self._piece_renderers[piece_symbol]

            offset: float = self._square_size / 2
            x_position: float = self._dragged_piece_from_current_x_position - offset
            y_position: float = self._dragged_piece_from_current_y_position - offset

            renderer.render(
                painter,
                QRectF(x_position, y_position, self._square_size, self._square_size),
            )
            painter.end()
        elif (
            self._is_animating
            and self._dragged_piece
            and self._animation_current_position is not None
        ):
            painter = QPainter(self)

            piece_symbol = self._dragged_piece.symbol()
            if piece_symbol not in self._piece_renderers:
                piece_svg = svg.piece(self._dragged_piece)
                renderer = QSvgRenderer()
                renderer.load(piece_svg.encode())
                self._piece_renderers[piece_symbol] = renderer

            renderer = self._piece_renderers[piece_symbol]

            offset = self._square_size / 2
            x_position = self._animation_current_position.x() - offset
            y_position = self._animation_current_position.y() - offset

            renderer.render(
                painter,
                QRectF(x_position, y_position, self._square_size, self._square_size),
            )
            painter.end()
