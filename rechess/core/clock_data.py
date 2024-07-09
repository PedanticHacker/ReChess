class ClockData:
    """A clock data manager for seconds, increment, and clock time."""

    def __init__(self, seconds: int, increment: int, time: int) -> None:
        self.seconds: int = seconds
        self.increment: int = increment
        self.time: int = time

        self.reset()

    def add_increment(self) -> None:
        """Add an increment in seconds to the current clock time."""
        self.time += self.increment

    def reset(self) -> None:
        """Reset the current clock time."""
        self.time = self.seconds

    def update_time(self) -> None:
        """Update the current clock time."""
        if self.time > 0:
            self.time -= 1
