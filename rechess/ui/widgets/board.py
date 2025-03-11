from __future__ import annotations

from functools import lru_cache
from typing import ClassVar, Final, NamedTuple

from chess import svg
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
from PySide6.QtGui import QColor, QPainter
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


class BoardCacheKey(NamedTuple):
    """Cache key for board state."""

    arrows: tuple[tuple[Square, Square], ...]
    board_colors: tuple[tuple[str, str], ...]
    dragging_from_square: Square | None
    fen: str
    is_animating: bool
    king_in_check: Square | None
    legal_moves: tuple[Square, ...] | None
    orientation: bool


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
        self._dragging_position_x: float | None = None
        self._dragging_position_y: float | None = None

    def _clear_cache(self) -> None:
        """Clear cached SVG and update board orientation."""
        self._renderer.invalidate_cache()
        current_orientation: bool = setting_value("board", "orientation")

        if self._current_orientation != current_orientation:
            self._current_orientation = current_orientation

        self.update()

    def _cache_key(self) -> BoardCacheKey:
        """Generate unique key for board state."""
        dragging_from_square: Square | None = (
            self._piece_dragged_from_square
            if self._is_dragging or self._animator.is_animating
            else None
        )

        return BoardCacheKey(
            arrows=tuple(self._game.arrow),
            board_colors=self._renderer.hashable_board_colors(),
            dragging_from_square=dragging_from_square,
            fen=self.board_fen(),
            is_animating=self._animator.is_animating,
            king_in_check=self._game.king_in_check,
            legal_moves=(
                tuple(self._game.legal_moves)
                if self._game.legal_moves is not None
                else None
            ),
            orientation=self._current_orientation,
        )

    def _square_center(self, square: Square) -> QPointF:
        """Calculate center coordinates of square."""
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
        self.reset_game_squares()
        self.update()

    def _has_dragging_coordinates(self) -> bool:
        """Check whether all data for piece rendering is available."""
        return (
            self._dragged_piece is not None
            and self._dragging_position_x is not None
            and self._dragging_position_y is not None
        )

    # Delegation methods to follow Law of Demeter
    def piece_at(self, square: Square) -> Piece | None:
        """Get piece at given square."""
        return self._game.board.piece_at(square)

    def is_piece_turn(self, piece: Piece) -> bool:
        """Check if it's given piece's turn to move."""
        return piece is not None and piece.color == self._game.board.turn

    def board_fen(self) -> str:
        """Get FEN representation of current board."""
        return self._game.board.fen()

    def set_origin_square(self, square: Square) -> None:
        """Set origin square for move."""
        self._game.from_square = square

    def set_target_square(self, square: Square) -> None:
        """Set target square for move."""
        self._game.to_square = square

    def find_move(self, from_square: Square, to_square: Square) -> None:
        """Find legal move between given squares."""
        self._game.find_move(from_square, to_square)

    def reset_game_squares(self) -> None:
        """Reset origin and target squares in game."""
        self._game.reset_squares()

    def locate_file_and_rank(self, x: float, y: float) -> tuple[int, int]:
        """Convert screen coordinates to board coordinates."""
        return self._game.locate_file_and_rank(x, y)

    def locate_square(self, x: float, y: float) -> None:
        """Handle square location from coordinates."""
        self._game.locate_square(x, y)

    def board_copy(self) -> Board:
        """Get copy of current board."""
        return self._game.board.copy()

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
        cache_key: BoardCacheKey = self._cache_key()
        board_svg: bytes = self._renderer.board_svg(cache_key)
        self.load(board_svg)
        super().paintEvent(event)

        if self._is_dragging and self._has_dragging_coordinates():
            self._renderer.render_piece(
                self._dragging_position_x, self._dragging_position_y
            )
        elif self._animator.is_animating:
            animated_piece: Piece | None = self._animator.dragged_piece
            animation_position: QPointF = self._animator._position
            if animated_piece and animation_position:
                self._renderer.render_piece(
                    animation_position.x(), animation_position.y(), animated_piece
                )


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
    """Handles board rendering with SVG."""

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

    def hashable_board_colors(self) -> tuple[tuple[str, str], ...]:
        """Return board colors as hashable object for caching."""
        return tuple(self.board_colors().items())

    @lru_cache(maxsize=128)
    def board_svg(self, cache_key: BoardCacheKey) -> bytes:
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
        self._svg_board: SvgBoard = board

    def square_index(self, x: float, y: float) -> Square | None:
        """Convert screen coordinates to board square index."""
        square_position: tuple[int, int] = self._svg_board.locate_file_and_rank(x, y)
        file: int = square_position[0]
        rank: int = square_position[1]
        square_index: Square = file + (rank * 8)
        return square_index if square_index < ALL_SQUARES else None

    def update_cursor(self, x: float, y: float) -> None:
        """Set cursor shape based on square content."""
        square_index: Square | None = self.square_index(x, y)
        if square_index is not None:
            piece: Piece | None = self._svg_board.piece_at(square_index)

            if self._svg_board.is_piece_turn(piece):
                self._svg_board.setCursor(Qt.CursorShape.OpenHandCursor)
                return

        self._svg_board.setCursor(Qt.CursorShape.ArrowCursor)

    def start_dragging(self, square: Square, piece: Piece, x: float, y: float) -> None:
        """Start piece dragging operation from square."""
        self._svg_board._is_dragging = True
        self._svg_board._piece_dragged_from_square = square
        self._svg_board._dragged_piece = piece
        self._svg_board._dragging_position_x = x
        self._svg_board._dragging_position_y = y
        self._svg_board.set_origin_square(square)

        self._svg_board.setCursor(Qt.CursorShape.ClosedHandCursor)

        self._svg_board._temporary_board = self._svg_board.board_copy()
        self._svg_board._temporary_board.set_piece_at(square, None)

        self._svg_board.update()

    def is_valid_move(self, target_square: Square) -> bool:
        """Verify whether target square is valid for current piece."""
        legal_moves = self._svg_board._game.legal_moves
        return (
            0 <= target_square < ALL_SQUARES
            and target_square != self._svg_board._piece_dragged_from_square
            and legal_moves
            and target_square in legal_moves
        )

    def execute_move(self, target_square: Square) -> None:
        """Complete move and update game state."""
        self._svg_board.set_target_square(target_square)
        self._svg_board.find_move(
            self._svg_board._piece_dragged_from_square, target_square
        )

        self.reset_dragging_state()
        self._svg_board.reset_game_squares()
        self._svg_board.update()

    def reset_dragging_state(self) -> None:
        """Reset all dragging-related state attributes."""
        self._svg_board._is_dragging = False
        self._svg_board._piece_dragged_from_square = None
        self._svg_board._dragged_piece = None
        self._svg_board._dragging_position_x = None
        self._svg_board._dragging_position_y = None
        self._svg_board._temporary_board = None
        self._svg_board.setCursor(Qt.CursorShape.ArrowCursor)

    def cancel_move(self, x: float, y: float) -> None:
        """Animate piece returning to origin square for invalid move."""
        self._svg_board._is_dragging = False
        self._svg_board.setCursor(Qt.CursorShape.ArrowCursor)

        self._svg_board._animator.start_return_animation(
            QPointF(x, y),
            self._svg_board._piece_dragged_from_square,
            self._svg_board._dragged_piece,
        )

    def handle_mouse_press(self, event: QMouseEvent) -> None:
        """Handle mouse press for piece selection or targeting."""
        if self._svg_board._animator.is_animating:
            return

        x: float = event.position().x()
        y: float = event.position().y()

        square_index: Square | None = self.square_index(x, y)

        if square_index is not None:
            piece: Piece | None = self._svg_board.piece_at(square_index)
            if self._svg_board.is_piece_turn(piece):
                self.start_dragging(square_index, piece, x, y)
                return

        self._svg_board.locate_square(x, y)

    def handle_mouse_move(self, event: QMouseEvent) -> None:
        """Update piece position during dragging or cursor shape."""
        if self._svg_board._animator.is_animating:
            return

        x: float = event.position().x()
        y: float = event.position().y()

        if self._svg_board._is_dragging:
            self._svg_board._dragging_position_x = x
            self._svg_board._dragging_position_y = y
            self._svg_board.update()
        else:
            self.update_cursor(x, y)

    def handle_mouse_release(self, event: QMouseEvent) -> None:
        """Process move or cancel piece dragging when mouse released."""
        if self._svg_board._animator.is_animating:
            return

        if (
            not self._svg_board._is_dragging
            or self._svg_board._piece_dragged_from_square is None
        ):
            return

        x: float = event.position().x()
        y: float = event.position().y()

        square_index: Square | None = self.square_index(x, y)

        if square_index is not None and self.is_valid_move(square_index):
            self.execute_move(square_index)
        else:
            self.cancel_move(x, y)
