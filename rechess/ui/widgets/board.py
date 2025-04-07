from __future__ import annotations

from functools import lru_cache
from typing import Final, NamedTuple

from chess import svg, Move, Piece
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


ANIMATION_DURATION: Final[int] = 200
HALF_SQUARE: Final[float] = 35.0
SQUARE_CENTER_OFFSET: Final[float] = 55.0
SQUARE_SIZE: Final[float] = 70.0

svg.XX = "<circle id='xx' r='4.5' cx='22.5' cy='22.5' stroke='#303030' fill='#e5e5e5'/>"


class BoardCache(NamedTuple):
    """Type annotations for board cache."""

    fen: str
    dragging: bool
    animation: bool
    orientation: bool
    check: Square | None
    square: Square | None
    arrows: tuple[tuple[Square, Square]]


class SvgBoard(QSvgWidget):
    """Piece drag-and-drop functionality and animation on SVG board."""

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
        self._game.move_played.connect(self.on_move_played)

        self.is_dragging: bool = False
        self.is_animating: bool = False
        self.dragged_piece: Piece | None = None
        self.animated_piece: Piece | None = None
        self.origin_square: Square | None = None
        self.animation_board: Board | None = None
        self.cursor_point: QPointF = QPointF(0.0, 0.0)
        self.orientation: bool = setting_value("board", "orientation")

        self._coord: QColor = QColor()
        self._inner_border: QColor = QColor()
        self._margin: QColor = QColor()
        self._outer_border: QColor = QColor()
        self._square_dark: QColor = QColor()
        self._square_dark_lastmove: QColor = QColor()
        self._square_light: QColor = QColor()
        self._square_light_lastmove: QColor = QColor()

        self._animation: QPropertyAnimation = QPropertyAnimation(self, b"point")
        self._animation.setDuration(ANIMATION_DURATION)
        self._animation.setEasingCurve(QEasingCurve.Type.OutBack)
        self._animation.finished.connect(self.on_animation_finished)

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

    def board_cache(self) -> BoardCache:
        """Get cache of current board state."""
        return BoardCache(
            fen=self._game.fen,
            check=self._game.check,
            dragging=self.is_dragging,
            square=self.origin_square,
            animation=self.is_animating,
            orientation=self.orientation,
            arrows=tuple(self._game.arrow),
        )

    def set_cursor_point(self, value: QPointF) -> None:
        """Set cursor point based on `value`."""
        self.cursor_point = value

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

    def square_index(self, cursor_point: QPointF) -> Square:
        """Get square index based on `cursor_point`."""
        return self._game.square_index(cursor_point)

    def cursor_point_from(self, event: QMouseEvent) -> QPointF:
        """Get cursor point from position data of `event`."""
        self.cursor_point = event.position()
        return self.cursor_point

    def can_drag(self, piece: Piece | None) -> bool:
        """Return True if color of `piece` does not belong to engine."""
        return piece is not None and piece.color != setting_value("engine", "is_white")

    def is_legal(self, target_square: Square) -> bool:
        """Return True if `target_square` is legal for a piece."""
        legal_targets: list[Square] = self._game.legal_targets(self.origin_square)
        return target_square in legal_targets

    def update_cursor_shape_at(self, cursor_point: QPointF) -> None:
        """Update cursor shape at `cursor_point`."""
        square_index: Square = self.square_index(cursor_point)
        piece: Piece | None = self._game.piece_at(square_index)

        if self.is_dragging:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            return

        if piece is not None and self.can_drag(piece):
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            return

        self.setCursor(Qt.CursorShape.ArrowCursor)

    def start_dragging(self, square: Square, piece: Piece) -> None:
        """Start dragging `piece` from `square`."""
        self.is_dragging = True
        self.dragged_piece = piece
        self.origin_square = square
        self._game.origin_square = square

        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        self.update()

    def stop_dragging(self) -> None:
        """Stop piece dragging and reset dragging-related state."""
        self._game.reset_selected_squares()

        self.is_dragging = False
        self.is_animating = False
        self.dragged_piece = None
        self.origin_square = None
        self.animated_piece = None
        self.animation_board = None

        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()

    def drop_piece(self, target_square: Square) -> None:
        """Drop dragged piece onto `target_square`."""
        self._game.target_square = target_square
        self._game.find_legal_move(self.origin_square, target_square)

        self.stop_dragging()

    def return_piece_at(self, cursor_point: QPointF) -> None:
        """Return dragged piece at `cursor_point` to its origin square."""
        self.is_dragging = False

        if self.origin_square is not None and self.dragged_piece is not None:
            self.start_animation(
                cursor_point=cursor_point,
                origin_square=self.origin_square,
                dragged_piece=self.dragged_piece,
            )

        self.setCursor(Qt.CursorShape.ArrowCursor)

    def start_animation(
        self,
        cursor_point: QPointF,
        origin_square: Square,
        dragged_piece: Piece,
    ) -> None:
        """Animate returning `dragged_piece` to its `origin_square`."""
        self.is_animating = True
        self.animated_piece = dragged_piece
        self.origin_square = origin_square

        self._animation.setStartValue(cursor_point)
        self._animation.setEndValue(self.square_center(origin_square))
        self._animation.start()

    @lru_cache(maxsize=128)
    def svg_data(self, cache: BoardCache) -> bytes:
        """Transform current board state into SVG data as bytes."""
        board_to_render: Board = self._game.board

        if cache.square is not None and cache.dragging or cache.animation:
            square: Square | None = (
                cache.square if cache.dragging else self.origin_square
            )
            board_to_render = board_to_render.copy()
            board_to_render.set_piece_at(square=square, piece=None)

        cached_square: Square | None = cache.square if cache.dragging else None
        legal_targets: list[Square] = self._game.legal_targets(cached_square)

        svg_board: str = svg.board(
            check=cache.check,
            arrows=cache.arrows,
            board=board_to_render,
            squares=legal_targets,
            colors=self.color_names(),
            orientation=cache.orientation,
        )
        return svg_board.encode()

    @lru_cache(maxsize=12)
    def svg_renderer(self, piece_symbol: str) -> QSvgRenderer:
        """Get or create piece SVG renderer based on `piece_symbol`."""
        svg_piece: str = svg.piece(Piece.from_symbol(piece_symbol))
        renderer: QSvgRenderer = QSvgRenderer()
        renderer.load(svg_piece.encode())
        return renderer

    def piece_render_area_at(self, cursor_point: QPointF) -> QRectF:
        """Get piece render area based on `cursor_point`."""
        return QRectF(
            cursor_point.x() - HALF_SQUARE,
            cursor_point.y() - HALF_SQUARE,
            SQUARE_SIZE,
            SQUARE_SIZE,
        )

    def render_piece(
        self,
        cursor_point: QPointF,
        piece: Piece | None = None,
    ) -> None:
        """Render `piece` at `cursor_point`."""
        dragged_piece: Piece | None = self.dragged_piece or None
        piece_to_render: Piece | None = dragged_piece or piece

        if piece_to_render is None:
            return

        painter: QPainter = QPainter(self)
        piece_symbol: str = piece_to_render.symbol()
        renderer: QSvgRenderer = self.svg_renderer(piece_symbol)
        piece_render_area: QRectF = self.piece_render_area_at(cursor_point)
        renderer.render(painter, piece_render_area)
        painter.end()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Render board and piece to animate."""
        board_svg: bytes = self.svg_data(self.board_cache())
        self.load(board_svg)
        super().paintEvent(event)

        if self.is_dragging and self.dragged_piece is not None:
            current_piece: Piece = self._game.piece_at(self.origin_square)

            if current_piece.color != self.dragged_piece.color:
                self.stop_dragging()
            else:
                self.render_piece(self.cursor_point)

        if self.is_animating:
            self.render_piece(self.cursor_point, self.animated_piece)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press for piece selection or targeting."""
        cursor_point: QPointF = self.cursor_point_from(event)
        square_index: Square = self.square_index(cursor_point)
        piece: Piece | None = self._game.piece_at(square_index)

        if piece is not None and self.can_drag(piece):
            self.start_dragging(square_index, piece)
        else:
            self._game.select_square_at(cursor_point)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Update cursor shape when hovering over board."""
        cursor_point: QPointF = self.cursor_point_from(event)
        self.update_cursor_shape_at(cursor_point)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Make move with dragging piece or return it back."""
        self.release_event: QMouseEvent = event

        cursor_point: QPointF = self.cursor_point_from(event)
        square_index: Square = self.square_index(cursor_point)

        if self.is_legal(square_index):
            self.drop_piece(square_index)
        else:
            self.return_piece_at(cursor_point)

    @Slot()
    def on_animation_finished(self) -> None:
        """Reset board state after animation has finished."""
        self.stop_dragging()

    @Slot(Move)
    def on_move_played(self, move: Move) -> None:
        """Update board state and clear cached SVG data."""
        self.orientation = setting_value("board", "orientation")

        self.svg_data.cache_clear()
        self.svg_renderer.cache_clear()

        self.update()
