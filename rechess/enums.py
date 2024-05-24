from enum import StrEnum


class ClockColor(StrEnum):
    """Black player's clock color and White players's clock color."""

    Black: str = "color: white; background: black;"
    White: str = "color: black; background: white;"
