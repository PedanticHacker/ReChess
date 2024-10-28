import json
import os
import platform
import stat
import subprocess
from typing import Callable, Literal, overload, TypeAlias

from psutil import cpu_count, virtual_memory
from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QPushButton


BoardSection: TypeAlias = Literal["board"]
ClockSection: TypeAlias = Literal["clock"]
EngineSection: TypeAlias = Literal["engine"]
SettingSection: TypeAlias = BoardSection | ClockSection | EngineSection

BoardKey: TypeAlias = Literal["orientation"]
ClockKey: TypeAlias = Literal["time", "increment"]
EngineKey: TypeAlias = Literal["is_pondering", "is_white"]
SettingKey: TypeAlias = BoardKey | ClockKey | EngineKey

SettingValue: TypeAlias = bool | float


def _optimal_hash_size() -> int:
    """Return 70% of available RAM in MB as optimal hash size."""
    available_ram = virtual_memory().available
    megabytes_factor = 1048576
    seventy_percent = 0.70
    return round(available_ram / megabytes_factor * seventy_percent)


def _optimal_threads() -> int:
    """Return optimal threads, reserving 1 for other CPU tasks."""
    available_threads = cpu_count(logical=True)
    reserved_threads = 1
    minimum_threads = 1
    return max(minimum_threads, available_threads - reserved_threads)


def _stockfish_file_name() -> str:
    """Return platform-specific file name of Stockfish chess engine."""
    return "stockfish.exe" if system_name() == "windows" else "stockfish"


@overload
def setting_value(section: BoardSection, key: BoardKey) -> bool: ...


@overload
def setting_value(section: ClockSection, key: ClockKey) -> float: ...


@overload
def setting_value(section: EngineSection, key: EngineKey) -> bool: ...


def setting_value(section: SettingSection, key: SettingKey) -> SettingValue:
    """Return JSON value of `key` from `section`."""
    with open("rechess/settings.json") as settings_file:
        settings_data = json.load(settings_file)
    return settings_data[section][key]


@overload
def set_setting_value(section: BoardSection, key: BoardKey, value: bool) -> None: ...


@overload
def set_setting_value(section: ClockSection, key: ClockKey, value: float) -> None: ...


@overload
def set_setting_value(section: EngineSection, key: EngineKey, value: bool) -> None: ...


def set_setting_value(
    section: SettingSection,
    key: SettingKey,
    value: SettingValue,
) -> None:
    """Set JSON `value` to `key` for `section`."""
    with open("rechess/settings.json") as settings_file:
        settings_data = json.load(settings_file)
    settings_data[section][key] = value

    with open("rechess/settings.json", mode="w", newline="\n") as settings_file:
        json.dump(settings_data, settings_file, indent=4)
        settings_file.write("\n")


def app_style(file_name: str) -> str:
    """Return app style from `file_name`."""
    with open(f"rechess/assets/styles/{file_name}.qss") as qss_file:
        return qss_file.read()


def board_colors() -> dict[str, str]:
    """Provide colors for chessboard elements."""
    return {
        "arrow blue": "#0056ff70",
        "arrow green": "#1a9c2270",
        "arrow red": "#cc262670",
        "arrow yellow": "#ffa000a0",
        "coord": "#f5f3f2",
        "inner border": "#2c2826",
        "margin": "#352f2d",
        "outer border": "#2c2826",
        "square dark": "#2c2826",
        "square dark lastmove": "#352f2d",
        "square light": "#45403d",
        "square light lastmove": "#5c5552",
    }


def create_action(
    name: str,
    icon: QIcon,
    shortcut: str,
    status_tip: str,
    handler: Callable,
) -> QAction:
    """Create action for toolbar or menubar item."""
    action = QAction(icon, name)
    action.setShortcut(shortcut)
    action.setStatusTip(status_tip)
    action.triggered.connect(handler)
    return action


def create_button(icon: QIcon) -> QPushButton:
    """Create button from `icon`."""
    button = QPushButton()
    button.setIcon(icon)
    button.setIconSize(QSize(56, 56))
    return button


def delete_quarantine_attribute(file_name) -> None:
    """Delete quarantine attribute for `file_name` on macOS."""
    if system_name() == "macos":
        file_attributes = subprocess.run(
            ["xattr", "-l", file_name],
            capture_output=True,
            text=True,
        )

        if "com.apple.quarantine" in file_attributes.stdout:
            subprocess.run(["xattr", "-d", "com.apple.quarantine", file_name])


def engine_configuration() -> dict[str, int]:
    """Return optimal configuration for UCI chess engine."""
    return {"Hash": _optimal_hash_size(), "Threads": _optimal_threads()}


def initialize_app() -> QApplication:
    """Initialize ReChess GUI app and set some basics."""
    app: QApplication = QApplication()
    app.setApplicationDisplayName("ReChess")
    app.setApplicationName("ReChess")
    app.setApplicationVersion("1.0")
    app.setDesktopFileName("ReChess")
    app.setStyle("fusion")
    app.setStyleSheet(app_style("dark"))
    app.setWindowIcon(svg_icon("logo"))
    return app


def make_executable(file_name) -> None:
    """Make `file_name` be executable."""
    os.chmod(file_name, os.stat(file_name).st_mode | stat.S_IXUSR)


def stockfish() -> str:
    """Return file path to default Stockfish 17 chess engine."""
    return (
        f"rechess/assets/engines/stockfish-17/{system_name()}"
        f"/{_stockfish_file_name()}"
    )


def svg_icon(file_name: str) -> QIcon:
    """Return SVG icon from `file_name`."""
    return QIcon(f":/icons/{file_name}.svg")


def system_name() -> str:
    """Return operating system name in lowercase."""
    operating_system = platform.system().lower()
    return "macos" if operating_system == "darwin" else operating_system
