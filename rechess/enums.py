from enum import StrEnum


class ClockStyle(StrEnum):
    """A chess clock style for either the Black or the White player."""

    Black: str = "color: white; background: black;"
    White: str = "color: black; background: white;"
