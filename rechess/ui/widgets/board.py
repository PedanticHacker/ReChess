from __future__ import annotations

from functools import lru_cache
from typing import ClassVar, Final, NamedTuple

from chess import svg, Piece
from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QObject,
    QPointF,
    QPropertyAnimation,
    QRectF,
    Qt,
    Signal,
    Slot,
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
    """Type annotations of cache key for board state."""

    arrows: tuple[tuple[Square, Square], ...]
    colors: tuple[tuple[str, str], ...]
    fen: str
    is_animating: bool
    is_white_at_bottom: bool
    king_in_check: Square | None
    square: Square | None


class SvgBoard(QSvgWidget):
    """Management for piece drag-and-drop functionality on SVG board."""

    coord: Property = Property(
        QColor,
        lambda self: self._coord,
        lambda self, color: self.update_color("_coord", color),
    )
    inner_border: Property = Property(
        QColor,
        lambda self: self._inner_border,
        lambda self, color: self.update_color("_inner_border", color),
    )
    margin: Property = Property(
        QColor,
        lambda self: self._margin,
        lambda self, color: self.update_color("_margin", color),
    )
    outer_border: Property = Property(
        QColor,
        lambda self: self._outer_border,
        lambda self, color: self.update_color("_outer_border", color),
    )
    square_dark: Property = Property(
        QColor,
        lambda self: self._square_dark,
        lambda self, color: self.update_color("_square_dark", color),
    )
    square_dark_lastmove: Property = Property(
        QColor,
        lambda self: self._square_dark_lastmove,
        lambda self, color: self.update_color("_square_dark_lastmove", color),
    )
    square_light: Property = Property(
        QColor,
        lambda self: self._square_light,
        lambda self, color: self.update_color("_square_light", color),
    )
    square_light_lastmove: Property = Property(
        QColor,
        lambda self: self._square_light_lastmove,
        lambda self, color: self.update_color("_square_light_lastmove", color),
    )

    def __init__(self, game: Game) -> None:
        super().__init__()

        self._game: Game = game
        self._game.move_played.connect(self.clear_cache)

        self.initialize_colors()
        self.initialize_dragging_state()

        self._renderer: BoardRenderer = BoardRenderer(self)
        self._interactor: BoardInteractor = BoardInteractor(self)

        self._animator: PieceAnimator = PieceAnimator(self)
        self._animator.animation_completed.connect(self.on_animation_complete)

        self.animatable_board: Board | None = None
        self.is_white_at_bottom: bool = setting_value("board", "orientation")

        self.setMouseTracking(True)

    def update_color(self, property_name: str, color_value: QColor) -> None:
        """Update color based on `property_name` and `color_value`."""
        setattr(self, property_name, color_value)
        self._renderer.invalidate_cache()
        self.update()

    def initialize_colors(self) -> None:
        """Initialize color properties for board elements."""
        self._coord: QColor = QColor()
        self._inner_border: QColor = QColor()
        self._margin: QColor = QColor()
        self._outer_border: QColor = QColor()
        self._square_dark: QColor = QColor()
        self._square_dark_lastmove: QColor = QColor()
        self._square_light: QColor = QColor()
        self._square_light_lastmove: QColor = QColor()

    def initialize_dragging_state(self) -> None:
        """Initialize instance attributes for piece dragging."""
        self.is_dragging: bool = False
        self.origin_square: Square | None = None
        self.dragged_piece: Piece | None = None
        self.dragging_from_x: float | None = None
        self.dragging_from_y: float | None = None

    def cache_key(self) -> BoardCacheKey:
        """Generate unique key for board state."""
        dragging_from_origin_square: Square | None = (
            self.origin_square
            if self.is_dragging or self._animator.is_animating
            else None
        )

        return BoardCacheKey(
            arrows=tuple(self._game.arrow),
            colors=self._renderer.hashable_board_colors(),
            fen=self.fen(),
            is_animating=self._animator.is_animating,
            is_white_at_bottom=self.is_white_at_bottom,
            king_in_check=self._game.king_in_check,
            square=dragging_from_origin_square,
        )

    def square_center(self, square: Square) -> QPointF:
        """Calculate center coordinates of `square`."""
        file: int = square % 8
        rank: int = square // 8

        if self.is_white_at_bottom:
            flipped_rank: int = 7 - rank
            x: float = SQUARE_CENTER_OFFSET + (SQUARE_SIZE * file)
            y: float = SQUARE_CENTER_OFFSET + (SQUARE_SIZE * flipped_rank)
        else:
            flipped_file: int = 7 - file
            x = SQUARE_CENTER_OFFSET + (SQUARE_SIZE * flipped_file)
            y = SQUARE_CENTER_OFFSET + (SQUARE_SIZE * rank)

        return QPointF(x, y)

    def piece_can_be_dragged(self) -> bool:
        """Return True if conditions allow for piece to be dragged."""
        return bool(
            self.is_dragging
            and self.dragged_piece
            and self.dragging_from_x
            and self.dragging_from_y
        )

    def piece_at(self, square: Square) -> Piece | None:
        """Get piece at `square`."""
        return self._game.board.piece_at(square)

    def can_drag_piece(self, piece: Piece | None) -> bool:
        """Return True if `piece` can be dragged based on turn."""
        return bool(piece and piece.color == self._game.turn)

    def fen(self) -> str:
        """Get FEN representation of current board setup."""
        return self._game.fen

    def set_origin_square(self, square: Square) -> None:
        """Set `square` as origin for move."""
        self._game.from_square = square

    def set_target_square(self, square: Square) -> None:
        """Set `square` as target for move."""
        self._game.to_square = square

    def find_move(self, origin_square: Square, target_square: Square) -> None:
        """Find legal move for `origin_square` and `target_square`."""
        self._game.find_move(origin_square, target_square)

    def reset_selected_squares(self) -> None:
        """Reset currently selected origin and target squares."""
        self._game.reset_squares()

    def locate_file_and_rank(self, x: float, y: float) -> tuple[int, int]:
        """Get file and rank location from `x` and `y` coordinates."""
        return self._game.locate_file_and_rank(x, y)

    def locate_square(self, x: float, y: float) -> None:
        """Get square location from `x` and `y` coordinates."""
        self._game.locate_square(x, y)

    def board_copy(self) -> Board:
        """Get copy of current board state."""
        return self._game.board.copy()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press for piece selection or targeting."""
        self._interactor.handle_mouse_press(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Update piece position during dragging or cursor shape."""
        self._interactor.handle_mouse_move(event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Process move or cancel piece dragging when mouse released."""
        self._interactor.handle_mouse_release(event)
        super().mouseReleaseEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Render board and dragged or animated pieces."""
        board_svg: bytes = self._renderer.board_as_svg(self.cache_key())
        self.load(board_svg)
        super().paintEvent(event)

        if (
            self.piece_can_be_dragged()
            and self.dragging_from_x
            and self.dragging_from_y
        ):
            self._renderer.render_piece(self.dragging_from_x, self.dragging_from_y)
        elif self._animator.is_animating:
            animated_piece: Piece | None = self._animator.dragged_piece
            animation_position: QPointF = self._animator._position

            if animated_piece and animation_position:
                self._renderer.render_piece(
                    animation_position.x(),
                    animation_position.y(),
                    animated_piece,
                )

    @Slot()
    def clear_cache(self) -> None:
        """Clear cached SVG data and update board orientation."""
        self._renderer.invalidate_cache()
        self.is_white_at_bottom = setting_value("board", "orientation")
        self.update()

    @Slot()
    def on_animation_complete(self) -> None:
        """Clean up board state after animation completes."""
        self.origin_square = None
        self.dragged_piece = None
        self.animatable_board = None
        self.reset_selected_squares()
        self.update()


class PieceAnimator(QObject):
    """Management for piece drag-and-drop animation on board."""

    animation_completed: ClassVar[Signal] = Signal()

    position: Property = Property(
        QPointF,
        lambda self: self._position,
        lambda self, value: self.update_position(value),
    )

    def __init__(self, board: SvgBoard) -> None:
        super().__init__(board)

        self._svg_board: SvgBoard = board

        self.is_animating: bool = False
        self.dragged_piece: Piece | None = None
        self.origin_square: Square | None = None
        self._position: QPointF = QPointF(0.0, 0.0)

        self._animation: QPropertyAnimation = QPropertyAnimation(self, b"position")
        self._animation.setDuration(ANIMATION_DURATION)
        self._animation.setEasingCurve(QEasingCurve.Type.OutBack)
        self._animation.finished.connect(self.end_animation)

    def update_position(self, value: QPointF) -> None:
        """Set position based on `value` and update board."""
        self._position = value
        self._svg_board.update()

    def start_return_animation(
        self,
        dragged_piece: Piece,
        origin_square: Square,
        position: QPointF,
    ) -> None:
        """Start animation to return piece to origin square."""
        self.is_animating = True
        self.dragged_piece = dragged_piece
        self.origin_square = origin_square

        self._animation.setStartValue(position)
        self._animation.setEndValue(self._svg_board.square_center(origin_square))
        self._animation.start()

    def end_animation(self) -> None:
        """Clean up after animation completes."""
        self.is_animating = False
        self.animation_completed.emit()


class BoardRenderer:
    """Management for rendering SVG board."""

    def __init__(self, board: SvgBoard) -> None:
        self._svg_board: SvgBoard = board

        self._piece_renderers: dict[str, QSvgRenderer] = {}
        self._cached_colors: dict[str, str] | None = None

    def is_dragging_with_animatable_board(self) -> bool:
        """Return True if piece dragged and animatable board exists."""
        return bool(self._svg_board.is_dragging and self._svg_board.animatable_board)

    def is_piece_animating(self) -> bool:
        """Return True if piece animation is currently in progress."""
        return self._svg_board._animator.is_animating

    def determine_board_to_render(self) -> Board:
        """Determine which board should be used for rendering."""
        if self.is_dragging_with_animatable_board() or self.is_piece_animating():
            return self._svg_board.animatable_board
        return self._svg_board._game.board

    @lru_cache(maxsize=1)
    def board_colors(self) -> dict[str, str]:
        """Create dictionary with color names for SVG rendering."""
        colors: dict[str, str] = {
            "coord": self._svg_board._coord.name(),
            "inner border": self._svg_board._inner_border.name(),
            "margin": self._svg_board._margin.name(),
            "outer border": self._svg_board._outer_border.name(),
            "square dark": self._svg_board._square_dark.name(),
            "square dark lastmove": self._svg_board._square_dark_lastmove.name(),
            "square light": self._svg_board._square_light.name(),
            "square light lastmove": self._svg_board._square_light_lastmove.name(),
        }
        self._cached_colors = colors
        return colors

    def hashable_board_colors(self) -> tuple[tuple[str, str], ...]:
        """Get board colors as hashable object for caching."""
        if self._cached_colors is None:
            self._cached_colors = self.board_colors()
        return tuple(self._cached_colors.items())

    @lru_cache(maxsize=128)
    def board_as_svg(self, cache_key: BoardCacheKey) -> bytes:
        """Transform current board state into SVG data."""
        svg_board: str = svg.board(
            arrows=cache_key.arrows,
            board=self.determine_board_to_render(),
            check=cache_key.king_in_check,
            colors=self.board_colors(),
            orientation=cache_key.is_white_at_bottom,
            squares=self._svg_board._game.legal_moves,
        )
        return svg_board.encode()

    @lru_cache(maxsize=12)
    def svg_renderer_for_piece(self, piece_symbol: str) -> QSvgRenderer:
        """Get or create piece SVG renderer based on `piece_symbol`."""
        if piece_symbol not in self._piece_renderers:
            svg_piece: str = svg.piece(Piece.from_symbol(piece_symbol))
            renderer: QSvgRenderer = QSvgRenderer()
            renderer.load(svg_piece.encode())
            self._piece_renderers[piece_symbol] = renderer

        return self._piece_renderers[piece_symbol]

    def render_piece(
        self, x: float, y: float, available_piece: Piece | None = None
    ) -> None:
        """Render `piece` at `x` and `y` coordinates."""
        dragged_piece: Piece | None = (
            self._svg_board.dragged_piece if self._svg_board.is_dragging else None
        )
        piece_to_render: Piece | None = available_piece or dragged_piece

        if not piece_to_render:
            return

        painter: QPainter = QPainter(self._svg_board)
        piece_symbol: str = piece_to_render.symbol()
        renderer: QSvgRenderer = self.svg_renderer_for_piece(piece_symbol)

        piece_render_area: QRectF = QRectF(
            x - HALF_SQUARE,
            y - HALF_SQUARE,
            SQUARE_SIZE,
            SQUARE_SIZE,
        )

        renderer.render(painter, piece_render_area)
        painter.end()

    def invalidate_cache(self) -> None:
        """Clear cached SVG data."""
        self.board_as_svg.cache_clear()
        self.board_colors.cache_clear()
        self.svg_renderer_for_piece.cache_clear()
        self._piece_renderers.clear()
        self._cached_colors = None


class BoardInteractor:
    """Management for interacting with pieces on board."""

    def __init__(self, board: SvgBoard) -> None:
        self._svg_board: SvgBoard = board

        self._last_cursor_position: tuple[float, float] | None = None
        self._last_square_index: Square | None = None

    def square_index(self, x: float, y: float) -> Square | None:
        """Convert `x` and `y` coordinates to square index."""
        current_position: tuple[float, float] = (x, y)

        if self._last_cursor_position == current_position and self._last_square_index:
            return self._last_square_index

        file, rank = self._svg_board.locate_file_and_rank(x, y)
        square_index: Square = file + (rank * 8)
        result: Square | None = square_index if square_index < ALL_SQUARES else None

        self._last_cursor_position = current_position
        self._last_square_index = result
        return result

    def update_cursor(self, x: float, y: float) -> None:
        """Set cursor shape based on square index from `x` and `y`."""
        square_index: Square | None = self.square_index(x, y)

        if square_index:
            piece: Piece | None = self._svg_board.piece_at(square_index)

            if self._svg_board.can_drag_piece(piece):
                self._svg_board.setCursor(Qt.CursorShape.OpenHandCursor)
                return

        self._svg_board.setCursor(Qt.CursorShape.ArrowCursor)

    def start_dragging(self, square: Square, piece: Piece, x: float, y: float) -> None:
        """Start dragging `piece` from `square` on `x` and `y`."""
        self._svg_board.is_dragging = True
        self._svg_board.origin_square = square
        self._svg_board.dragged_piece = piece
        self._svg_board.dragging_from_x = x
        self._svg_board.dragging_from_y = y
        self._svg_board.set_origin_square(square)
        self._svg_board.setCursor(Qt.CursorShape.ClosedHandCursor)

        self._svg_board.animatable_board = self._svg_board.board_copy()
        self._svg_board.animatable_board.set_piece_at(square, None)

        self._svg_board.update()

    def is_valid_move(self, target_square: Square) -> bool:
        """Verify whether `target_square` is valid for current piece."""
        legal_moves: list[Square] | None = self._svg_board._game.legal_moves
        return (
            0 <= target_square < ALL_SQUARES
            and target_square != self._svg_board.origin_square
            and legal_moves is not None
            and target_square in legal_moves
        )

    def make_move(self, target_square: Square) -> None:
        """Make move and update game state."""
        self._svg_board.set_target_square(target_square)
        self._svg_board.find_move(self._svg_board.origin_square, target_square)

        self.reset_dragging_state()
        self._svg_board.reset_selected_squares()
        self._svg_board.update()

    def reset_dragging_state(self) -> None:
        """Reset all dragging-related state attributes."""
        self._svg_board.is_dragging = False
        self._svg_board.origin_square = None
        self._svg_board.dragged_piece = None
        self._svg_board.dragging_from_x = None
        self._svg_board.dragging_from_y = None
        self._svg_board.animatable_board = None
        self._svg_board.setCursor(Qt.CursorShape.ArrowCursor)

    def cancel_move(self, x: float, y: float) -> None:
        """Animate piece returning to origin square for invalid move."""
        self._svg_board.is_dragging = False
        self._svg_board.setCursor(Qt.CursorShape.ArrowCursor)

        if self._svg_board.origin_square and self._svg_board.dragged_piece:
            self._svg_board._animator.start_return_animation(
                position=QPointF(x, y),
                origin_square=self._svg_board.origin_square,
                dragged_piece=self._svg_board.dragged_piece,
            )

    def handle_mouse_press(self, event: QMouseEvent) -> None:
        """Handle mouse press for piece selection or targeting."""
        if self._svg_board._animator.is_animating:
            return

        x: float = event.position().x()
        y: float = event.position().y()
        square_index: Square | None = self.square_index(x, y)

        if square_index:
            piece: Piece | None = self._svg_board.piece_at(square_index)

            if piece and self._svg_board.can_drag_piece(piece):
                self.start_dragging(square_index, piece, x, y)
                return

        self._svg_board.locate_square(x, y)

    def handle_mouse_move(self, event: QMouseEvent) -> None:
        """Update piece position during dragging or cursor shape."""
        if self._svg_board._animator.is_animating:
            return

        x: float = event.position().x()
        y: float = event.position().y()

        if self._svg_board.is_dragging:
            self._svg_board.dragging_from_x = x
            self._svg_board.dragging_from_y = y
            self._svg_board.update()
        else:
            self.update_cursor(x, y)

    def handle_mouse_release(self, event: QMouseEvent) -> None:
        """Process move or cancel piece dragging when mouse released."""
        if self._svg_board._animator.is_animating:
            return

        if not self._svg_board.origin_square:
            return

        if not self._svg_board.is_dragging:
            return

        x: float = event.position().x()
        y: float = event.position().y()
        square_index: Square | None = self.square_index(x, y)

        if square_index and self.is_valid_move(square_index):
            self.make_move(square_index)
        else:
            self.cancel_move(x, y)
