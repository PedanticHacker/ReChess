from __future__ import annotations

import json
import os
import platform
import stat
import subprocess
import sys
from functools import lru_cache
from typing import Any, Callable, Final

from psutil import cpu_count, virtual_memory
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QColor, QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton, QSplashScreen


def colorize_icon(color: str) -> QIcon:
    """Get icon in 16 by 16 pixels filled with `color`."""
    pixmap: QPixmap = QPixmap(16, 16)
    pixmap.fill(QColor(color))
    return QIcon(pixmap)


def create_action(
    handler: Callable, icon: QIcon, name: str, shortcut: str, status_tip: str
) -> QAction:
    """Create action for menu or toolbar button."""
    action: QAction = QAction(icon, name)
    action.setShortcut(shortcut)
    action.setStatusTip(status_tip)
    action.triggered.connect(handler)
    return action


def create_app() -> QApplication:
    """Create QApplication object initialized with basic settings."""
    app: QApplication = QApplication()
    app.setApplicationDisplayName("ReChess")
    app.setApplicationName("ReChess")
    app.setApplicationVersion("1.0")
    app.setDesktopFileName("ReChess")
    app.setStyle("fusion")
    app.setWindowIcon(svg_icon("logo"))
    return app


def create_button(icon: QIcon) -> QPushButton:
    """Create button with `icon`."""
    button: QPushButton = QPushButton()
    button.setIcon(icon)
    button.setIconSize(QSize(56, 56))
    return button


def create_splash_screen() -> QSplashScreen:
    """Create and show ReChess text and app logo as splash screen."""
    logo_pixmap: QPixmap = svg_icon("logo").pixmap(300, 300)
    center_alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter
    yellow_color: Qt.GlobalColor = Qt.GlobalColor.yellow

    splash_screen: QSplashScreen = QSplashScreen(logo_pixmap)

    message_font: QFont = splash_screen.font()
    message_font.setBold(True)
    message_font.setPointSize(16)

    splash_screen.setFont(message_font)
    splash_screen.showMessage("ReChess 1.0", center_alignment, yellow_color)
    splash_screen.show()
    splash_screen.repaint()

    return splash_screen


def show_info(parent: QWidget, message: str) -> None:
    """Inform about something based on `message`."""
    QMessageBox.information(parent, "Info", message)


def show_warning(parent: QWidget) -> None:
    """Warn that ReChess is already running and terminate relaunch."""
    title: str = "Warning"
    text: str = "ReChess is already running!"
    QMessageBox.warning(parent, title, text)
    parent.destruct()
    sys.exit()


def svg_icon(file_name: str) -> QIcon:
    """Get SVG icon from SVG file at `file_name`."""
    return QIcon(f":/icons/{file_name}.svg")


def _settings() -> dict[str, dict[str, Any]]:
    """Get all settings from settings.json file."""
    with open("rechess/settings.json") as settings_file:
        return json.load(settings_file)


def setting_value(section: str, key: str) -> Any:
    """Get value of `key` from `section`."""
    settings_dict: dict[str, dict[str, Any]] = _settings()
    return settings_dict[section][key]


def set_setting_value(section: str, key: str, value: Any) -> None:
    """Set `value` to `key` for `section`."""
    settings_dict: dict[str, dict[str, Any]] = _settings()
    settings_dict[section][key] = value

    with open("rechess/settings.json", mode="w", newline="\n") as settings_file:
        json.dump(settings_dict, settings_file, indent=2)
        settings_file.write("\n")


def style_name(file_name: str) -> str:
    """Get formatted QSS style name based on `file_name`."""
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
    return styles[file_name]


def delete_quarantine_attribute(path_to_file: str) -> None:
    """Delete quarantine attribute for file at `path_to_file`."""
    if platform.system() == "Darwin":
        subprocess.run(
            ["xattr", "-d", "com.apple.quarantine", path_to_file],
            stderr=subprocess.DEVNULL,
        )


def _available_hash() -> int:
    """Get all available RAM in megabytes to be used as hash."""
    MEGABYTES_FACTOR: Final[int] = 1_048_576
    return virtual_memory().available // MEGABYTES_FACTOR


def _available_threads() -> int:
    """Get all available CPU threads, else at least one."""
    cpu_threads: int | None = cpu_count()
    return cpu_threads if cpu_threads is not None else 1


def engine_configuration() -> dict[str, int]:
    """Get configuration for engine based on available resources."""
    return {"Hash": _available_hash(), "Threads": _available_threads()}


def engine_file_filter() -> str:
    """Get platform-specific filter for executable file of engine."""
    return "Chess engine (*.exe)" if platform.system() == "Windows" else ""


def make_executable(path_to_file: str) -> None:
    """Make file at `path_to_file` be executable."""
    if platform.system() == "Linux":
        os.chmod(path_to_file, os.stat(path_to_file).st_mode | stat.S_IXUSR)


def path_to_stockfish() -> str:
    """Get path to executable file of Stockfish 17 engine."""
    system: str = platform.system()
    extension: str = ".exe" if system == "Windows" else ""
    return f"rechess/assets/engines/stockfish-17.1/{system}/stockfish{extension}"


@lru_cache(maxsize=1)
def _load_openings() -> dict[str, list[str]]:
    """Load openings from JSON file."""
    with open("rechess/openings.json", encoding="utf-8") as json_file:
        return json.load(json_file)


def find_opening(fen: str) -> list[str] | None:
    """Get ECO code and opening name based on `fen`."""
    return _load_openings().get(fen)
