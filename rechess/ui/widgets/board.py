from __future__ import annotations

from functools import lru_cache
from typing import ClassVar, Final

from chess import Square, svg
from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QObject,
    QPointF,
    QPropertyAnimation,
    QRectF,
    Qt,
    Signal,
)
from PySide6.QtGui import QColor, QPainter, QMouseEvent, QKeyEvent
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QSvgWidget

from rechess.utils import setting_value


ALL_SQUARES: Final[int] = 64
ANIMATION_DURATION: Final[int] = 200
BOARD_MARGIN: Final[float] = 20.0
HALF_SQUARE: Final[float] = 35.0
SQUARE_CENTER_OFFSET: Final[float] = 55.0
SQUARE_SIZE: Final[float] = 70.0

svg.XX = "<circle id='xx' r='4.5' cx='22.5' cy='22.5' stroke='#303030' fill='#e5e5e5'/>"


class PieceAnimator(QObject):
    """Piece drag-and-drop animation management for board."""

    animation_completed: ClassVar[Signal] = Signal()

    position: Property = Property(
        QPointF,
        lambda self: self._position,
        lambda self, value: self._update_position(value),
    )

    def __init__(self, svg_board: SvgBoard) -> None:
        super().__init__(svg_board)

        self.svg_board: SvgBoard = svg_board
        self.is_animating: bool = False
        self.dragged_piece: Piece | None = None
        self.origin_square: Square | None = None

        self._position: QPointF = QPointF(0.0, 0.0)
        self._animation: QPropertyAnimation = QPropertyAnimation(self, b"position")
        self._animation.setDuration(ANIMATION_DURATION)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.finished.connect(self._end_animation)

    def _update_position(self, value: QPointF) -> None:
        """Update position and trigger redraw."""
        self._position = value
        self.svg_board.update()

    def start_return_animation(
        self,
        current_position: QPointF,
        origin_square: Square,
        piece: Piece,
    ) -> None:
        """Start animation to return piece to origin square."""
        self.is_animating = True
        self.dragged_piece = piece
        self.origin_square = origin_square

        self._animation.setStartValue(current_position)
        self._animation.setEndValue(self.svg_board._square_center(origin_square))
        self._animation.start()

    def _end_animation(self) -> None:
        """Clean up after animation completes."""
        self.is_animating = False
        self.animation_completed.emit()


class BoardRenderer:
    """Handles chess board rendering with SVG."""

    def __init__(self, board: SvgBoard) -> None:
        """Set up board renderer with colors and cached renderers."""
        self.board: SvgBoard = board
        self._piece_renderers: dict[str, QSvgRenderer] = {}

    @lru_cache(maxsize=1)
    def board_colors(self) -> dict[str, str]:
        """Create color name dictionary for SVG rendering."""
        return {
            "coord": self.board._coord.name(),
            "inner border": self.board._inner_border.name(),
            "margin": self.board._margin.name(),
            "outer border": self.board._outer_border.name(),
            "square dark": self.board._square_dark.name(),
            "square dark lastmove": self.board._square_dark_lastmove.name(),
            "square light": self.board._square_light.name(),
            "square light lastmove": self.board._square_light_lastmove.name(),
        }

    def hashable_board_colors(self) -> tuple:
        """Return board colors as hashable object for caching."""
        return tuple(self.board_colors().items())

    @lru_cache(maxsize=128)
    def board_svg(self, cache_key: tuple) -> bytes:
        """Generate SVG representation of current board."""
        if (
            self.board._is_dragging and self.board._temporary_board
        ) or self.board._animator.is_animating:
            board_to_render: Board = self.board._temporary_board
        else:
            board_to_render = self.board._game.board

        svg_board: str = svg.board(
            arrows=self.board._game.arrow,
            board=board_to_render,
            check=self.board._game.king_in_check,
            colors=self.board_colors(),
            orientation=self.board._current_orientation,
            squares=self.board._game.legal_moves,
        )
        return svg_board.encode()

    @lru_cache(maxsize=12)
    def svg_renderer_for_piece(self, piece_symbol: str) -> QSvgRenderer:
        """Get or create SVG renderer for piece."""
        if piece_symbol not in self._piece_renderers:
            piece_to_render: Piece | None = None

            if self.board._is_dragging and self.board._dragged_piece:
                piece_to_render = self.board._dragged_piece
            elif self.board._animator.is_animating:
                piece_to_render = self.board._animator.dragged_piece

            if piece_to_render:
                piece_svg: str = svg.piece(piece_to_render)
                renderer: QSvgRenderer = QSvgRenderer()
                renderer.load(piece_svg.encode())
                self._piece_renderers[piece_symbol] = renderer

        return self._piece_renderers[piece_symbol]

    def render_piece(self, x: float, y: float, piece: Piece | None = None) -> None:
        """Draw piece at specified coordinates."""
        piece_to_render: Piece | None = piece

        if not piece_to_render and self.board._is_dragging:
            piece_to_render = self.board._dragged_piece

        if not piece_to_render:
            return

        painter: QPainter = QPainter(self.board)
        renderer: QSvgRenderer = self.svg_renderer_for_piece(piece_to_render.symbol())

        piece_rectangle: QRectF = QRectF(
            x - HALF_SQUARE,
            y - HALF_SQUARE,
            SQUARE_SIZE,
            SQUARE_SIZE,
        )

        renderer.render(painter, piece_rectangle)
        painter.end()

    def invalidate_cache(self) -> None:
        """Clear cached SVG data."""
        self.board_svg.cache_clear()
        self.board_colors.cache_clear()


class BoardInteraction:
    """Manager for interacting with pieces on board."""

    def __init__(self, board: SvgBoard) -> None:
        """Set up board interaction handler."""
        self.board: SvgBoard = board

    def square_index(self, x: float, y: float) -> Square | None:
        """Convert screen coordinates to board square index."""
        square_position: tuple[int, int] = self.board._game.locate_file_and_rank(x, y)
        file: int = square_position[0]
        rank: int = square_position[1]
        square_index: Square = Square(file + (8 * rank))
        return square_index if square_index < ALL_SQUARES else None

    def update_cursor(self, x: float, y: float) -> None:
        """Set cursor shape based on square content."""
        square_index: Square | None = self.square_index(x, y)
        if square_index is not None:
            piece: Piece | None = self.board._game.board.piece_at(square_index)

            if piece and piece.color == self.board._game.board.turn:
                self.board.setCursor(Qt.CursorShape.OpenHandCursor)
                return

        self.board.setCursor(Qt.CursorShape.ArrowCursor)

    def start_dragging(self, square: Square, piece: Piece, x: float, y: float) -> None:
        """Start piece dragging operation from `square`."""
        self.board._is_dragging = True
        self.board._piece_dragged_from_square = square
        self.board._dragged_piece = piece
        self.board._drag_position_x = x
        self.board._drag_position_y = y
        self.board._game.from_square = square

        self.board.setCursor(Qt.CursorShape.ClosedHandCursor)

        self.board._temporary_board = self.board._game.board.copy()
        self.board._temporary_board.set_piece_at(square, None)

        self.board.update()

    def is_valid_move(self, target_square: Square) -> bool:
        """Verify whether target square is valid for current piece."""
        return (
            0 <= target_square < ALL_SQUARES
            and target_square != self.board._piece_dragged_from_square
            and self.board._game.legal_moves
            and target_square in self.board._game.legal_moves
        )

    def execute_move(self, target_square: Square) -> None:
        """Complete move and update game state."""
        self.board._game.to_square = target_square
        self.board._game.find_move(self.board._piece_dragged_from_square, target_square)

        self.reset_dragging_state()
        self.board._game.reset_squares()
        self.board.update()

    def reset_dragging_state(self) -> None:
        """Reset all dragging-related state attributes."""
        self.board._is_dragging = False
        self.board._piece_dragged_from_square = None
        self.board._dragged_piece = None
        self.board._drag_position_x = None
        self.board._drag_position_y = None
        self.board._temporary_board = None
        self.board.setCursor(Qt.CursorShape.ArrowCursor)

    def cancel_move(self, x: float, y: float) -> None:
        """Animate piece returning to origin square for invalid move."""
        self.board._is_dragging = False
        self.board.setCursor(Qt.CursorShape.ArrowCursor)

        self.board._animator.start_return_animation(
            QPointF(x, y),
            self.board._piece_dragged_from_square,
            self.board._dragged_piece,
        )

    def handle_mouse_press(self, event: QMouseEvent) -> None:
        """Handle mouse press for piece selection or targeting."""
        if self.board._animator.is_animating:
            return

        x: float = event.position().x()
        y: float = event.position().y()

        square_index: Square | None = self.square_index(x, y)

        if square_index is not None:
            piece: Piece | None = self.board._game.board.piece_at(square_index)
            if piece and piece.color == self.board._game.board.turn:
                self.start_dragging(square_index, piece, x, y)
                return

        self.board._game.locate_square(x, y)

    def handle_mouse_move(self, event: QMouseEvent) -> None:
        """Update piece position during dragging or cursor shape."""
        if self.board._animator.is_animating:
            return

        x: float = event.position().x()
        y: float = event.position().y()

        if self.board._is_dragging:
            self.board._drag_position_x = x
            self.board._drag_position_y = y
            self.board.update()
        else:
            self.update_cursor(x, y)

    def handle_mouse_release(self, event: QMouseEvent) -> None:
        """Process move or cancel piece dragging when mouse released."""
        if self.board._animator.is_animating:
            return

        if not self.board._is_dragging or self.board._piece_dragged_from_square is None:
            return

        x: float = event.position().x()
        y: float = event.position().y()

        square_index: Square | None = self.square_index(x, y)

        if square_index is not None and self.is_valid_move(square_index):
            self.execute_move(square_index)
        else:
            self.cancel_move(x, y)


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
        self._renderer: BoardRenderer = BoardRenderer(self)
        self._interaction: BoardInteraction = BoardInteraction(self)
        self._temporary_board: Board | None = None
        self._current_orientation: bool = setting_value("board", "orientation")

        self.setMouseTracking(True)

    def _update_color(self, property_name: str, color_value: QColor) -> None:
        """Update color property and refresh board display."""
        setattr(self, property_name, color_value)
        self._renderer.invalidate_cache()
        self.update()

    def _setup_colors(self) -> None:
        """Set up color properties for board elements."""
        self._coord: QColor = QColor()
        self._inner_border: QColor = QColor()
        self._margin: QColor = QColor()
        self._outer_border: QColor = QColor()
        self._square_dark: QColor = QColor()
        self._square_dark_lastmove: QColor = QColor()
        self._square_light: QColor = QColor()
        self._square_light_lastmove: QColor = QColor()

    def _setup_dragging_state(self) -> None:
        """Set up state variables for piece dragging."""
        self._is_dragging: bool = False
        self._piece_dragged_from_square: Square | None = None
        self._dragged_piece: Piece | None = None
        self._drag_position_x: float | None = None
        self._drag_position_y: float | None = None

    def _clear_cache(self) -> None:
        """Clear cached SVG and update board orientation."""
        self._renderer.invalidate_cache()
        current_orientation: bool = setting_value("board", "orientation")

        if self._current_orientation != current_orientation:
            self._current_orientation = current_orientation

        self.update()

    def _cache_key(self) -> tuple:
        """Generate unique key for board state caching."""
        dragging_square: Square | None = (
            self._piece_dragged_from_square
            if self._is_dragging or self._animator.is_animating
            else None
        )

        return (
            self._game.board.fen(),
            tuple(self._game.legal_moves) if self._game.legal_moves else None,
            tuple(self._game.arrow) if self._game.arrow else None,
            self._game.king_in_check,
            self._current_orientation,
            self._renderer.hashable_board_colors(),
            dragging_square,
            self._animator.is_animating,
        )

    def _square_center(self, square: Square) -> QPointF:
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

    def _has_dragging_coordinates(self) -> bool:
        """Check whether all data for piece rendering is available."""
        return (
            self._dragged_piece is not None
            and self._drag_position_x is not None
            and self._drag_position_y is not None
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press for piece selection or targeting."""
        self._interaction.handle_mouse_press(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Update piece position during dragging or cursor shape."""
        self._interaction.handle_mouse_move(event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Process move or cancel piece dragging when mouse released."""
        self._interaction.handle_mouse_release(event)
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle keyboard navigation."""
        super().keyPressEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Render board and dragged or animated pieces."""
        cache_key: tuple = self._cache_key()
        board_svg: bytes = self._renderer.board_svg(cache_key)
        self.load(board_svg)
        super().paintEvent(event)

        if self._is_dragging and self._has_dragging_coordinates():
            self._renderer.render_piece(self._drag_position_x, self._drag_position_y)
        elif self._animator.is_animating:
            animated_piece: Piece | None = self._animator.dragged_piece
            animation_position: QPointF = self._animator._position
            if animated_piece and animation_position:
                self._renderer.render_piece(
                    animation_position.x(), animation_position.y(), animated_piece
                )
