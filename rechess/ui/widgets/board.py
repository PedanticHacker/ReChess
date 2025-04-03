from __future__ import annotations

from functools import lru_cache
from typing import Final, NamedTuple

from chess import svg, Piece
from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPointF,
    QPropertyAnimation,
    QRectF,
    Qt,
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


class BoardCache(NamedTuple):
    """Type annotations for board cache."""

    fen: str
    animation: bool
    orientation: bool
    check: Square | None
    square: Square | None
    arrows: tuple[tuple[Square, Square]]


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

    point: Property = Property(
        QPointF,
        lambda self: self.cursor_point,
        lambda self, value: self.set_cursor_point(value),
    )

    def __init__(self, game: Game) -> None:
        super().__init__()

        self._game: Game = game
        self._game.move_played.connect(self.clear_cache)

        self._coord: QColor = QColor()
        self._inner_border: QColor = QColor()
        self._margin: QColor = QColor()
        self._outer_border: QColor = QColor()
        self._square_dark: QColor = QColor()
        self._square_dark_lastmove: QColor = QColor()
        self._square_light: QColor = QColor()
        self._square_light_lastmove: QColor = QColor()

        self.is_dragging: bool = False
        self.dragged_piece: Piece | None = None
        self.origin_square: Square | None = None
        self.dragging_from_x: float | None = None
        self.dragging_from_y: float | None = None

        self.is_animating: bool = False
        self.animated_piece: Piece | None = None
        self.animation_origin_square: Square | None = None
        self.cursor_point: QPointF = QPointF(0.0, 0.0)

        self._animation: QPropertyAnimation = QPropertyAnimation(self, b"point")
        self._animation.setDuration(ANIMATION_DURATION)
        self._animation.setEasingCurve(QEasingCurve.Type.OutBack)
        self._animation.finished.connect(self.on_animation_finished)

        self._last_cursor_point: QPointF = QPointF(0.0, 0.0)
        self._last_square_index: Square | None = None

        self.animation_board: Board | None = None
        self.orientation: bool = setting_value("board", "orientation")

        self.setMouseTracking(True)

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
        self.svg_data.cache_clear()
        self.svg_renderer.cache_clear()
        self.update()

    def piece_origin_square(self) -> Square | None:
        """Get origin square of dragged or animated piece."""
        return self.origin_square if self.is_dragging or self.is_animating else None

    def board_cache(self) -> BoardCache:
        """Get board cache."""
        return BoardCache(
            fen=self._game.fen,
            check=self._game.check,
            animation=self.is_animating,
            orientation=self.orientation,
            arrows=tuple(self._game.arrow),
            square=self.piece_origin_square(),
        )

    def square_center(self, square: Square) -> QPointF:
        """Get center point of `square`."""
        file: int = square % 8
        rank: int = square // 8

        if self.orientation:
            flipped_rank: int = 7 - rank
            x: float = SQUARE_CENTER_OFFSET + (SQUARE_SIZE * file)
            y: float = SQUARE_CENTER_OFFSET + (SQUARE_SIZE * flipped_rank)
        else:
            flipped_file: int = 7 - file
            x = SQUARE_CENTER_OFFSET + (SQUARE_SIZE * flipped_file)
            y = SQUARE_CENTER_OFFSET + (SQUARE_SIZE * rank)

        return QPointF(x, y)

    def dragging_position(self) -> QPointF:
        """Get current position for dragged piece."""
        return QPointF(self.dragging_from_x, self.dragging_from_y)

    def update_dragging_position(self, position: QPointF | None = None) -> None:
        """Update position for dragged piece."""
        if position is None:
            self.dragging_from_x = None
            self.dragging_from_y = None
        else:
            self.dragging_from_x = position.x()
            self.dragging_from_y = position.y()
        self.update()

    def can_drag_piece(self, piece: Piece | None) -> bool:
        """Return True if `piece` with specific color can be dragged."""
        return bool(piece and piece.color != setting_value("engine", "is_white"))

    def set_cursor_point(self, value: QPointF) -> None:
        """Set cursor point based on `value` and update board."""
        self.cursor_point = value
        self.update()

    def start_animation(
        self,
        cursor_point: QPointF,
        origin_square: Square,
        dragged_piece: Piece,
    ) -> None:
        """Animate returning `dragged_piece` to `origin_square`."""
        self.is_animating = True
        self.animated_piece = dragged_piece
        self.animation_origin_square = origin_square

        self._animation.setStartValue(cursor_point)
        self._animation.setEndValue(self.square_center(origin_square))
        self._animation.start()

    def animate_returning_piece_at(self, cursor_point: QPointF) -> None:
        """Animate returning dragged piece to origin square."""
        if self.origin_square and self.dragged_piece:
            self.start_animation(
                cursor_point=cursor_point,
                origin_square=self.origin_square,
                dragged_piece=self.dragged_piece,
            )

    @lru_cache(maxsize=128)
    def svg_data(self, cache: BoardCache) -> bytes:
        """Transform current board state into SVG data."""
        svg_board: str = svg.board(
            check=cache.check,
            arrows=cache.arrows,
            colors=self.color_names(),
            orientation=cache.orientation,
            squares=self._game.legal_targets,
            board=self.animation_board or self._game.board,
        )
        return svg_board.encode()

    @lru_cache(maxsize=12)
    def svg_renderer(self, piece_symbol: str) -> QSvgRenderer:
        """Get or create piece SVG renderer based on `piece_symbol`."""
        svg_piece: str = svg.piece(Piece.from_symbol(piece_symbol))
        renderer: QSvgRenderer = QSvgRenderer()
        renderer.load(svg_piece.encode())
        return renderer

    def piece_render_area(self, cursor_point: QPointF) -> QRectF:
        """Get piece render area based on `cursor_point`."""
        return QRectF(
            cursor_point.x() - HALF_SQUARE,
            cursor_point.y() - HALF_SQUARE,
            SQUARE_SIZE,
            SQUARE_SIZE,
        )

    def render_piece(self, cursor_point: QPointF, piece: Piece | None = None) -> None:
        """Render `piece` at `cursor_point`."""
        dragged_piece: Piece | None = self.dragged_piece or None
        piece_to_render: Piece | None = dragged_piece or piece

        if piece_to_render is None:
            return

        painter: QPainter = QPainter(self)
        piece_symbol: str = piece_to_render.symbol()
        renderer: QSvgRenderer = self.svg_renderer(piece_symbol)
        piece_render_area: QRectF = self.piece_render_area(cursor_point)
        renderer.render(painter, piece_render_area)
        painter.end()

    def square_index(self, cursor_point: QPointF) -> Square | None:
        """Get square index based on `cursor_point`."""
        if self._last_cursor_point == cursor_point and self._last_square_index:
            return self._last_square_index

        square_index: Square = self._game.square_index(cursor_point)

        self._last_cursor_point = cursor_point
        self._last_square_index = square_index
        return square_index

    def change_cursor_shape_at(self, cursor_point: QPointF) -> None:
        """Change cursor shape at `cursor_point`."""
        square_index: Square | None = self.square_index(cursor_point)

        if square_index:
            piece: Piece | None = self._game.piece_at(square_index)

            if self.can_drag_piece(piece):
                self.setCursor(Qt.CursorShape.OpenHandCursor)
                return

        self.setCursor(Qt.CursorShape.ArrowCursor)

    def start_dragging(
        self,
        square: Square,
        piece: Piece,
        cursor_point: QPointF,
    ) -> None:
        """Start dragging `piece` on `square` from `cursor_point`."""
        self.is_dragging = True
        self.dragged_piece = piece
        self.origin_square = square
        self._game.origin_square = square
        self.update_dragging_position(cursor_point)
        self.setCursor(Qt.CursorShape.ClosedHandCursor)

        self.animation_board = self._game.board.copy()
        self.animation_board.set_piece_at(square=square, piece=None)

        self.update()

    def is_valid(self, target_square: Square) -> bool:
        """Return True if `target_square` is valid."""
        return target_square in self._game.legal_targets

    def move_piece_to(self, target_square: Square) -> None:
        """Move dragged piece to `target_square`."""
        self._game.target_square = target_square
        self._game.find_legal_move(self.origin_square, target_square)
        self._game.reset_selected_squares()

        self.reset_dragging_state()
        self.update()

    def reset_dragging_state(self) -> None:
        """Reset all dragging-related state attributes."""
        self.is_dragging = False
        self.dragged_piece = None
        self.origin_square = None
        self.animation_board = None
        self.update_dragging_position()
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def return_piece_to_origin_square_from(self, cursor_point: QPointF) -> None:
        """Animate returning piece to origin square."""
        self.is_dragging = False
        self.animate_returning_piece_at(cursor_point)
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def cursor_point_from(self, event: QMouseEvent) -> QPointF:
        """Get cursor point based on `event`."""
        self.cursor_point = QPointF(event.position().x(), event.position().y())
        return self.cursor_point

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press for piece selection or targeting."""
        if self.is_animating:
            return

        cursor_point: QPointF = self.cursor_point_from(event)
        square_index: Square | None = self.square_index(cursor_point)

        if square_index:
            piece: Piece | None = self._game.piece_at(square_index)

            if piece and self.can_drag_piece(piece):
                self.start_dragging(square_index, piece, cursor_point)
                return

        self._game.select_square(cursor_point)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Update piece position during dragging or cursor shape."""
        if self.is_animating:
            return

        cursor_point: QPointF = self.cursor_point_from(event)

        if self.is_dragging:
            self.update_dragging_position(cursor_point)
        else:
            self.change_cursor_shape_at(cursor_point)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Process move or cancel piece dragging when mouse released."""
        if not self.is_dragging or self.is_animating:
            return

        cursor_point: QPointF = self.cursor_point_from(event)
        square_index: Square | None = self.square_index(cursor_point)

        if self.is_valid(square_index):
            self.move_piece_to(square_index)
        else:
            self.return_piece_to_origin_square_from(cursor_point)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Render board and piece to animate."""
        board_svg: bytes = self.svg_data(self.board_cache())
        self.load(board_svg)
        super().paintEvent(event)

        if self.is_dragging:
            self.render_piece(self.dragging_position())
        elif self.is_animating:
            self.render_piece(self.cursor_point, self.animated_piece)

    @Slot()
    def clear_cache(self) -> None:
        """Update board orientation and clear cached SVG data."""
        self.orientation = setting_value("board", "orientation")

        self.svg_data.cache_clear()
        self.svg_renderer.cache_clear()

        self.update()

    @Slot()
    def on_animation_finished(self) -> None:
        """Reset board state after animation has finished."""
        self.is_animating = False
        self.origin_square = None
        self.dragged_piece = None
        self.animation_board = None

        self._game.reset_selected_squares()

        self.update()
