from enum import StrEnum


class ClockColor(StrEnum):
    """CSS color style enum for clocks of Black and White players."""

    Black: str = "color: white; background-color: black;"
    White: str = "color: black; background-color: white;"
