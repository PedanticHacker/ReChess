from functools import partial
from pathlib import Path

from chess import BLACK, Move
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
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from rechess.core import Engine, Game
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


Bottom: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignBottom
Top: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignTop


class MainWindow(QMainWindow):
    """Main window containing all widgets."""

    def __init__(self) -> None:
        super().__init__()

        self.apply_style("dark-forest")

        self._game: Game = Game()
        self._engine: Engine = Engine(self._game)

        self._table_model: TableModel = TableModel(self._game.san_moves)
        self._table_view: TableView = TableView(self._table_model)

        self._black_clock: Clock = Clock(ClockColor.Black)
        self._white_clock: Clock = Clock(ClockColor.White)

        self._board: Board = Board(self._game)
        self._evaluation_bar: EvaluationBar = EvaluationBar()
        self._fen_editor: FenEditor = FenEditor(self._game.board)

        self._engine_name_label: QLabel = QLabel()
        self._openings_label: QLabel = QLabel()

        self._notifications_label: QLabel = QLabel()
        self._notifications_label.setObjectName("notifications")
        self._notifications_label.setFixedWidth(self._table_view.width())

        self._engine_analysis_label: QLabel = QLabel()
        self._engine_analysis_label.setAlignment(Top)
        self._engine_analysis_label.setWordWrap(True)

        self.create_actions()
        self.create_menubar()
        self.create_toolbar()
        self.set_grid_layout()
        self.create_statusbar()
        self.set_minimum_size()
        self.switch_clock_timers()
        self.adjust_engine_buttons()
        self.connect_signals_to_slots()

        if self._game.is_engine_on_turn():
            self.invoke_engine()

    def create_actions(self) -> None:
        """Create actions for menubar menus or toolbar buttons."""
        self.about_action = create_action(
            handler=self.show_about,
            icon=svg_icon("about"),
            name="About ReChess",
            shortcut="F1",
            status_tip="Shows info about ReChess, copyright, and license.",
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
            status_tip="Flips the chessboard and its related widgets.",
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
            status_tip="Shows the file manager to load a UCI chess engine.",
        )
        self.new_game_action = create_action(
            handler=self.offer_new_game,
            icon=svg_icon("new-game"),
            name="New game",
            shortcut="Ctrl+N",
            status_tip="Shows a dialog offering to start a new chess game.",
        )
        self.play_move_now_action = create_action(
            handler=self.play_move_now,
            icon=svg_icon("play-move-now"),
            name="Play move now",
            shortcut="Ctrl+P",
            status_tip="Forces the UCI chess engine to play on current turn.",
        )
        self.quit_action = create_action(
            handler=self.quit,
            icon=svg_icon("quit"),
            name="Quit...",
            shortcut="Ctrl+Q",
            status_tip="Offers to quit ReChess.",
        )
        self.settings_action = create_action(
            handler=self.show_settings_dialog,
            icon=svg_icon("settings"),
            name="Settings...",
            shortcut="Ctrl+,",
            status_tip="Shows the Settings dialog to edit app settings.",
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

    def set_grid_layout(self) -> None:
        """Set grid layout for widgets on main window."""
        self._grid_layout: QGridLayout = QGridLayout()
        self._grid_layout.addWidget(self._black_clock, 0, 0, 1, 1, Top)
        self._grid_layout.addWidget(self._white_clock, 0, 0, 1, 1, Bottom)
        self._grid_layout.addWidget(self._board, 0, 1, 1, 1)
        self._grid_layout.addWidget(self._evaluation_bar, 0, 2, 1, 1)
        self._grid_layout.addWidget(self._table_view, 0, 3, 1, 2)
        self._grid_layout.addWidget(self._notifications_label, 1, 3, 1, 1)
        self._grid_layout.addWidget(self._fen_editor, 1, 1, 1, 1)
        self._grid_layout.addWidget(self._engine_analysis_label, 2, 1, 1, 1)

        self._widget_container: QWidget = QWidget()
        self._widget_container.setLayout(self._grid_layout)
        self.setCentralWidget(self._widget_container)

        if setting_value("board", "orientation") == BLACK:
            self.flip_clock_alignments()

    def create_statusbar(self) -> None:
        """Create statusbar for displaying various info."""
        self.statusBar().addWidget(self._openings_label)
        self.statusBar().addPermanentWidget(self._engine_name_label)
        self._engine_name_label.setText(self._engine.name)

    def set_minimum_size(self) -> None:
        """Set minimum size to be 1000 by 700 pixels."""
        self.setMinimumSize(1000, 700)

    def switch_clock_timers(self) -> None:
        """Activate clock timer for player on turn."""
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

    def adjust_engine_buttons(self) -> None:
        """Adjust state of UCI chess engine's toolbar buttons."""
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
        """Invoke UCI chess engine to play move."""
        QThreadPool.globalInstance().start(self._engine.play_move)
        self._notifications_label.setText("Thinking...")

    def invoke_analysis(self) -> None:
        """Invoke UCI chess engine to start analysis."""
        QThreadPool.globalInstance().start(self._engine.start_analysis)
        self._notifications_label.setText("Analyzing...")

    def show_maximized(self) -> None:
        """Show main window in maximized size."""
        self.showMaximized()

    def quit(self) -> None:
        """Trigger main window's close event to quit ReChess."""
        self.close()

    def flip(self) -> None:
        """Flip board and its related widgets."""
        flipped_orientation: bool = not setting_value("board", "orientation")
        set_setting_value("board", "orientation", flipped_orientation)

        self.flip_clock_alignments()
        self._evaluation_bar.flip_appearance()

    def play_move_now(self) -> None:
        """Force UCI chess engine to play move on current turn."""
        set_setting_value("engine", "is_white", self._game.turn)
        self.invoke_engine()

    def show_settings_dialog(self) -> None:
        """Show dialog to edit settings and apply them if saved."""
        settings_dialog: SettingsDialog = SettingsDialog()
        settings_dialog.set_groups_disabled(self._game.is_in_progress())

        if settings_dialog.exec() == QDialog.DialogCode.Accepted:
            self.apply_saved_settings()

    def apply_saved_settings(self) -> None:
        """Act on settings being saved by applying them."""
        if not self._game.is_in_progress():
            self._black_clock.reset()
            self._white_clock.reset()

        if self._game.is_engine_on_turn() and not self._game.is_over():
            self.invoke_engine()

    def apply_style(self, filename: str) -> None:
        """Apply style from QSS file with `filename`."""
        with open(f"rechess/assets/styles/{filename}.qss") as qss_file:
            self.setStyleSheet(qss_file.read())

    def load_engine(self) -> None:
        """Show file manager to load UCI chess engine."""
        path_to_file, _ = QFileDialog.getOpenFileName(
            self,
            "File Manager",
            Path.home().as_posix(),
            "UCI chess engine (*.exe)" if platform_name() == "windows" else "",
        )

        if path_to_file:
            self.start_new_engine(path_to_file)

    def start_new_engine(self, path_to_file: str) -> None:
        """Start new UCI chess engine from file at `path_to_file`."""
        self.stop_analysis()

        self._game.clear_arrows()
        self._engine_analysis_label.clear()
        self._evaluation_bar.reset_appearance()

        self._engine.load_from_file_at(path_to_file)
        self._engine_name_label.setText(self._engine.name)

        if self._game.is_engine_on_turn() and not self._game.is_over():
            self.invoke_engine()

    def show_about(self) -> None:
        """Show info about ReChess, copyright, and license."""
        QMessageBox.about(
            self,
            "About",
            (
                "App for playing chess against a UCI engine.\n\n"
                "Copyright 2024 Boštjan Mejak\n"
                "MIT License"
            ),
        )

    def flip_clock_alignments(self) -> None:
        """Flip alignments of top and bottom clocks."""
        if Top in self._grid_layout.itemAt(0).alignment():
            self._grid_layout.itemAt(0).setAlignment(Bottom)
            self._grid_layout.itemAt(1).setAlignment(Top)
        else:
            self._grid_layout.itemAt(0).setAlignment(Top)
            self._grid_layout.itemAt(1).setAlignment(Bottom)

        self._grid_layout.update()

    def start_analysis(self) -> None:
        """Start analyzing current position."""
        self.invoke_analysis()
        self._evaluation_bar.show()
        self._black_clock.stop_timer()
        self._white_clock.stop_timer()
        self.stop_analysis_action.setEnabled(True)
        self.start_analysis_action.setDisabled(True)

    def stop_analysis(self) -> None:
        """Stop analyzing current position."""
        self._engine.stop_analysis()

        self.switch_clock_timers()
        self.adjust_engine_buttons()
        self._notifications_label.clear()

    def show_fen(self) -> None:
        """Show FEN in FEN editor."""
        self._fen_editor.setText(self._game.fen)
        self._fen_editor.hide_warning()
        self._fen_editor.clearFocus()

    def show_opening(self) -> None:
        """Show ECO code and opening name."""
        opening: tuple[str, str] | None = find_opening(self._game.fen)

        if opening:
            eco_code, opening_name = opening
            self._openings_label.setText(f"{eco_code}: {opening_name}")

    def refresh_ui(self) -> None:
        """Refresh current state of UI."""
        self.stop_analysis()

        self._table_model.refresh_view()
        self._engine_analysis_label.clear()
        self._table_view.select_last_item()

        self._evaluation_bar.reset_appearance()

        self.show_fen()
        self.show_opening()
        self.switch_clock_timers()

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
        """Start new game by resetting everything."""
        if setting_value("board", "orientation") == BLACK:
            self.flip()

        self._black_clock.reset()
        self._white_clock.reset()
        self._openings_label.clear()

        self._game.set_new_game()
        self._table_model.reset()

        self._engine_analysis_label.clear()
        self._evaluation_bar.reset_appearance()

        self.show_fen()
        self.stop_analysis()
        self.switch_clock_timers()

        if self._game.is_engine_on_turn():
            self.invoke_engine()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Ask whether to quit by closing main window."""
        answer: QMessageBox.StandardButton = QMessageBox.question(
            self,
            "Quit",
            "Do you want to quit?",
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
        """Based on engine analysis, show `best_move` as arrow."""
        self._game.set_arrow(best_move)

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
        self._black_clock.stop_timer()
        self._white_clock.stop_timer()
        self._engine_analysis_label.clear()

        self._evaluation_bar.reset_appearance()

        if self._game.is_over():
            self._notifications_label.setText(self._game.result)

    @Slot(Move)
    def on_move_played(self, move: Move) -> None:
        """Play `move` by pushing it and refreshing UI."""
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
