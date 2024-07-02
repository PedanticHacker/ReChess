from enum import StrEnum


class ClockColor(StrEnum):
    """A CSS color for Black and White player's clock."""

    Black: str = "color: white; background: black;"
    White: str = "color: black; background: white;"
