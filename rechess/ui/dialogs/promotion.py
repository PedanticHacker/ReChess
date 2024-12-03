from chess import BISHOP, KNIGHT, QUEEN, ROOK, WHITE, Color, PieceType
from PySide6.QtWidgets import QDialog, QHBoxLayout

from rechess.utils import create_button, svg_icon


class PromotionDialog(QDialog):
    """Dialog with buttons for selecting pawn promotion piece type."""

    def __init__(self, piece_color: Color) -> None:
        super().__init__()

        self._piece_color: Color = piece_color
        self._piece_type: PieceType = PieceType()

        self.set_title()
        self.create_buttons()
        self.set_horizontal_layout()
        self.connect_signals_to_slots()

    def set_title(self) -> None:
        """Set dialog's window title to be Pawn Promotion."""
        self.setWindowTitle("Pawn Promotion")

    def create_buttons(self) -> None:
        """Create buttons based on piece color showing piece type."""
        if self._piece_color == WHITE:
            self.queen_button = create_button(svg_icon("white-queen"))
            self.rook_button = create_button(svg_icon("white-rook"))
            self.bishop_button = create_button(svg_icon("white-bishop"))
            self.knight_button = create_button(svg_icon("white-knight"))
        else:
            self.queen_button = create_button(svg_icon("black-queen"))
            self.rook_button = create_button(svg_icon("black-rook"))
            self.bishop_button = create_button(svg_icon("black-bishop"))
            self.knight_button = create_button(svg_icon("black-knight"))

    def set_horizontal_layout(self) -> None:
        """Add buttons to horizontal layout."""
        horizontal_layout: QHBoxLayout = QHBoxLayout()
        horizontal_layout.addWidget(self.queen_button)
        horizontal_layout.addWidget(self.rook_button)
        horizontal_layout.addWidget(self.bishop_button)
        horizontal_layout.addWidget(self.knight_button)

        self.setLayout(horizontal_layout)

    def connect_signals_to_slots(self) -> None:
        """Connect button signals to corresponding slot methods."""
        self.queen_button.clicked.connect(self.on_queen_button_clicked)
        self.rook_button.clicked.connect(self.on_rook_button_clicked)
        self.bishop_button.clicked.connect(self.on_bishop_button_clicked)
        self.knight_button.clicked.connect(self.on_knight_button_clicked)

    def on_queen_button_clicked(self) -> None:
        """Set piece type to queen."""
        self._piece_type = QUEEN
        self.accept()

    def on_rook_button_clicked(self) -> None:
        """Set piece type to rook."""
        self._piece_type = ROOK
        self.accept()

    def on_bishop_button_clicked(self) -> None:
        """Set piece type to bishop."""
        self._piece_type = BISHOP
        self.accept()

    def on_knight_button_clicked(self) -> None:
        """Set piece type to knight."""
        self._piece_type = KNIGHT
        self.accept()

    @property
    def piece_type(self) -> PieceType:
        """Return selected piece type."""
        return self._piece_type
