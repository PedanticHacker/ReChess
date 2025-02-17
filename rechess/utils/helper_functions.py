import json
import os
import platform
import stat
import subprocess
from typing import Callable, Literal, overload

from psutil import cpu_count, virtual_memory
from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QColor, QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QPushButton


type BoardSection = Literal["board"]
type ClockSection = Literal["clock"]
type EngineSection = Literal["engine"]
type HumanSection = Literal["human"]
type UiSection = Literal["ui"]

type BoardKey = Literal["orientation"]
type ClockKey = Literal["time", "increment"]
type EngineKey = Literal["is_white", "is_ponder_on"]
type HumanKey = Literal["name"]
type StyleKey = Literal["style"]

type SettingSection = BoardSection | ClockSection | EngineSection | HumanSection | UiSection
type SettingKey = BoardKey | ClockKey | EngineKey | HumanKey | StyleKey
type SettingValue = bool | float | str
type SettingsDict = dict[SettingSection, dict[SettingKey, SettingValue]]


def platform_name() -> str:
    """Return platform name in lowercase."""
    name: str = platform.system().lower()
    return "macos" if name == "darwin" else name


def _stockfish_filename() -> str:
    """Return platform-specific filename of Stockfish engine."""
    return "stockfish.exe" if platform_name() == "windows" else "stockfish"


def path_to_stockfish() -> str:
    """Return path to executable file of Stockfish 17 engine."""
    return (
        f"rechess/assets/engines/stockfish-17/{platform_name()}"
        f"/{_stockfish_filename()}"
    )


def engine_file_filter() -> str:
    """Return platform-specific filter of executable engine file."""
    return "Chess engine (*.exe)" if platform_name() == "windows" else ""


def delete_quarantine_attribute(path_to_file: str) -> None:
    """Delete quarantine attribute for file at `path_to_file`."""
    if hasattr(os, "removexattr"):
        os.removexattr(path_to_file, "com.apple.quarantine")


def make_executable(path_to_file: str) -> None:
    """Make file at `path_to_file` be executable."""
    os.chmod(path_to_file, os.stat(path_to_file).st_mode | stat.S_IXUSR)


def _available_hash() -> int:
    """Return all available RAM in megabytes to be used as hash."""
    MEGABYTES_FACTOR: int = 1_048_576
    return virtual_memory().available // MEGABYTES_FACTOR


def _available_threads() -> int:
    """Return all CPU threads, but reserve one for other CPU tasks."""
    cpu_threads: int | None = cpu_count()
    return 1 if not cpu_threads or cpu_threads == 1 else cpu_threads - 1


def engine_configuration() -> dict[str, int]:
    """Return configuration for engine based on available resources."""
    return {"Hash": _available_hash(), "Threads": _available_threads()}


def _settings() -> SettingsDict:
    """Return all settings from settings.json file."""
    with open("rechess/settings.json") as settings_file:
        return json.load(settings_file)


@overload
def setting_value(section: BoardSection, key: BoardKey) -> bool: ...
@overload
def setting_value(section: ClockSection, key: ClockKey) -> float: ...
@overload
def setting_value(section: EngineSection, key: EngineKey) -> bool: ...
@overload
def setting_value(section: HumanSection, key: HumanKey) -> str: ...
@overload
def setting_value(section: UiSection, key: StyleKey) -> str: ...
def setting_value(section: SettingSection, key: SettingKey) -> SettingValue:
    """Return value of `key` from `section`."""
    settings_dict: SettingsDict = _settings()
    return settings_dict[section][key]


@overload
def set_setting_value(section: BoardSection, key: BoardKey, value: bool) -> None: ...
@overload
def set_setting_value(section: ClockSection, key: ClockKey, value: float) -> None: ...
@overload
def set_setting_value(section: EngineSection, key: EngineKey, value: bool) -> None: ...
@overload
def set_setting_value(section: HumanSection, key: HumanKey, value: str) -> None: ...
@overload
def set_setting_value(section: UiSection, key: StyleKey, value: str) -> None: ...
def set_setting_value(
    section: SettingSection, key: SettingKey, value: SettingValue
) -> None:
    """Set `value` to `key` for `section`."""
    settings_dict: SettingsDict = _settings()
    settings_dict[section][key] = value

    with open("rechess/settings.json", mode="w", newline="\n") as settings_file:
        json.dump(settings_dict, settings_file, indent=2)
        settings_file.write("\n")


def find_opening(fen: str) -> tuple[str, str] | None:
    """Return ECO code and opening name based on `fen`."""
    with open("rechess/openings.json", encoding="utf-8") as json_file:
        openings = json.load(json_file)
    return openings.get(fen)


def style_name(filename: str) -> str:
    """Return human-readable style name based on `filename`."""
    styles: dict[str, str] = {
        "dark-forest": "Dark forest",
        "dark-mint": "Dark mint",
        "dark-nebula": "Dark nebula",
        "dark-ocean": "Dark ocean",
        "light-forest": "Light forest",
        "light-mint": "Light mint",
        "light-nebula": "Light nebula",
        "light-ocean": "Light ocean",
    }
    return styles[filename]


def app_object() -> QApplication:
    """Initialize QApplication with basic settings and return it."""
    app: QApplication = QApplication()
    app.setApplicationDisplayName("ReChess")
    app.setApplicationName("ReChess")
    app.setApplicationVersion("1.0")
    app.setDesktopFileName("ReChess")
    app.setStyle("fusion")
    app.setWindowIcon(svg_icon("logo"))
    return app


def create_action(
    handler: Callable, icon: QIcon, name: str, shortcut: str, status_tip: str
) -> QAction:
    """Create action for menubar menu or toolbar button."""
    action: QAction = QAction(icon, name)
    action.setShortcut(shortcut)
    action.setStatusTip(status_tip)
    action.triggered.connect(handler)
    return action


def create_button(icon: QIcon) -> QPushButton:
    """Create button with `icon`."""
    button: QPushButton = QPushButton()
    button.setIcon(icon)
    button.setIconSize(QSize(56, 56))
    return button


def colorize_icon(color: str) -> QIcon:
    """Return icon in 16 by 16 pixels filled with `color`."""
    pixmap: QPixmap = QPixmap(16, 16)
    pixmap.fill(QColor(color))
    return QIcon(pixmap)


def svg_icon(filename: str) -> QIcon:
    """Return SVG icon from file at `filename`."""
    return QIcon(f":/icons/{filename}.svg")
