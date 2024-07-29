from enum import StrEnum


class ClockColor(StrEnum):
    """CSS colors enum for Black and White players' chess clocks."""

    Black: str = "color: white; background-color: black;"
    White: str = "color: black; background-color: white;"
