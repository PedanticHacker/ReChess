from typing import Protocol


class Engine(Protocol):
    """Protocol for specific chess engine implementation."""

    game: Game


class Game(Protocol):
    """Protocol for specific chess game rules implementation."""

    def find_move(self) -> None:
        raise NotImplementedError

    def push(self) -> None:
        raise NotImplementedError
