from enum import StrEnum


class ClockColor(StrEnum):
    """CSS color for Black and White player's chess clock."""

    Black: str = "color: white; background: black;"
    White: str = "color: black; background: white;"
