from functools import partial
from pathlib import Path

from chess import Move
from chess.engine import Score
from PySide6.QtCore import Qt, QThreadPool, Slot
from PySide6.QtGui import QCloseEvent, QWheelEvent
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QGridLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QWidget,
)

from rechess.core import Game
from rechess.uci import Engine
from rechess.ui import ClockColor
from rechess.ui.dialogs import SettingsDialog
from rechess.ui.table import TableModel, TableView
from rechess.ui.widgets import Board, Clock, EvaluationBar, FenEditor
from rechess.utils import (
    create_action,
    find_opening,
    platform_name,
    set_setting_value,
    setting_value,
    style_icon,
    svg_icon,
)


class MainWindow(QMainWindow):
    """Main window containing all widgets."""

    def __init__(self) -> None:
        super().__init__()

        self.apply_style(setting_value("ui", "style"))

        self._game: Game = Game()
        self._engine: Engine = Engine(self._game)

        self._table_model: TableModel = TableModel(self._game.moves)
        self._table_view: TableView = TableView(self._table_model)

        self._black_clock: Clock = Clock(ClockColor.Black)
        self._white_clock: Clock = Clock(ClockColor.White)

        self._board: Board = Board(self._game)
        self._fen_editor: FenEditor = FenEditor(self._game)
        self._evaluation_bar: EvaluationBar = EvaluationBar()

        self._engine_analysis_label: QLabel = QLabel()
        self._engine_analysis_label.setObjectName("analysis")
        self._engine_analysis_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._engine_analysis_label.setWordWrap(True)

        self._engine_name_label: QLabel = QLabel()
        self._engine_name_label.setObjectName("engine")
        self._engine_name_label.setText(self._engine.name)

        self._human_name_label: QLabel = QLabel()
        self._human_name_label.setObjectName("human")
        self._human_name_label.setText("Boštjan Mejak")

        self._notifications_label: QLabel = QLabel()
        self._notifications_label.setObjectName("notifications")

        self._openings_label: QLabel = QLabel()

        self.set_size()
        self.set_layout()
        self.create_actions()
        self.create_menubar()
        self.create_toolbar()
        self.create_statusbar()
        self.switch_clock_timers()
        self.adjust_toolbar_buttons()
        self.connect_signals_to_slots()

        if self.should_flip():
            self.flip()
            self.invoke_engine()

    def set_size(self) -> None:
        """Set minimum size to 1000 by 700 pixels, show maximized."""
        self.setMinimumSize(1000, 700)
        self.showMaximized()

    def set_layout(self) -> None:
        """Set layout for fixed-position widgets."""
        self._grid_layout: QGridLayout = QGridLayout()

        self._grid_layout.addWidget(self._black_clock, 1, 1)
        self._grid_layout.addWidget(self._engine_name_label, 2, 1)
        self._grid_layout.addWidget(self._white_clock, 4, 1)
        self._grid_layout.addWidget(self._human_name_label, 5, 1)
        self._grid_layout.addWidget(self._board, 1, 2, 4, 1)
        self._grid_layout.addWidget(self._evaluation_bar, 1, 3, 4, 1)
        self._grid_layout.addWidget(self._table_view, 1, 4, 4, 1)
        self._grid_layout.addWidget(self._notifications_label, 5, 4)
        self._grid_layout.addWidget(self._fen_editor, 5, 2)
        self._grid_layout.addWidget(self._engine_analysis_label, 6, 2)

        self._grid_layout.setRowStretch(0, 4)
        self._grid_layout.setRowStretch(3, 4)
        self._grid_layout.setRowStretch(5, 4)
        self._grid_layout.setRowStretch(7, 4)
        self._grid_layout.setColumnStretch(0, 4)
        self._grid_layout.setColumnStretch(5, 4)

        self._central_widget: QWidget = QWidget()
        self._central_widget.setLayout(self._grid_layout)
        self.setCentralWidget(self._central_widget)

    def create_actions(self) -> None:
        """Create menu and toolbar actions."""
        self.about_action = create_action(
            handler=self.show_about,
            icon=svg_icon("about"),
            name="About ReChess",
            shortcut="F1",
            status_tip="Shows the About dialog.",
        )
        self.dark_forest_style_action = create_action(
            handler=partial(self.apply_style, "dark-forest"),
            icon=style_icon("#2d382d"),
            name="Dark forest",
            shortcut="Alt+F1",
            status_tip="Applies the dark forest style.",
        )
        self.dark_mint_style_action = create_action(
            handler=partial(self.apply_style, "dark-mint"),
            icon=style_icon("#1a2e2e"),
            name="Dark mint",
            shortcut="Alt+F2",
            status_tip="Applies the dark mint style.",
        )
        self.dark_nebula_style_action = create_action(
            handler=partial(self.apply_style, "dark-nebula"),
            icon=style_icon("#1a1025"),
            name="Dark nebula",
            shortcut="Alt+F3",
            status_tip="Applies the dark nebula style.",
        )
        self.dark_ocean_style_action = create_action(
            handler=partial(self.apply_style, "dark-ocean"),
            icon=style_icon("#1a2838"),
            name="Dark ocean",
            shortcut="Alt+F4",
            status_tip="Applies the dark ocean style.",
        )
        self.flip_action = create_action(
            handler=self.flip,
            icon=svg_icon("flip"),
            name="Flip",
            shortcut="Ctrl+F",
            status_tip="Flips the orientation of board and its related widgets.",
        )
        self.light_forest_style_action = create_action(
            handler=partial(self.apply_style, "light-forest"),
            icon=style_icon("#e8efe6"),
            name="Light forest",
            shortcut="Alt+F5",
            status_tip="Applies the light forest style.",
        )
        self.light_mint_style_action = create_action(
            handler=partial(self.apply_style, "light-mint"),
            icon=style_icon("#ebf5f3"),
            name="Light mint",
            shortcut="Alt+F6",
            status_tip="Applies the light mint style.",
        )
        self.light_nebula_style_action = create_action(
            handler=partial(self.apply_style, "light-nebula"),
            icon=style_icon("#f4ebff"),
            name="Light nebula",
            shortcut="Alt+F7",
            status_tip="Applies the light nebula style.",
        )
        self.light_ocean_style_action = create_action(
            handler=partial(self.apply_style, "light-ocean"),
            icon=style_icon("#ebf3f8"),
            name="Light ocean",
            shortcut="Alt+F8",
            status_tip="Applies the light ocean style.",
        )
        self.load_engine_action = create_action(
            handler=self.load_engine,
            icon=svg_icon("load-engine"),
            name="Load engine...",
            shortcut="Ctrl+L",
            status_tip="Shows the file manager to load an engine.",
        )
        self.new_game_action = create_action(
            handler=self.offer_new_game,
            icon=svg_icon("new-game"),
            name="New game",
            shortcut="Ctrl+N",
            status_tip="Shows a dialog offering to start a new game.",
        )
        self.play_move_now_action = create_action(
            handler=self.play_move_now,
            icon=svg_icon("play-move-now"),
            name="Play move now",
            shortcut="Ctrl+P",
            status_tip="Forces the engine to play on current turn.",
        )
        self.quit_action = create_action(
            handler=self.quit,
            icon=svg_icon("quit"),
            name="Quit...",
            shortcut="Ctrl+Q",
            status_tip="Offers to quit the app.",
        )
        self.settings_action = create_action(
            handler=self.show_settings_dialog,
            icon=svg_icon("settings"),
            name="Settings...",
            shortcut="Ctrl+,",
            status_tip="Shows a dialog to edit the settings.",
        )
        self.start_analysis_action = create_action(
            handler=self.start_analysis,
            icon=svg_icon("start-analysis"),
            name="Start analysis",
            shortcut="F3",
            status_tip="Starts analyzing the current position.",
        )
        self.stop_analysis_action = create_action(
            handler=self.stop_analysis,
            icon=svg_icon("stop-analysis"),
            name="Stop analysis",
            shortcut="F4",
            status_tip="Stops analyzing the current position.",
        )

    def create_menubar(self) -> None:
        """Create menubar with actions in separate menus."""

        # Menubar
        menubar = self.menuBar()

        # General menu
        general_menu = menubar.addMenu("General")

        # Style menu
        style_menu = menubar.addMenu("Style")

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        # Help menu
        help_menu = menubar.addMenu("Help")

        # General menu > Load engine...
        general_menu.addAction(self.load_engine_action)

        # General menu separator
        general_menu.addSeparator()

        # General menu > Quit...
        general_menu.addAction(self.quit_action)

        # Style menu > Dark forest
        style_menu.addAction(self.dark_forest_style_action)

        # Style menu > Dark mint
        style_menu.addAction(self.dark_mint_style_action)

        # Style menu > Dark nebula
        style_menu.addAction(self.dark_nebula_style_action)

        # Style menu > Dark ocean
        style_menu.addAction(self.dark_ocean_style_action)

        # Style menu > Light forest
        style_menu.addAction(self.light_forest_style_action)

        # Style menu > Light mint
        style_menu.addAction(self.light_mint_style_action)

        # Style menu > Light nebula
        style_menu.addAction(self.light_nebula_style_action)

        # Style menu > Light ocean
        style_menu.addAction(self.light_ocean_style_action)

        # Edit menu > Settings...
        edit_menu.addAction(self.settings_action)

        # Help menu > About
        help_menu.addAction(self.about_action)

    def create_toolbar(self) -> None:
        """Create toolbar with buttons in separate areas."""

        # General area
        general_area = self.addToolBar("General")

        # Edit area
        edit_area = self.addToolBar("Edit")

        # Help area
        help_area = self.addToolBar("Help")

        # General area > Quit
        general_area.addAction(self.quit_action)

        # Edit area > New game
        edit_area.addAction(self.new_game_action)

        # Edit area > Flip orientation
        edit_area.addAction(self.flip_action)

        # Edit area > Play move now
        edit_area.addAction(self.play_move_now_action)

        # Edit area > Start analysis
        edit_area.addAction(self.start_analysis_action)

        # Edit area > Stop analysis
        edit_area.addAction(self.stop_analysis_action)

        # Edit area > Settings
        edit_area.addAction(self.settings_action)

        # Edit area > Load engine
        edit_area.addAction(self.load_engine_action)

        # Help area > About
        help_area.addAction(self.about_action)

    def create_statusbar(self) -> None:
        """Create statusbar for showing openings and tips."""
        self.statusBar().addWidget(self._openings_label)

    def switch_clock_timers(self) -> None:
        """Switch Black's and White's clock timers based on turn."""
        if self._game.is_white_on_turn():
            self._black_clock.stop_timer()
            self._white_clock.start_timer()
            if self._game.is_in_progress():
                self._black_clock.add_increment()
        else:
            self._white_clock.stop_timer()
            self._black_clock.start_timer()
            if self._game.is_in_progress():
                self._white_clock.add_increment()

    def adjust_toolbar_buttons(self) -> None:
        """Adjust state of engine-related toolbar buttons."""
        self.play_move_now_action.setEnabled(True)
        self.start_analysis_action.setEnabled(True)
        self.stop_analysis_action.setDisabled(True)

        if self._game.is_over():
            self.play_move_now_action.setDisabled(True)
            self.stop_analysis_action.setDisabled(True)
            self.start_analysis_action.setDisabled(True)

    def connect_signals_to_slots(self) -> None:
        """Connect component signals to corresponding slot methods."""
        self._black_clock.time_expired.connect(self.on_black_time_expired)
        self._engine.best_move_analyzed.connect(self.on_best_move_analyzed)
        self._engine.move_played.connect(self.on_move_played)
        self._engine.score_analyzed.connect(self.on_score_analyzed)
        self._engine.variation_analyzed.connect(self.on_variation_analyzed)
        self._fen_editor.fen_validated.connect(self.on_fen_validated)
        self._game.move_played.connect(self.on_move_played)
        self._table_view.item_selected.connect(self.on_item_selected)
        self._white_clock.time_expired.connect(self.on_white_time_expired)

    def invoke_engine(self) -> None:
        """Invoke engine to play move."""
        QThreadPool.globalInstance().start(self._engine.play_move)
        self._notifications_label.setText("Thinking...")

    def invoke_analysis(self) -> None:
        """Invoke engine to start analysis."""
        QThreadPool.globalInstance().start(self._engine.start_analysis)
        self._notifications_label.setText("Analyzing...")

    def quit(self) -> None:
        """Trigger main window's close event to quit."""
        self.close()

    def flip(self) -> None:
        """Flip orientation of board and its related widgets."""
        current_orientation: bool = setting_value("board", "orientation")
        set_setting_value("board", "orientation", not current_orientation)

        self.flip_clocks()
        self.flip_player_names()
        self._evaluation_bar.flip_appearance()

    def should_flip(self) -> bool:
        """Return True if orientation should be flipped."""
        is_engine_white: bool = setting_value("engine", "is_white")
        is_white_on_bottom: bool = setting_value("board", "orientation")
        return is_engine_white and is_white_on_bottom

    def play_move_now(self) -> None:
        """Force engine to play move, despite not being on turn."""
        self.invoke_engine()

    def show_settings_dialog(self) -> None:
        """Show dialog to edit settings."""
        settings_dialog: SettingsDialog = SettingsDialog()

        if settings_dialog.exec() == QDialog.DialogCode.Accepted:
            self.apply_saved_settings()

    def apply_saved_settings(self) -> None:
        """Act on settings being saved."""
        if self.should_flip():
            self.flip()
            self.invoke_engine()

    def apply_style(self, filename: str) -> None:
        """Apply style from QSS file at `filename` and set setting."""
        with open(f"rechess/assets/styles/{filename}.qss") as qss_file:
            self.setStyleSheet(qss_file.read())
        set_setting_value("ui", "style", filename)

    def load_engine(self) -> None:
        """Show file manager to load engine."""
        path_to_file, _ = QFileDialog.getOpenFileName(
            self,
            "File Manager",
            Path.home().as_posix(),
            "Chess engine (*.exe)",
        )

        if path_to_file:
            self.start_new_engine(path_to_file)

    def start_new_engine(self, path_to_file: str) -> None:
        """Start new engine from file at `path_to_file`."""
        self.stop_analysis()

        self._game.clear_arrows()
        self._engine_analysis_label.clear()
        self._evaluation_bar.reset_appearance()

        self._engine.load_from_file_at(path_to_file)
        self._engine_name_label.setText(self._engine.name)

        if self._game.is_engine_on_turn() and not self._game.is_over():
            self.invoke_engine()

    def show_about(self) -> None:
        """Show About dialog."""
        QMessageBox.about(
            self,
            "About",
            (
                "This is a UI-based app for playing chess.\n\n"
                "Copyright 2024 Boštjan Mejak\n"
                "MIT License"
            ),
        )

    def flip_clocks(self) -> None:
        """Flip positions of Black's and White's clock."""
        top_clock: QWidget = self._grid_layout.itemAtPosition(1, 1).widget()
        bottom_clock: QWidget = self._grid_layout.itemAtPosition(4, 1).widget()

        self._grid_layout.removeWidget(top_clock)
        self._grid_layout.removeWidget(bottom_clock)

        self._grid_layout.addWidget(top_clock, 4, 1)
        self._grid_layout.addWidget(bottom_clock, 1, 1)

    def flip_player_names(self) -> None:
        """Flip positions of engine and human player name."""
        top_name: QWidget = self._grid_layout.itemAtPosition(2, 1).widget()
        bottom_name: QWidget = self._grid_layout.itemAtPosition(5, 1).widget()

        self._grid_layout.removeWidget(top_name)
        self._grid_layout.removeWidget(bottom_name)

        self._grid_layout.addWidget(top_name, 5, 1)
        self._grid_layout.addWidget(bottom_name, 2, 1)

    def start_analysis(self) -> None:
        """Start analyzing current position."""
        self.invoke_analysis()

        self._black_clock.stop_timer()
        self._white_clock.stop_timer()

        self.stop_analysis_action.setEnabled(True)
        self.start_analysis_action.setDisabled(True)

    def stop_analysis(self) -> None:
        """Stop analyzing current position."""
        self._engine.stop_analysis()

        self.switch_clock_timers()
        self.adjust_toolbar_buttons()

    def show_fen(self) -> None:
        """Show FEN in editor."""
        self._fen_editor.clearFocus()
        self._fen_editor.hide_warning()
        self._fen_editor.setText(self._game.fen)

    def show_opening(self) -> None:
        """Show ECO code and opening name."""
        opening: tuple[str, str] | None = find_opening(self._game.fen)

        if opening:
            eco_code, opening_name = opening
            self._openings_label.setText(f"{eco_code}: {opening_name}")

    def refresh_ui(self) -> None:
        """Refresh current state of UI."""
        self._table_model.refresh_view()
        self._table_view.select_last_item()

        self._notifications_label.clear()
        self._engine_analysis_label.clear()
        self._evaluation_bar.reset_appearance()

        self.show_fen()
        self.show_opening()
        self.stop_analysis()

        if self._game.is_over():
            self._black_clock.stop_timer()
            self._white_clock.stop_timer()
            self._notifications_label.setText(self._game.result)
            return

        if self._game.is_engine_on_turn() and not self._game.is_over():
            self.invoke_engine()

    def offer_new_game(self) -> None:
        """Show dialog offering to start new game."""
        answer: QMessageBox.StandardButton = QMessageBox.question(
            self,
            "New game",
            "Do you want to start a new game?",
        )

        if answer == answer.Yes:
            self.start_new_game()

    def start_new_game(self) -> None:
        """Start new game by resetting and clearing everything."""
        self._game.prepare_new_game()

        self._black_clock.reset()
        self._white_clock.reset()

        self._table_model.reset()
        self._evaluation_bar.reset()

        self._openings_label.clear()
        self._notifications_label.clear()
        self._engine_analysis_label.clear()

        self.show_fen()
        self.stop_analysis()

        if self.should_flip():
            self.flip()
            self.invoke_engine()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Ask whether to quit by closing main window."""
        answer: QMessageBox.StandardButton = QMessageBox.question(
            self,
            "Quit",
            "Do you really want to quit?",
        )

        if answer == answer.Yes:
            self._engine.quit()
            event.accept()
        else:
            event.ignore()

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Select item in table view on mouse wheel scroll."""
        wheel_step: int = event.angleDelta().y()

        if wheel_step > 0:
            self._table_view.select_previous_item()
        elif wheel_step < 0:
            self._table_view.select_next_item()

    @Slot(Move)
    def on_best_move_analyzed(self, best_move: Move) -> None:
        """Show `best_move` as arrow marker based on engine analysis."""
        self._game.show_arrow(best_move)

    @Slot()
    def on_black_time_expired(self) -> None:
        """Notify that White won as Black's time has expired."""
        self._notifications_label.setText("White won on time")

    @Slot()
    def on_white_time_expired(self) -> None:
        """Notify that Black won as White's time has expired."""
        self._notifications_label.setText("Black won on time")

    @Slot()
    def on_fen_validated(self) -> None:
        """Refresh UI after FEN has been validated."""
        self.refresh_ui()

    @Slot(int)
    def on_item_selected(self, item_index: int) -> None:
        """Set move based on `item_index`."""
        if item_index > -1:
            self._game.set_move(item_index)
        else:
            self._game.clear_arrows()
            self._game.set_root_position()
            self._openings_label.clear()

        self.show_fen()
        self.show_opening()
        self.stop_analysis()
        self._game.reset_squares()
        self._black_clock.stop_timer()
        self._white_clock.stop_timer()
        self._notifications_label.clear()
        self._engine_analysis_label.clear()
        self._evaluation_bar.reset_appearance()

        if self._game.is_over():
            self._notifications_label.setText(self._game.result)

    @Slot(Move)
    def on_move_played(self, move: Move) -> None:
        """Play `move` and refresh UI."""
        if self._game.is_legal(move):
            self._game.delete_data_after(self._table_view.item_index)
            self._game.push(move)
            self.refresh_ui()

    @Slot(str)
    def on_variation_analyzed(self, variation: str) -> None:
        """Show `variation` based on engine analysis."""
        self._engine_analysis_label.setText(variation)

    @Slot(Score)
    def on_score_analyzed(self, score: Score) -> None:
        """Show position evaluation based on `score`."""
        self._evaluation_bar.animate(score)