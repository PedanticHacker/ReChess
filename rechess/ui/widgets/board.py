from __future__ import annotations

from functools import lru_cache
from typing import ClassVar, Final

from chess import svg
from PySide6.QtCore import Property, QObject, QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QSvgWidget

from rechess.utils import setting_value


ALL_SQUARES: Final[int] = 64
ANIMATION_STEPS: Final[int] = 10
ANIMATION_TIME: Final[int] = 20
BOARD_MARGIN: Final[float] = 20.0
HALF_SQUARE: Final[float] = 35.0
SQUARE_CENTER_OFFSET: Final[float] = 55.0
SQUARE_SIZE: Final[float] = 70.0

svg.XX = "<circle id='xx' r='4.5' cx='22.5' cy='22.5' stroke='#303030' fill='#e5e5e5'/>"


class PieceAnimator(QObject):
    """Piece drag-and-drop animation management for board."""

    animation_completed: ClassVar[Signal] = Signal()

    def __init__(self, svg_board: SvgBoard) -> None:
        super().__init__(svg_board)

        self.svg_board: SvgBoard = svg_board

        self.animation_timer: QTimer = QTimer(svg_board)
        self.animation_timer.timeout.connect(self._step_animation)

        self.is_animating: bool = False
        self.animation_start_position: QPointF | None = None
        self.animation_end_position: QPointF | None = None
        self.current_animation_position: QPointF | None = None
        self.current_animation_step: int = 0

        self.dragged_piece: Piece | None = None
        self.origin_square: int | None = None

        self.motion_values: list[float] = []
        self._precompute_motion_values()

    def _precompute_motion_values(self) -> None:
        """Calculate and save motion values based on animation steps."""
        for step in range(ANIMATION_STEPS + 1):
            animation_step_fraction: float = step / ANIMATION_STEPS
            motion_value: float = 1.0 - (1.0 - animation_step_fraction) ** 2
            self.motion_values.append(motion_value)

    def start_return_animation(
        self,
        current_position: QPointF,
        origin_square: int,
        piece: Piece,
    ) -> None:
        """Start animation to return piece to origin square."""
        self.is_animating = True
        self.animation_start_position = current_position
        self.animation_end_position = self.svg_board._square_center(origin_square)
        self.current_animation_position = current_position
        self.current_animation_step = 0
        self.dragged_piece = piece
        self.origin_square = origin_square
        self.animation_timer.start(ANIMATION_TIME)

    def _step_animation(self) -> None:
        """Update animation position based on current step."""
        if self.current_animation_step >= ANIMATION_STEPS:
            self._end_animation()
            return

        self.current_animation_step += 1
        motion_progress: float = self.motion_values[self.current_animation_step]

        if self.animation_start_position and self.animation_end_position:
            self.current_animation_position = QPointF(
                self.animation_start_position.x() * (1 - motion_progress)
                + self.animation_end_position.x() * motion_progress,
                self.animation_start_position.y() * (1 - motion_progress)
                + self.animation_end_position.y() * motion_progress,
            )
            self.svg_board.update()

    def _end_animation(self) -> None:
        """Stop animation and emit completion signal."""
        self.animation_timer.stop()
        self.is_animating = False
        self.animation_completed.emit()


class SvgBoard(QSvgWidget):
    """Interactive SVG-based board with drag-and-drop support."""

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
        self._setup_dragging_state()

        self._animator: PieceAnimator = PieceAnimator(self)
        self._animator.animation_completed.connect(self._on_animation_complete)
        self._piece_renderers: dict[str, QSvgRenderer] = {}
        self._temporary_board: Board | None = None
        self._current_orientation: bool = setting_value("board", "orientation")

        self.setMouseTracking(True)

    def _update_color(self, property_name: str, color_value: QColor) -> None:
        """Update color property and refresh board display."""
        setattr(self, property_name, color_value)
        self._board_colors.cache_clear()
        self.update()

    def _setup_colors(self) -> None:
        """Initialize color properties for board elements."""
        self._coord: QColor = QColor()
        self._inner_border: QColor = QColor()
        self._margin: QColor = QColor()
        self._outer_border: QColor = QColor()
        self._square_dark: QColor = QColor()
        self._square_dark_lastmove: QColor = QColor()
        self._square_light: QColor = QColor()
        self._square_light_lastmove: QColor = QColor()

    def _setup_dragging_state(self) -> None:
        """Initialize state variables for piece dragging."""
        self._is_dragging: bool = False
        self._piece_dragged_from_square: int | None = None
        self._dragged_piece: Piece | None = None
        self._drag_position_x: float | None = None
        self._drag_position_y: float | None = None

    def _update_cursor(self, x: float, y: float) -> None:
        """Set cursor shape based on square content."""
        square_index: int | None = self._square_index(x, y)
        if square_index is not None:
            piece: Piece | None = self._game.board.piece_at(square_index)
            if piece and piece.color == self._game.board.turn:
                self.setCursor(Qt.CursorShape.OpenHandCursor)
                return
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def _clear_cache(self) -> None:
        """Clear cached SVG and update board orientation."""
        self._board_svg.cache_clear()
        current_orientation: bool = setting_value("board", "orientation")

        if self._current_orientation != current_orientation:
            self._current_orientation = current_orientation

        self.update()

    @lru_cache(maxsize=1)
    def _board_colors(self) -> dict[str, str]:
        """Create color name dictionary for SVG rendering."""
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

    def _hashable_board_colors(self) -> tuple:
        """Return board colors as hashable object for caching."""
        return tuple(self._board_colors().items())

    def _cache_key(self) -> tuple:
        """Generate unique key for board state caching."""
        dragging_square: int | None = (
            self._piece_dragged_from_square
            if self._is_dragging or self._animator.is_animating
            else None
        )

        return (
            self._game.board.fen(),
            str(self._game.legal_moves),
            str(self._game.arrow),
            self._game.king_in_check,
            self._current_orientation,
            self._hashable_board_colors(),
            dragging_square,
            self._animator.is_animating,
        )

    def _square_center(self, square: int) -> QPointF:
        """Calculate center coordinates of chess square."""
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

    def _on_animation_complete(self) -> None:
        """Clean up board state after animation completes."""
        self._piece_dragged_from_square = None
        self._dragged_piece = None
        self._temporary_board = None
        self._game.reset_squares()
        self.update()

    def _start_animation(self, current_position: QPointF) -> None:
        """Begin animation to return piece to origin square."""
        if not self._piece_dragged_from_square:
            return

        self._is_dragging = False
        self.setCursor(Qt.CursorShape.ArrowCursor)

        self._animator.start_return_animation(
            current_position,
            self._piece_dragged_from_square,
            self._dragged_piece,
        )

    def _square_index(self, x: float, y: float) -> int | None:
        """Convert screen coordinates to board square index."""
        square_position: tuple[int, int] = self._game.locate_file_and_rank(x, y)
        file: int = square_position[0]
        rank: int = square_position[1]
        square_index: int = file + (8 * rank)
        return square_index if square_index < ALL_SQUARES else None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press for piece selection or targeting."""
        if self._animator.is_animating:
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
        """Start piece dragging operation from `square`."""
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

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Update piece position during dragging or cursor shape."""
        if self._animator.is_animating:
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

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Process move or cancel piece dragging when mouse released."""
        if self._animator.is_animating:
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
        """Verify whether target square is valid for current piece."""
        return (
            0 <= target_square < ALL_SQUARES
            and target_square != self._piece_dragged_from_square
            and self._game.legal_moves
            and target_square in self._game.legal_moves
        )

    def _execute_move(self, target_square: int) -> None:
        """Complete move and update game state."""
        self._game.to_square = target_square
        self._game.find_move(self._piece_dragged_from_square, target_square)

        self._reset_dragging_state()
        self._game.reset_squares()
        self.update()

    def _reset_dragging_state(self) -> None:
        """Reset all dragging-related state attributes."""
        self._is_dragging = False
        self._piece_dragged_from_square = None
        self._dragged_piece = None
        self._drag_position_x = None
        self._drag_position_y = None
        self._temporary_board = None
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def _cancel_move(self, x: float, y: float) -> None:
        """Animate piece returning to origin square for invalid move."""
        self._start_animation(QPointF(x, y))

    def paintEvent(self, event: QPaintEvent) -> None:
        """Render board and dragged or animated pieces."""
        cache_key: tuple = self._cache_key()
        board_svg: bytes = self._board_svg(cache_key)
        self.load(board_svg)
        super().paintEvent(event)

        if self._is_dragging and self._has_dragging_coordinates():
            self._render_piece(self._drag_position_x, self._drag_position_y)
        elif self._animator.is_animating:
            animated_piece: Piece | None = self._animator.dragged_piece
            animation_position: QPointF | None = (
                self._animator.current_animation_position
            )
            if animated_piece and animation_position:
                self._render_piece(
                    animation_position.x(), animation_position.y(), animated_piece
                )

    @lru_cache(maxsize=128)
    def _board_svg(self, cache_key: tuple) -> bytes:
        """Generate SVG representation of current board."""
        if (self._is_dragging and self._temporary_board) or self._animator.is_animating:
            board_to_render: Board = self._temporary_board
        else:
            board_to_render = self._game.board

        svg_board: str = svg.board(
            arrows=self._game.arrow,
            board=board_to_render,
            check=self._game.king_in_check,
            colors=self._board_colors(),
            orientation=self._current_orientation,
            squares=self._game.legal_moves,
        )
        return svg_board.encode()

    def _has_dragging_coordinates(self) -> bool:
        """Check whether all data for piece rendering is available."""
        return (
            self._dragged_piece is not None
            and self._drag_position_x is not None
            and self._drag_position_y is not None
        )

    @lru_cache(maxsize=12)
    def _svg_renderer_for_piece(self, piece_symbol: str) -> QSvgRenderer:
        """Get or create SVG renderer for piece."""
        if piece_symbol not in self._piece_renderers:
            piece_to_render: Piece | None = None

            if self._is_dragging and self._dragged_piece:
                piece_to_render = self._dragged_piece
            elif self._animator.is_animating:
                piece_to_render = self._animator.dragged_piece

            if piece_to_render:
                piece_svg: str = svg.piece(piece_to_render)
                renderer: QSvgRenderer = QSvgRenderer()
                renderer.load(piece_svg.encode())
                self._piece_renderers[piece_symbol] = renderer

        return self._piece_renderers[piece_symbol]

    def _render_piece(
        self, x: float | None, y: float | None, piece: Piece = None
    ) -> None:
        """Draw piece at specified coordinates."""
        if x is None or y is None:
            return

        piece_to_render: Piece | None = piece if piece else self._dragged_piece

        if not piece_to_render:
            return

        painter: QPainter = QPainter(self)
        renderer: QSvgRenderer = self._svg_renderer_for_piece(piece_to_render.symbol())

        piece_rectangle: QRectF = QRectF(
            x - HALF_SQUARE,
            y - HALF_SQUARE,
            SQUARE_SIZE,
            SQUARE_SIZE,
        )

        renderer.render(painter, piece_rectangle)
        painter.end()
