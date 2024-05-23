from enum import StrEnum


class ClockColor(StrEnum):
    """Clock colors for the Black player and the White player."""

    Black: str = "color: white; background: black;"
    White: str = "color: black; background: white;"
