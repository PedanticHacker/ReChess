from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QRadioButton,
    QVBoxLayout,
)

from rechess.utils import set_setting_value, setting_value


Cancel: QDialogButtonBox.StandardButton = QDialogButtonBox.StandardButton.Cancel
Save: QDialogButtonBox.StandardButton = QDialogButtonBox.StandardButton.Save


class SettingsDialog(QDialog):
    """Dialog for changing and saving settings."""

    def __init__(self) -> None:
        super().__init__()

        self._button_box: QDialogButtonBox = QDialogButtonBox(Save | Cancel)

        self.set_title()
        self.create_groups()
        self.create_options()
        self.set_vertical_layout()
        self.connect_signals_to_slots()

    def set_title(self) -> None:
        """Set dialog's title."""
        self.setWindowTitle("Settings")

    def create_groups(self) -> None:
        """Create groups for related settings to be put together."""
        self._engine_group: QGroupBox = QGroupBox("Engine")
        self._human_group: QGroupBox = QGroupBox("Human")
        self._time_control_group: QGroupBox = QGroupBox("Time Control")

    def create_options(self) -> None:
        """Create options that represent settings."""
        is_engine_white: bool = setting_value("engine", "is_white")
        is_engine_ponder_on: bool = setting_value("engine", "is_ponder_on")

        clock_time: float = setting_value("clock", "time")
        clock_increment: float = setting_value("clock", "increment")

        self._engine_black_option: QRadioButton = QRadioButton()
        self._engine_black_option.setText("Black")
        self._engine_black_option.setChecked(not is_engine_white)

        self._engine_white_option: QRadioButton = QRadioButton()
        self._engine_white_option.setText("White")
        self._engine_white_option.setChecked(is_engine_white)

        self._engine_ponder_option: QCheckBox = QCheckBox()
        self._engine_ponder_option.setText("Ponder")
        self._engine_ponder_option.setChecked(is_engine_ponder_on)

        self._clock_time_option: QComboBox = QComboBox()
        self._clock_time_option.addItem("1 minute", 60.0)
        self._clock_time_option.addItem("3 minutes", 180.0)
        self._clock_time_option.addItem("5 minutes", 300.0)
        self._clock_time_option.addItem("10 minutes", 600.0)
        self._clock_time_option.addItem("20 minutes", 1200.0)
        self._clock_time_option.addItem("30 minutes", 1800.0)
        self._clock_time_option.addItem("1 hour", 3600.0)
        self._clock_time_option.addItem("2 hours", 7200.0)
        self._clock_time_option.setCurrentIndex(
            self._clock_time_option.findData(clock_time)
        )

        self._clock_increment_option: QComboBox = QComboBox()
        self._clock_increment_option.addItem("0 seconds", 0.0)
        self._clock_increment_option.addItem("6 seconds", 6.0)
        self._clock_increment_option.addItem("12 seconds", 12.0)
        self._clock_increment_option.addItem("30 seconds", 30.0)
        self._clock_increment_option.setCurrentIndex(
            self._clock_increment_option.findData(clock_increment)
        )

        self._human_name_option: QLineEdit = QLineEdit()
        self._human_name_option.setMaxLength(20)
        self._human_name_option.setText(setting_value("human", "name"))

    def set_vertical_layout(self) -> None:
        """Set layout of dialog's widgets to be vertical."""
        human_layout: QVBoxLayout = QVBoxLayout()
        human_layout.addWidget(self._human_name_option)
        self._human_group.setLayout(human_layout)

        engine_layout: QVBoxLayout = QVBoxLayout()
        engine_layout.addWidget(self._engine_black_option)
        engine_layout.addWidget(self._engine_white_option)
        engine_layout.addWidget(self._engine_ponder_option)
        self._engine_group.setLayout(engine_layout)

        time_control_layout: QHBoxLayout = QHBoxLayout()
        time_control_layout.addWidget(self._clock_time_option)
        time_control_layout.addWidget(self._clock_increment_option)
        self._time_control_group.setLayout(time_control_layout)

        vertical_layout: QVBoxLayout = QVBoxLayout()
        vertical_layout.addWidget(self._human_group)
        vertical_layout.addWidget(self._engine_group)
        vertical_layout.addWidget(self._time_control_group)
        vertical_layout.addWidget(self._button_box)
        self.setLayout(vertical_layout)

    def connect_signals_to_slots(self) -> None:
        """Connect result signals to appropriate slot methods."""
        self.accepted.connect(self.on_accepted)
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)

    @Slot()
    def on_accepted(self) -> None:
        """Save settings on pressing dialog's Save button."""
        set_setting_value(
            section="clock",
            key="time",
            value=self._clock_time_option.currentData(),
        )
        set_setting_value(
            section="clock",
            key="increment",
            value=self._clock_increment_option.currentData(),
        )
        set_setting_value(
            section="engine",
            key="is_white",
            value=self._engine_white_option.isChecked(),
        )
        set_setting_value(
            section="engine",
            key="is_ponder_on",
            value=self._engine_ponder_option.isChecked(),
        )
        set_setting_value(
            section="human",
            key="name",
            value=self._human_name_option.text().strip() or "Human Warrior",
        )
