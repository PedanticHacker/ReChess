from json import dump

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QDialog,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QVBoxLayout,
    QRadioButton,
    QDialogButtonBox,
)

from rechess import get_config_value


class SettingsDialog(QDialog):
    """A dialog for changing the settings."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Settings")

        self.set_button_box()
        self.create_groups()
        self.create_options()
        self.set_personal_layout()
        self.connect_events_with_handlers()

    def set_button_box(self) -> None:
        """Set a button box with OK and Cancel buttons."""
        self.button_box: QDialogButtonBox = QDialogButtonBox()
        self.button_box.setStandardButtons(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

    def create_groups(self) -> None:
        """Create a chess engine group and a time control group."""
        self.engine_group: QGroupBox = QGroupBox()
        self.engine_group.setTitle("Chess engine")
        # self.engine_group.setDisabled()

        self.time_control_group: QGroupBox = QGroupBox()
        self.time_control_group.setTitle("Time control")
        # self.time_control_group.setDisabled()

    def create_options(self) -> None:
        """Create options that will represent the settings."""
        is_engine_black: bool = get_config_value("engine", "black")
        is_engine_pondering: bool = get_config_value("engine", "pondering")

        clock_time: int = get_config_value("clock", "time")
        clock_increment: int = get_config_value("clock", "increment")

        self.engine_black_option: QRadioButton = QRadioButton()
        self.engine_black_option.setText("Black")
        self.engine_black_option.setChecked(is_engine_black)

        self.engine_white_option: QRadioButton = QRadioButton()
        self.engine_white_option.setText("White")
        self.engine_white_option.setChecked(not is_engine_black)

        self.pondering_option: QCheckBox = QCheckBox()
        self.pondering_option.setText("Pondering")
        self.pondering_option.setChecked(is_engine_pondering)

        self.time_option: QComboBox = QComboBox()
        self.time_option.addItem("1 minute", 60)
        self.time_option.addItem("3 minutes", 180)
        self.time_option.addItem("5 minutes", 300)
        self.time_option.addItem("10 minutes", 600)
        self.time_option.addItem("20 minutes", 1200)
        self.time_option.addItem("30 minutes", 1800)
        self.time_option.addItem("1 hour", 3600)
        self.time_option.addItem("2 hours", 7200)
        self.time_option.setCurrentIndex(self.time_option.findData(clock_time))

        self.increment_option: QComboBox = QComboBox()
        self.increment_option.addItem("0 seconds", 0)
        self.increment_option.addItem("6 seconds", 6)
        self.increment_option.addItem("12 seconds", 12)
        self.increment_option.addItem("30 seconds", 30)
        self.increment_option.setCurrentIndex(
            self.increment_option.findData(clock_increment),
        )

    def set_personal_layout(self) -> None:
        """Set a personal layout for the widgets."""
        engine_layout: QVBoxLayout = QVBoxLayout()
        engine_layout.addWidget(self.engine_black_option)
        engine_layout.addWidget(self.engine_white_option)
        engine_layout.addWidget(self.pondering_option)
        self.engine_group.setLayout(engine_layout)

        time_control_layout: QHBoxLayout = QHBoxLayout()
        time_control_layout.addWidget(self.time_option)
        time_control_layout.addWidget(self.increment_option)
        self.time_control_group.setLayout(time_control_layout)

        personal_layout: QVBoxLayout = QVBoxLayout()
        personal_layout.addWidget(self.engine_group)
        personal_layout.addWidget(self.time_control_group)
        personal_layout.addWidget(self.button_box)
        self.setLayout(personal_layout)

    def connect_events_with_handlers(self) -> None:
        """Connect various events with specific handlers."""
        self.accepted.connect(self.save_settings)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    @Slot()
    def save_settings(self) -> None:
        """Save the changed settings."""
        is_engine_black: bool = self.engine_black_option.isChecked()
        is_engine_pondering: bool = self.pondering_option.isChecked()

        clock_time: int = self.time_option.currentData()
        clock_increment: int = self.increment_option.currentData()

        config_contents = {
            "engine": {
                "black": is_engine_black,
                "pondering": is_engine_pondering,
            },
            "clock": {
                "time": clock_time,
                "increment": clock_increment,
            },
        }

        with open("config.json", mode="w", newline="\n") as config_file:
            dump(config_contents, config_file, indent=4)
            config_file.write("\n")
