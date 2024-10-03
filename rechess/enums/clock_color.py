from enum import StrEnum


class ClockColor(StrEnum):
    """CSS color enum for Black's and White's chess clock widget."""

    Black: str = "color: white; background-color: black;"
    White: str = "color: black; background-color: white;"
