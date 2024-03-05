from chess import Move
from PySide6.QtCore import QObject, Signal


class Signals(QObject):
    """Custom PySide6 signals."""
    move_played: Signal = Signal(Move)
