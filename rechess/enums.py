from enum import EnumDict, StrEnum

from PySide6.QtCore import QUrl


class ClockColor(StrEnum):
    """CSS color style enum for clocks of Black and White players."""

    Black = "color: white; background-color: black;"
    White = "color: black; background-color: white;"


class SoundEffectUrl(EnumDict):
    """File URL enum for sound effects of various move types."""

    Capture = QUrl("file:rechess/assets/audio/capture.wav")
    Castling = QUrl("file:rechess/assets/audio/castling.wav")
    Check = QUrl("file:rechess/assets/audio/check.wav")
    GameOver = QUrl("file:rechess/assets/audio/game-over.wav")
    Move = QUrl("file:rechess/assets/audio/move.wav")
    Promotion = QUrl("file:rechess/assets/audio/promotion.wav")
