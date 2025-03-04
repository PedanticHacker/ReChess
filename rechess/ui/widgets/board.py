from __future__ import annotations

from functools import lru_cache
from typing import Final

from chess import svg
from PySide6.QtCore import Property, QPointF, QRectF, QTimer, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QSvgWidget

from rechess.utils import setting_value


ALL_SQUARES: Final[int] = 64
ANIMATION_TIME: Final[int] = 20
BOARD_MARGIN: Final[float] = 20.0
HALF_SQUARE: Final[float] = 35.0
SQUARE_CENTER_OFFSET: Final[float] = 55.0
SQUARE_SIZE: Final[float] = 70.0

svg.XX = "<circle id='xx' r='4.5' cx='22.5' cy='22.5' stroke='#303030' fill='#e5e5e5'/>"


class SvgBoard(QSvgWidget):
    coord: Property = Property(
        QColor,
        lambda self: self._coord,
        lambda self, color: self._update_color("_coord", color),
    )
    inner_border: Property = Property(
        QColor,
        lambda self: self._inner_border,
        lambda self, color: self._update_color("_inner_border", color),
    )
    margin: Property = Property(
        QColor,
        lambda self: self._margin,
        lambda self, color: self._update_color("_margin", color),
    )
    outer_border: Property = Property(
        QColor,
        lambda self: self._outer_border,
        lambda self, color: self._update_color("_outer_border", color),
    )
    square_dark: Property = Property(
        QColor,
        lambda self: self._square_dark,
        lambda self, color: self._update_color("_square_dark", color),
    )
    square_dark_lastmove: Property = Property(
        QColor,
        lambda self: self._square_dark_lastmove,
        lambda self, color: self._update_color("_square_dark_lastmove", color),
    )
    square_light: Property = Property(
        QColor,
        lambda self: self._square_light,
        lambda self, color: self._update_color("_square_light", color),
    )
    square_light_lastmove: Property = Property(
        QColor,
        lambda self: self._square_light_lastmove,
        lambda self, color: self._update_color("_square_light_lastmove", color),
    )

    def __init__(self, game: Game) -> None:
        super().__init__()

        self._game: Game = game
        self._game.move_played.connect(self._clear_cache)

        self._setup_colors()
        self._setup_drag_state()
        self._setup_animation()

        self._piece_renderers: dict[str, QSvgRenderer] = {}
        self._temporary_board: Board | None = None

        self._easing_values: list[float] = []
        self._precompute_easing_values()

        self._current_orientation: bool = setting_value("board", "orientation")

        self.setMouseTracking(True)

    def _update_color(self, property_name: str, color_value: QColor) -> None:
        """Update color, clear color cache, and refresh board."""
        setattr(self, property_name, color_value)
        self._color_dict.cache_clear()
        self.update()

    def _setup_colors(self) -> None:
        """Set up colors for board elements."""
        self._coord: QColor = QColor()
        self._inner_border: QColor = QColor()
        self._margin: QColor = QColor()
        self._outer_border: QColor = QColor()
        self._square_dark: QColor = QColor()
        self._square_dark_lastmove: QColor = QColor()
        self._square_light: QColor = QColor()
        self._square_light_lastmove: QColor = QColor()

    def _setup_drag_state(self) -> None:
        """Set up state for piece dragging."""
        self._is_dragging: bool = False
        self._piece_dragged_from_square: int | None = None
        self._dragged_piece: Piece | None = None
        self._drag_position_x: float | None = None
        self._drag_position_y: float | None = None

    def _setup_animation(self) -> None:
        """Set up animation system for piece movement."""
        self._is_animating: bool = False
        self._animation_timer: QTimer = QTimer(self)
        self._animation_timer.timeout.connect(self._step_animation)
        self._animation_start_position: QPointF | None = None
        self._animation_end_position: QPointF | None = None
        self._current_animation_position: QPointF | None = None
        self._animation_steps: int = 10
        self._current_animation_step: int = 0

    def _update_cursor(self, x: float, y: float) -> None:
        """Update cursor based on element under mouse arrow."""
        square_index: int | None = self._square_index(x, y)
        if square_index is not None:
            piece: Piece | None = self._game.board.piece_at(square_index)
            if piece and piece.color == self._game.board.turn:
                self.setCursor(Qt.CursorShape.OpenHandCursor)
                return
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def _precompute_easing_values(self) -> None:
        """Precompute easing values for smoother animations."""
        steps: int = self._animation_steps
        self._easing_values = []

        for step in range(steps + 1):
            linear: float = step / steps
            eased: float = 1.0 - (1.0 - linear) ** 2
            self._easing_values.append(eased)

    def _clear_cache(self) -> None:
        """Clear SVG cache and update orientation if changed."""
        self._board_svg.cache_clear()
        current_orientation: bool = setting_value("board", "orientation")
        if self._current_orientation != current_orientation:
            self._current_orientation = current_orientation
        self.update()

    @lru_cache(maxsize=1)
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
        """Create unique key for caching board SVG state."""
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
            self._current_orientation,
            hash(frozenset(self._color_dict().items())),
            dragging_square,
            self._is_animating,
        )

    def _square_center(self, square: int) -> QPointF:
        """Calculate and return center point coordinates of `square`."""
        file: int = square % 8
        rank: int = square // 8
        flipped_file: int = 7 - file
        flipped_rank: int = 7 - rank

        if self._current_orientation:
            x: float = SQUARE_CENTER_OFFSET + (SQUARE_SIZE * file)
            y: float = SQUARE_CENTER_OFFSET + (SQUARE_SIZE * flipped_rank)
        else:
            x = SQUARE_CENTER_OFFSET + (SQUARE_SIZE * flipped_file)
            y = SQUARE_CENTER_OFFSET + (SQUARE_SIZE * rank)

        return QPointF(x, y)

    def _start_animation(self, current_position: QPointF) -> None:
        """Begin animation from current position to origin square."""
        if not self._piece_dragged_from_square:
            return

        self._is_animating = True
        self._is_dragging = False
        self.setCursor(Qt.CursorShape.ArrowCursor)

        self._animation_start_position = current_position
        self._animation_end_position = self._square_center(
            self._piece_dragged_from_square
        )
        self._current_animation_position = current_position
        self._current_animation_step = 0
        self._animation_timer.start(ANIMATION_TIME)

    def _step_animation(self) -> None:
        """Update piece position for each animation step."""
        if self._current_animation_step >= self._animation_steps:
            self._end_animation()
            return

        self._current_animation_step += 1
        eased_progress: float = self._easing_values[self._current_animation_step]

        if self._animation_start_position and self._animation_end_position:
            start_position: QPointF = self._animation_start_position
            end_position: QPointF = self._animation_end_position
            self._current_animation_position = QPointF(
                start_position.x() * (1 - eased_progress)
                + end_position.x() * eased_progress,
                start_position.y() * (1 - eased_progress)
                + end_position.y() * eased_progress,
            )
            self.update()

    def _end_animation(self) -> None:
        """Clean up after animation completes."""
        self._animation_timer.stop()
        self._is_animating = False
        self._animation_start_position = None
        self._animation_end_position = None
        self._current_animation_position = None
        self._piece_dragged_from_square = None
        self._dragged_piece = None
        self._temporary_board = None
        self._game.reset_squares()
        self.update()

    def _square_index(self, x: float, y: float) -> int | None:
        """Convert `x` and `y` to square index."""
        square_position: tuple[int, int] = self._game.locate_file_and_rank(x, y)
        file, rank = square_position
        square_index: int = file + (8 * rank)
        return square_index if square_index < ALL_SQUARES else None

    def mousePressEvent(self, event) -> None:
        if self._is_animating:
            return

        x: float = event.position().x()
        y: float = event.position().y()

        square_index: int | None = self._square_index(x, y)
        if square_index is not None:
            piece: Piece | None = self._game.board.piece_at(square_index)
            if piece and piece.color == self._game.board.turn:
                self._start_dragging(square_index, piece, x, y)
                return

        self._game.locate_square(x, y)

    def _start_dragging(self, square: int, piece: Piece, x: float, y: float) -> None:
        """Set up drag operation for piece."""
        self._is_dragging = True
        self._piece_dragged_from_square = square
        self._dragged_piece = piece
        self._drag_position_x = x
        self._drag_position_y = y
        self._game.from_square = square

        self.setCursor(Qt.CursorShape.ClosedHandCursor)

        self._temporary_board = self._game.board.copy()
        self._temporary_board.set_piece_at(square, None)

        self.update()

    def mouseMoveEvent(self, event) -> None:
        """Update dragged piece position or mouse cursor."""
        if self._is_animating:
            return

        x: float = event.position().x()
        y: float = event.position().y()

        if self._is_dragging:
            self._drag_position_x = x
            self._drag_position_y = y
            self.update()
        else:
            self._update_cursor(x, y)
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        """Complete or cancel move when mouse is released."""
        if self._is_animating:
            return

        if not self._is_dragging or self._piece_dragged_from_square is None:
            super().mouseReleaseEvent(event)
            return

        x: float = event.position().x()
        y: float = event.position().y()

        square_index: int | None = self._square_index(x, y)
        if square_index is not None and self._is_valid_move(square_index):
            self._execute_move(square_index)
        else:
            self._cancel_move(x, y)

    def _is_valid_move(self, target_square: int) -> bool:
        """Check whether `target_square` is valid for current piece."""
        return (
            0 <= target_square < ALL_SQUARES
            and target_square != self._piece_dragged_from_square
            and self._game.legal_moves
            and target_square in self._game.legal_moves
        )

    def _execute_move(self, target_square: int) -> None:
        """Execute move and update board state."""
        self._game.to_square = target_square
        self._game.find_move(self._piece_dragged_from_square, target_square)

        self._reset_drag_state()
        self._game.reset_squares()
        self.update()

    def _reset_drag_state(self) -> None:
        """Reset state related to drag operation."""
        self._is_dragging = False
        self._piece_dragged_from_square = None
        self._dragged_piece = None
        self._drag_position_x = None
        self._drag_position_y = None
        self._temporary_board = None
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def _cancel_move(self, x: float, y: float) -> None:
        """Start animation to return piece to original position."""
        self._start_animation(QPointF(x, y))

    def paintEvent(self, event) -> None:
        """Draw board and any piece being dragged or animated."""
        cache_key: tuple = self._cache_key()

        board_svg: bytes = self._board_svg(cache_key)
        self.load(board_svg)
        super().paintEvent(event)

        if self._is_dragging and self._has_drag_coordinates():
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

    @lru_cache(maxsize=128)
    def _board_svg(self, _cache_key: tuple) -> bytes:
        """Generate SVG representation of current board state."""
        if (
            self._is_dragging or self._is_animating
        ) and self._temporary_board is not None:
            board_to_render: Board = self._temporary_board
        else:
            board_to_render = self._game.board

        svg_board: str = svg.board(
            arrows=self._game.arrow,
            board=board_to_render,
            check=self._game.king_in_check,
            colors=self._color_dict(),
            orientation=self._current_orientation,
            squares=self._game.legal_moves,
        )

        return svg_board.encode()

    def _has_drag_coordinates(self) -> bool:
        """Check if all conditions to render dragged piece are met."""
        return (
            self._dragged_piece is not None
            and self._drag_position_x is not None
            and self._drag_position_y is not None
        )

    @lru_cache(maxsize=12)
    def _svg_renderer_for_piece(self, piece_symbol: str) -> QSvgRenderer:
        """Return SVG renderer for specified chess piece."""
        if piece_symbol not in self._piece_renderers:
            dragged_piece: Piece = self._dragged_piece
            piece_svg: str = svg.piece(dragged_piece)
            renderer: QSvgRenderer = QSvgRenderer()
            renderer.load(piece_svg.encode())
            self._piece_renderers[piece_symbol] = renderer

        return self._piece_renderers[piece_symbol]

    def _render_piece(self, x: float | None, y: float | None) -> None:
        """Render chess piece at specified coordinates."""
        if x is None or y is None:
            return

        painter: QPainter = QPainter(self)
        renderer: QSvgRenderer = self._svg_renderer_for_piece(
            self._dragged_piece.symbol()
        )

        piece_rectangle: QRectF = QRectF(
            x - HALF_SQUARE,
            y - HALF_SQUARE,
            SQUARE_SIZE,
            SQUARE_SIZE,
        )

        renderer.render(painter, piece_rectangle)
        painter.end()
