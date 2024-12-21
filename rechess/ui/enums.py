from enum import StrEnum


class ClockColor(StrEnum):
    """CSS color style enum for clocks of Black and White players."""

    Black = "color: white; background-color: black;"
    White = "color: black; background-color: white;"
