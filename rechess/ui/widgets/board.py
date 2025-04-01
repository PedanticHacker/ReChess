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

    fen: str
    animation: bool
    orientation: bool
    piece_square: Square | None
    checked_king_square: Square | None
    arrows: tuple[tuple[Square, Square]] | None


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

        self.animatable_board: Board | None = None
        self.is_white_at_bottom: bool = setting_value("board", "orientation")

        self._renderer: BoardRenderer = BoardRenderer(self)
        self._interactor: BoardInteractor = BoardInteractor(self)
        self._animator: PieceAnimator = PieceAnimator(self)
        self._animator.animation_completed.connect(self.on_animation_completed)

        self.setMouseTracking(True)

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
        self.dragged_piece: Piece | None = None
        self.origin_square: Square | None = None
        self.dragging_from_x: float | None = None
        self.dragging_from_y: float | None = None

    def color_names(self) -> dict[str, str]:
        """Get color names for SVG rendering."""
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

    def update_color(self, property_name: str, color_value: QColor) -> None:
        """Update color based on `property_name` and `color_value`."""
        setattr(self, property_name, color_value)
        self._renderer.clear_cache()
        self.update()

    def drag_origin_square(self) -> Square | None:
        """Get origin square of dragged piece."""
        return (
            self.origin_square
            if self.is_dragging or self._animator.is_animating
            else None
        )

    def cache_key(self) -> BoardCacheKey:
        """Generate unique key for board state."""
        return BoardCacheKey(
            fen=self._game.fen,
            arrows=tuple(self._game.arrow),
            orientation=self.is_white_at_bottom,
            animation=self._animator.is_animating,
            piece_square=self.drag_origin_square(),
            checked_king_square=self._game.checked_king_square,
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
        return self._game.piece_at(square)

    def set_origin_square(self, square: Square) -> None:
        """Set `square` as origin for move."""
        self._game.origin_square = square

    def set_target_square(self, square: Square) -> None:
        """Set `square` as target for move."""
        self._game.target_square = square

    def legal_targets(self) -> list[Square] | None:
        """Get target squares considered as legal moves for piece."""
        return self._game.legal_targets

    def start_piece_return_animation(self, cursor_point: QPointF) -> None:
        """Start animation to return dragged piece to origin square."""
        if self.origin_square and self.dragged_piece:
            self._animator.start_return_animation(
                cursor_point=cursor_point,
                origin_square=self.origin_square,
                dragged_piece=self.dragged_piece,
            )

    def find_legal_move(self, origin_square: Square, target_square: Square) -> None:
        """Find legal move for `origin_square` and `target_square`."""
        self._game.find_legal_move(origin_square, target_square)

    def reset_selected_squares(self) -> None:
        """Reset currently selected origin and target squares."""
        self._game.reset_selected_squares()

    def selection_point(self, cursor_point: QPointF) -> QPoint:
        """Get selection point based on `cursor_point`."""
        return self._game.selection_point(cursor_point)

    def select_square(self, cursor_point: QPointF) -> None:
        """Select square based on `cursor_point`."""
        self._game.select_square(cursor_point)

    def game_state(self) -> Board:
        """Get current game state."""
        return self._game.board

    def game_state_clone(self) -> Board:
        """Get clone of current game state."""
        return self._game.board.copy()

    def can_drag_piece(self, piece: Piece | None) -> bool:
        """Return True if `piece` can be dragged based on turn."""
        return bool(piece and piece.color != setting_value("engine", "is_white"))

    def is_animation_in_progress(self) -> bool:
        """Return True if animation is currently in progress."""
        return self._animator.is_animating

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
        """Render board and piece to animate."""
        board_svg: bytes = self._renderer.svg_data(self.cache_key())
        self.load(board_svg)
        super().paintEvent(event)

        if (
            self.piece_can_be_dragged()
            and self.dragging_from_x
            and self.dragging_from_y
        ):
            cursor_point: QPointF = QPointF(self.dragging_from_x, self.dragging_from_y)
            self._renderer.render_piece(cursor_point)
        elif self._animator.is_animating:
            cursor_point = self._animator.cursor_point
            piece_to_animate: Piece | None = self._animator.dragged_piece

            if cursor_point and piece_to_animate:
                self._renderer.render_piece(
                    cursor_point,
                    piece_to_animate,
                )

    @Slot()
    def clear_cache(self) -> None:
        """Update board orientation and clear cached SVG data."""
        self.is_white_at_bottom = setting_value("board", "orientation")

        self._renderer.clear_cache()
        self.update()

    @Slot()
    def on_animation_completed(self) -> None:
        """Clean up board state after animation completes."""
        self.origin_square = None
        self.dragged_piece = None
        self.animatable_board = None

        self.reset_selected_squares()
        self.update()


class PieceAnimator(QObject):
    """Management for piece drag-and-drop animation on board."""

    animation_completed: ClassVar[Signal] = Signal()

    point: Property = Property(
        QPointF,
        lambda self: self.cursor_point,
        lambda self, value: self.set_cursor_point(value),
    )

    def __init__(self, board: SvgBoard) -> None:
        super().__init__(board)

        self._svg_board: SvgBoard = board

        self.is_animating: bool = False
        self.dragged_piece: Piece | None = None
        self.origin_square: Square | None = None
        self.cursor_point: QPointF = QPointF(0.0, 0.0)

        self._animation: QPropertyAnimation = QPropertyAnimation(self, b"point")
        self._animation.setDuration(ANIMATION_DURATION)
        self._animation.setEasingCurve(QEasingCurve.Type.OutBack)
        self._animation.finished.connect(self.end_animation)

    def set_cursor_point(self, value: QPointF) -> None:
        """Set cursor point based on `value` and then update board."""
        self.cursor_point = value
        self._svg_board.update()

    def start_return_animation(
        self,
        cursor_point: QPointF,
        origin_square: Square,
        dragged_piece: Piece,
    ) -> None:
        """Start animation to return piece to origin square."""
        self.is_animating = True
        self.dragged_piece = dragged_piece
        self.origin_square = origin_square

        self._animation.setStartValue(cursor_point)
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

    def is_dragging_with_animatable_board(self) -> bool:
        """Return True if piece dragged and animatable board exists."""
        return bool(self._svg_board.is_dragging and self._svg_board.animatable_board)

    def is_piece_animating(self) -> bool:
        """Return True if piece animation is currently in progress."""
        return self._svg_board.is_animation_in_progress()

    def board_to_render(self) -> Board:
        """Get board to be used for rendering."""
        if self.is_dragging_with_animatable_board() or self.is_piece_animating():
            return self._svg_board.animatable_board
        return self._svg_board.game_state()

    def color_names(self) -> dict[str, str]:
        """Get color names for SVG rendering."""
        return self._svg_board.color_names()

    @lru_cache(maxsize=128)
    def svg_data(self, cache_key: BoardCacheKey) -> bytes:
        """Transform current board state into SVG data."""
        svg_board: str = svg.board(
            arrows=cache_key.arrows,
            colors=self.color_names(),
            board=self.board_to_render(),
            orientation=cache_key.orientation,
            check=cache_key.checked_king_square,
            squares=self._svg_board.legal_targets(),
        )
        return svg_board.encode()

    @lru_cache(maxsize=12)
    def svg_renderer(self, piece_symbol: str) -> QSvgRenderer:
        """Get or create piece SVG renderer based on `piece_symbol`."""
        svg_piece: str = svg.piece(Piece.from_symbol(piece_symbol))
        renderer: QSvgRenderer = QSvgRenderer()
        renderer.load(svg_piece.encode())
        return renderer

    def render_piece(
        self, cursor_point: QPointF, selected_piece: Piece | None = None
    ) -> None:
        """Render `piece` at `x` and `y` coordinates."""
        dragged_piece: Piece | None = (
            self._svg_board.dragged_piece if self._svg_board.is_dragging else None
        )
        piece_to_render: Piece | None = selected_piece or dragged_piece

        if not piece_to_render:
            return

        painter: QPainter = QPainter(self._svg_board)
        piece_symbol: str = piece_to_render.symbol()
        renderer: QSvgRenderer = self.svg_renderer(piece_symbol)

        piece_render_area: QRectF = QRectF(
            cursor_point.x() - HALF_SQUARE,
            cursor_point.y() - HALF_SQUARE,
            SQUARE_SIZE,
            SQUARE_SIZE,
        )

        renderer.render(painter, piece_render_area)
        painter.end()

    def clear_cache(self) -> None:
        """Clear cached SVG data."""
        self.svg_data.cache_clear()
        self.svg_renderer.cache_clear()


class BoardInteractor:
    """Management for interacting with pieces on board."""

    def __init__(self, board: SvgBoard) -> None:
        self._svg_board: SvgBoard = board

        self._last_cursor_point: QPointF = QPointF(0.0, 0.0)
        self._last_square_index: Square | None = None

    def square_index(self, cursor_point: QPointF) -> Square | None:
        """Get square index based on `cursor_point`."""
        if self._last_cursor_point == cursor_point and self._last_square_index:
            return self._last_square_index

        selection_point = self._svg_board.selection_point(cursor_point)
        square_index: Square = selection_point.x() + selection_point.y() * 8
        valid_square_index: Square | None = (
            square_index if square_index < ALL_SQUARES else None
        )

        self._last_cursor_point = cursor_point
        self._last_square_index = valid_square_index
        return valid_square_index

    def change_cursor_shape(self, cursor_point: QPointF) -> None:
        """Change cursor shape based on `cursor_point`."""
        square_index: Square | None = self.square_index(cursor_point)

        if square_index:
            piece: Piece | None = self._svg_board.piece_at(square_index)

            if self._svg_board.can_drag_piece(piece):
                self._svg_board.setCursor(Qt.CursorShape.OpenHandCursor)
                return

        self._svg_board.setCursor(Qt.CursorShape.ArrowCursor)

    def start_dragging(
        self,
        square: Square,
        piece: Piece,
        cursor_point: QPointF,
    ) -> None:
        """Start dragging `piece` on `square` from `cursor_point`."""
        self._svg_board.is_dragging = True
        self._svg_board.origin_square = square
        self._svg_board.dragged_piece = piece
        self._svg_board.dragging_from_x = cursor_point.x()
        self._svg_board.dragging_from_y = cursor_point.y()
        self._svg_board.set_origin_square(square)
        self._svg_board.setCursor(Qt.CursorShape.ClosedHandCursor)

        self._svg_board.animatable_board = self._svg_board.game_state_clone()
        self._svg_board.animatable_board.set_piece_at(square, None)

        self._svg_board.update()

    def is_valid_move(self, target_square: Square) -> bool:
        """Verify whether `target_square` is valid for current piece."""
        legal_targets: list[Square] | None = self._svg_board.legal_targets()

        return (
            0 <= target_square < ALL_SQUARES
            and target_square != self._svg_board.origin_square
            and legal_targets is not None
            and target_square in legal_targets
        )

    def make_move(self, target_square: Square) -> None:
        """Make move and update game state."""
        self._svg_board.set_target_square(target_square)
        self._svg_board.find_legal_move(self._svg_board.origin_square, target_square)
        self._svg_board.reset_selected_squares()
        self._svg_board.update()

        self.reset_dragging_state()

    def reset_dragging_state(self) -> None:
        """Reset all dragging-related state attributes."""
        self._svg_board.is_dragging = False
        self._svg_board.origin_square = None
        self._svg_board.dragged_piece = None
        self._svg_board.dragging_from_x = None
        self._svg_board.dragging_from_y = None
        self._svg_board.animatable_board = None
        self._svg_board.setCursor(Qt.CursorShape.ArrowCursor)

    def cancel_move(self, cursor_point: QPointF) -> None:
        """Animate piece returning to origin square for invalid move."""
        self._svg_board.is_dragging = False
        self._svg_board.setCursor(Qt.CursorShape.ArrowCursor)
        self._svg_board.start_piece_return_animation(cursor_point)

    def handle_mouse_press(self, event: QMouseEvent) -> None:
        """Handle mouse press for piece selection or targeting."""
        if self._svg_board.is_animation_in_progress():
            return

        cursor_point: QPointF = QPointF(event.position().x(), event.position().y())
        square_index: Square | None = self.square_index(cursor_point)

        if square_index:
            piece: Piece | None = self._svg_board.piece_at(square_index)

            if piece and self._svg_board.can_drag_piece(piece):
                self.start_dragging(square_index, piece, cursor_point)
                return

        self._svg_board.select_square(cursor_point)

    def handle_mouse_move(self, event: QMouseEvent) -> None:
        """Update piece position during dragging or cursor shape."""
        if self._svg_board.is_animation_in_progress():
            return

        cursor_point: QPointF = QPointF(event.position().x(), event.position().y())

        if self._svg_board.is_dragging:
            self._svg_board.dragging_from_x = cursor_point.x()
            self._svg_board.dragging_from_y = cursor_point.y()
            self._svg_board.update()
        else:
            self.change_cursor_shape(cursor_point)

    def handle_mouse_release(self, event: QMouseEvent) -> None:
        """Process move or cancel piece dragging when mouse released."""
        if not self._svg_board.is_dragging:
            return

        if self._svg_board.is_animation_in_progress():
            return

        cursor_point: QPointF = QPointF(event.position().x(), event.position().y())
        square_index: Square | None = self.square_index(cursor_point)

        if square_index and self.is_valid_move(square_index):
            self.make_move(square_index)
        else:
            self.cancel_move(cursor_point)
