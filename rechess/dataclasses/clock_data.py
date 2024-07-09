from dataclasses import dataclass


@dataclass
class ClockData:
    seconds: int
    increment: int
    time: int

    def __post_init__(self) -> None:
        self.reset()

    def add_increment(self) -> None:
        self.time += self.increment

    def reset(self) -> None:
        self.time: int = self.seconds

    def update_time(self) -> None:
        if self.time > 0:
            self.time -= 1
