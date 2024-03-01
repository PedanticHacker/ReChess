from chess import Color, PieceType
from chess import BISHOP, KNIGHT, QUEEN, ROOK, WHITE
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QHBoxLayout

from rechess import create_button, get_svg_icon


class PromotionDialog(QDialog):
    """A dialog for selecting a promotion piece."""

    def __init__(self, player_color: Color) -> None:
        super().__init__()

        self.player_color: Color = player_color
        self._piece_type: PieceType = PieceType()

        self.set_title()
        self.set_layout()
        self.create_buttons()
        self.add_buttons_to_box()
        self.connect_events_with_handlers()

        self.exec()

    def set_title(self) -> None:
        self.setWindowTitle("Pawn Promotion")

    def set_layout(self) -> None:
        self.button_box = QDialogButtonBox()
        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.addWidget(self.button_box)
        self.setLayout(self.horizontal_layout)

    def create_buttons(self) -> None:
        if self.player_color == WHITE:
            self.queen_button = create_button(get_svg_icon("white-queen"))
            self.rook_button = create_button(get_svg_icon("white-rook"))
            self.bishop_button = create_button(get_svg_icon("white-bishop"))
            self.knight_button = create_button(get_svg_icon("white-knight"))
        else:
            self.queen_button = create_button(get_svg_icon("black-queen"))
            self.rook_button = create_button(get_svg_icon("black-rook"))
            self.bishop_button = create_button(get_svg_icon("black-bishop"))
            self.knight_button = create_button(get_svg_icon("black-knight"))

    def add_buttons_to_box(self) -> None:
        self.button_box.addButton(
            self.queen_button,
            QDialogButtonBox.ButtonRole.AcceptRole,
        )
        self.button_box.addButton(
            self.rook_button,
            QDialogButtonBox.ButtonRole.AcceptRole,
        )
        self.button_box.addButton(
            self.bishop_button,
            QDialogButtonBox.ButtonRole.AcceptRole,
        )
        self.button_box.addButton(
            self.knight_button,
            QDialogButtonBox.ButtonRole.AcceptRole,
        )

    def connect_events_with_handlers(self) -> None:
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.queen_button.clicked.connect(self.on_queen_button_clicked)
        self.rook_button.clicked.connect(self.on_rook_button_clicked)
        self.bishop_button.clicked.connect(self.on_bishop_button_clicked)
        self.knight_button.clicked.connect(self.on_knight_button_clicked)

    def on_queen_button_clicked(self) -> None:
        self._piece_type = QUEEN

    def on_rook_button_clicked(self) -> None:
        self._piece_type = ROOK

    def on_bishop_button_clicked(self) -> None:
        self._piece_type = BISHOP

    def on_knight_button_clicked(self) -> None:
        self._piece_type = KNIGHT

    @property
    def piece_type(self) -> PieceType:
        return self._piece_type
