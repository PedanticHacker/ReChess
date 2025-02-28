from __future__ import annotations

from functools import lru_cache
from typing import Final

from chess import svg
from PySide6.QtCore import Property, QPointF, QRectF, QTimer
from PySide6.QtGui import QColor, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QSvgWidget

from rechess.utils import setting_value


ANIMATION_TIME: Final[int] = 20
BOARD_MARGIN: Final[float] = 20.0
HALF_SQUARE: Final[float] = 35.0
SQUARE_CENTER_OFFSET: Final[float] = 55.0
SQUARE_SIZE: Final[float] = 70.0

svg.XX = "<circle id='xx' r='4.5' cx='22.5' cy='22.5' stroke='#303030' fill='#e5e5e5'/>"


class SvgBoard(QSvgWidget):
    """Render SVG-based interface for pieces and squares."""

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
        self._game.move_played.connect(self._clear_cache)

        self._square_size: float = SQUARE_SIZE
        self._initialize_colors()

        self._initialize_drag_state()
        self._initialize_animation()

        self._piece_renderers: dict[str, QSvgRenderer] = {}

    def _initialize_colors(self) -> None:
        """Initialize default colors for board."""
        self._coord: QColor = QColor()
        self._inner_border: QColor = QColor()
        self._margin: QColor = QColor()
        self._outer_border: QColor = QColor()
        self._square_dark: QColor = QColor()
        self._square_dark_lastmove: QColor = QColor()
        self._square_light: QColor = QColor()
        self._square_light_lastmove: QColor = QColor()

    def _initialize_drag_state(self) -> None:
        """Initialize initial state for drag operations."""
        self._is_dragging: bool = False
        self._piece_dragged_from_square: int | None = None
        self._dragged_piece: Piece | None = None
        self._drag_position_x: float | None = None
        self._drag_position_y: float | None = None

    def _initialize_animation(self) -> None:
        """Initialize animation system for piece movement."""
        self._is_animating: bool = False
        self._animation_timer: QTimer = QTimer(self)
        self._animation_timer.timeout.connect(self._animate_piece_return)
        self._animation_start_position: QPointF | None = None
        self._animation_end_position: QPointF | None = None
        self._current_animation_position: QPointF | None = None
        self._animation_steps: int = 10
        self._current_animation_step: int = 0

    def _clear_cache(self) -> None:
        """Clear board SVG cache and update display."""
        self._board_svg.cache_clear()
        self.update()

    def _color_dict(self) -> dict[str, str]:
        """Return dictionary of board colors for SVG rendering."""
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

    def _cache_key(self) -> tuple:
        """Create unique key for caching board SVG."""
        dragging_square: int | None = (
            self._piece_dragged_from_square
            if (self._is_dragging or self._is_animating)
            else None
        )

        return (
            self._game.board.fen(),
            str(self._game.legal_moves),
            str(self._game.arrow),
            self._game.king_in_check,
            setting_value("board", "orientation"),
            tuple(sorted(self._color_dict().items())),
            dragging_square,
            self._is_animating,
        )

    def _square_center(self, square: int) -> QPointF:
        """Calculate center point of board square."""
        file: int = square % 8
        rank: int = square // 8
        flipped_file: int = 7 - file
        flipped_rank: int = 7 - rank
        orientation: bool = setting_value("board", "orientation")

        if orientation:
            x_position: float = SQUARE_CENTER_OFFSET + (SQUARE_SIZE * file)
            y_position: float = SQUARE_CENTER_OFFSET + (SQUARE_SIZE * flipped_rank)
        else:
            x_position = SQUARE_CENTER_OFFSET + (SQUARE_SIZE * flipped_file)
            y_position = SQUARE_CENTER_OFFSET + (SQUARE_SIZE * rank)

        return QPointF(x_position, y_position)

    def _start_animation(self, current_position: QPointF) -> None:
        """Begin animation from current position to origin square."""
        if not self._piece_dragged_from_square:
            return

        self._is_animating = True
        self._is_dragging = False
        self._animation_start_position = current_position
        self._animation_end_position = self._square_center(
            self._piece_dragged_from_square
        )
        self._current_animation_position = current_position
        self._current_animation_step = 0
        self._animation_timer.start(ANIMATION_TIME)

    def _animate_piece_return(self) -> None:
        """Update piece position for each step of return animation."""
        if self._current_animation_step >= self._animation_steps:
            self._end_animation()
            return

        self._current_animation_step += 1
        progress: float = self._current_animation_step / self._animation_steps
        progress = 1.0 - (1.0 - progress) * (1.0 - progress)

        if self._animation_start_position and self._animation_end_position:
            start_position: QPointF = self._animation_start_position
            end_position: QPointF = self._animation_end_position
            self._current_animation_position = QPointF(
                start_position.x() * (1 - progress) + end_position.x() * progress,
                start_position.y() * (1 - progress) + end_position.y() * progress,
            )
            self.update()

    def _end_animation(self) -> None:
        """Clean up after animation completion."""
        self._animation_timer.stop()
        self._is_animating = False
        self._animation_start_position = None
        self._animation_end_position = None
        self._current_animation_position = None
        self._piece_dragged_from_square = None
        self._dragged_piece = None
        self._game.reset_squares()
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events for piece selection."""
        if self._is_animating:
            return

        x_position: float = event.position().x()
        y_position: float = event.position().y()

        square_position: tuple[int, int] = self._game.locate_file_and_rank(
            x_position, y_position
        )
        file, rank = square_position
        square_index: int = rank * 8 + file

        if 0 <= square_index < 64:
            piece: Piece | None = self._game.board.piece_at(square_index)
            if piece and piece.color == self._game.board.turn:
                self._start_dragging(square_index, piece, x_position, y_position)
                return

        self._game.locate_square(x_position, y_position)

    def _start_dragging(
        self, square: int, piece: Piece, x_position: float, y_position: float
    ) -> None:
        """Initialize drag operation for piece."""
        self._is_dragging = True
        self._piece_dragged_from_square = square
        self._dragged_piece = piece
        self._drag_position_x = x_position
        self._drag_position_y = y_position
        self._game.from_square = square
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse movement for piece dragging."""
        if self._is_animating:
            return

        if self._is_dragging:
            self._drag_position_x = event.position().x()
            self._drag_position_y = event.position().y()
            self.update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release events for piece placement."""
        if self._is_animating:
            return

        if not self._is_dragging or self._piece_dragged_from_square is None:
            super().mouseReleaseEvent(event)
            return

        x_position: float = event.position().x()
        y_position: float = event.position().y()

        square_position: tuple[int, int] = self._game.locate_file_and_rank(
            x_position, y_position
        )
        file, rank = square_position
        target_square: int = rank * 8 + file

        if self._is_valid_move(target_square):
            self._make_move(target_square)
        else:
            self._cancel_move(x_position, y_position)

    def _is_valid_move(self, target_square: int) -> bool:
        """Check if `target_square` is valid destination for move."""
        return (
            0 <= target_square < 64
            and target_square != self._piece_dragged_from_square
            and self._game.legal_moves
            and target_square in self._game.legal_moves
        )

    def _make_move(self, target_square: int) -> None:
        """Execute move and update board state."""
        self._game.to_square = target_square
        self._game.find_move(self._piece_dragged_from_square, target_square)

        self._reset_drag_state()
        self._game.reset_squares()
        self.update()

    def _reset_drag_state(self) -> None:
        """Reset state variables of drag operation."""
        self._is_dragging = False
        self._piece_dragged_from_square = None
        self._dragged_piece = None
        self._drag_position_x = None
        self._drag_position_y = None

    def _cancel_move(self, x_position: float, y_position: float) -> None:
        """Start animation to return piece to original position."""
        self._start_animation(QPointF(x_position, y_position))

    def paintEvent(self, event: QPaintEvent) -> None:
        """Render board and pieces being animated."""
        cache_key: tuple = self._cache_key()

        board_svg: bytes = self._board_svg(cache_key)
        self.load(board_svg)
        super().paintEvent(event)

        if self._is_dragging and self._can_render_dragged_piece():
            self._render_piece(self._drag_position_x, self._drag_position_y)
        elif (
            self._is_animating
            and self._dragged_piece
            and self._current_animation_position
        ):
            self._render_piece(
                self._current_animation_position.x(),
                self._current_animation_position.y(),
            )

    @lru_cache(maxsize=20)
    def _board_svg(self, cache_key: tuple) -> bytes:
        """Generate SVG representation of current board state."""
        if (
            self._is_dragging or self._is_animating
        ) and self._piece_dragged_from_square is not None:
            temporary_board: Board = self._game.board.copy()
            temporary_board.set_piece_at(self._piece_dragged_from_square, None)
        else:
            temporary_board = self._game.board

        svg_board: str = svg.board(
            arrows=self._game.arrow,
            board=temporary_board,
            check=self._game.king_in_check,
            colors=self._color_dict(),
            orientation=setting_value("board", "orientation"),
            squares=self._game.legal_moves,
        )

        return svg_board.encode()

    def _can_render_dragged_piece(self) -> bool:
        """Check if necessary conditions for rendering piece exist."""
        return (
            self._dragged_piece is not None
            and self._drag_position_x is not None
            and self._drag_position_y is not None
        )

    @lru_cache(maxsize=20)
    def _piece_renderer(self, piece_symbol: str) -> QSvgRenderer:
        """Return renderer for specified piece."""
        if piece_symbol not in self._piece_renderers:
            dragged_piece: Piece = self._dragged_piece
            piece_svg: str = svg.piece(dragged_piece)
            renderer: QSvgRenderer = QSvgRenderer()
            renderer.load(piece_svg.encode())
            self._piece_renderers[piece_symbol] = renderer

        return self._piece_renderers[piece_symbol]

    def _render_piece(self, x_position: float | None, y_position: float | None) -> None:
        """Render piece at specified position."""
        if x_position is None or y_position is None:
            return

        painter: QPainter = QPainter(self)
        renderer: QSvgRenderer = self._piece_renderer(self._dragged_piece.symbol())

        piece_rectangle: QRectF = QRectF(
            x_position - HALF_SQUARE,
            y_position - HALF_SQUARE,
            SQUARE_SIZE,
            SQUARE_SIZE,
        )

        renderer.render(painter, piece_rectangle)
        painter.end()
