from PySide6.QtCore import QElapsedTimer, Qt, QTimer, Signal, Slot
from PySide6.QtWidgets import QLCDNumber

from rechess.enums import ClockColor
from rechess.utils import setting_value


class Clock(QLCDNumber):
    """A chess clock with 30 millisecond timer accuracy."""

    time_expired: Signal = Signal()

    def __init__(self, clock_color: ClockColor) -> None:
        super().__init__()

        self.setFixedSize(200, 50)
        self.setStyleSheet(clock_color)
        self.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)

        self._timer: QTimer = QTimer(self)
        self._timer.setInterval(30)
        self._timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._timer.timeout.connect(self.update_time)

        self._elapsed_timer: QElapsedTimer = QElapsedTimer()

        self.reset()

    def reset(self) -> None:
        """Set time to values from settings."""
        self.time: float = setting_value("clock", "time")
        self.increment: float = setting_value("clock", "increment")
        self.display_time()

    def display_time(self) -> None:
        """Display time in hh:mm:ss or mm:ss format."""
        time_as_text: str = self.format_time()
        self.setDigitCount(len(time_as_text))
        self.display(time_as_text)

    def format_time(self) -> str:
        """Return time in hh:mm:ss or mm:ss format."""
        time_in_seconds: int = round(self.time)
        hours, remaining_time = divmod(time_in_seconds, 3600)
        minutes, seconds = divmod(remaining_time, 60)
        return (
            f"{hours:02}:{minutes:02}:{seconds:02}"
            if hours
            else f"{minutes:02}:{seconds:02}"
        )

    def start_timer(self) -> None:
        """Track elapsed time and start timer countdown."""
        self._elapsed_timer.start()
        self._timer.start()

    def stop_timer(self) -> None:
        """Stop timer countdown."""
        self._timer.stop()

    def add_increment(self) -> None:
        """Add increment to time."""
        self.time += self.increment
        self.display_time()

    @Slot()
    def update_time(self) -> None:
        """Display decremented time and handle time expiration."""
        elapsed_time: float = self._elapsed_timer.restart() / 1000.0
        self.time -= elapsed_time
        self.display_time()

        if self.time <= 0.0:
            self._timer.stop()
            self.time_expired.emit()
