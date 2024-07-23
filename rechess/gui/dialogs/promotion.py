from chess import BISHOP, Color, KNIGHT, PieceType, QUEEN, ROOK, WHITE
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QHBoxLayout

from rechess.utils import create_button, svg_icon


class PromotionDialog(QDialog):
    """Dialog for selecting a pawn promotion piece."""

    def __init__(self, player_color: Color) -> None:
        super().__init__()

        self._player_color: Color = player_color
        self._piece: PieceType = PieceType()

        self.set_title()
        self.create_buttons()
        self.add_buttons_to_box()
        self.set_horizontal_layout()
        self.connect_signals_to_slots()

    def set_title(self) -> None:
        """Set the dialog's title to be Pawn Promotion."""
        self.setWindowTitle("Pawn Promotion")

    def create_buttons(self) -> None:
        """Create buttons for each promotion piece option."""
        if self._player_color == WHITE:
            self.queen_button = create_button(svg_icon("white-queen"))
            self.rook_button = create_button(svg_icon("white-rook"))
            self.bishop_button = create_button(svg_icon("white-bishop"))
            self.knight_button = create_button(svg_icon("white-knight"))
        else:
            self.queen_button = create_button(svg_icon("black-queen"))
            self.rook_button = create_button(svg_icon("black-rook"))
            self.bishop_button = create_button(svg_icon("black-bishop"))
            self.knight_button = create_button(svg_icon("black-knight"))

    def add_buttons_to_box(self) -> None:
        """Add promotion buttons to a button box."""
        self.button_box: QDialogButtonBox = QDialogButtonBox(self)

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

    def set_horizontal_layout(self) -> None:
        """Set horizontal layout for the promotion buttons."""
        horizontal_layout: QHBoxLayout = QHBoxLayout(self)
        horizontal_layout.addWidget(self.button_box)
        self.setLayout(horizontal_layout)

    def connect_signals_to_slots(self) -> None:
        """Connect button signals to their respective slot methods."""
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.queen_button.clicked.connect(self.on_queen_button_clicked)
        self.rook_button.clicked.connect(self.on_rook_button_clicked)
        self.bishop_button.clicked.connect(self.on_bishop_button_clicked)
        self.knight_button.clicked.connect(self.on_knight_button_clicked)

    def on_queen_button_clicked(self) -> None:
        """Set a queen to replace the promoting pawn."""
        self._piece = QUEEN

    def on_rook_button_clicked(self) -> None:
        """Set a rook to replace the promoting pawn."""
        self._piece = ROOK

    def on_bishop_button_clicked(self) -> None:
        """Set a bishop to replace the promoting pawn."""
        self._piece = BISHOP

    def on_knight_button_clicked(self) -> None:
        """Set a knight to replace the promoting pawn."""
        self._piece = KNIGHT

    @property
    def piece(self) -> PieceType:
        """Return the selected promotion piece."""
        return self._piece
