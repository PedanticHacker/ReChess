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

from rechess.core import Game, TableModel
from rechess.enums import ClockColor
from rechess.gui.dialogs import SettingsDialog
from rechess.gui.widgets import (
    Clock,
    EvaluationBar,
    FenEditor,
    SvgBoard,
    TableView,
)
from rechess.uci import Engine
from rechess.utils import (
    chess_openings,
    create_action,
    svg_icon,
    set_setting_value,
    setting_value,
)


class MainWindow(QMainWindow):
    """The main window of the app."""

    def __init__(self) -> None:
        super().__init__()

        self._game: Game = Game()

        self._engine: Engine = Engine(self._game)

        self._svg_board: SvgBoard = SvgBoard(self._game)
        self._fen_editor: FenEditor = FenEditor(self._game)
        self._evaluation_bar: EvaluationBar = EvaluationBar(self._game)

        self._black_clock: Clock = Clock(ClockColor.Black)
        self._white_clock: Clock = Clock(ClockColor.White)

        self._table_model: TableModel = TableModel(self._game.notation_items)
        self._table_view: TableView = TableView(self._table_model)

        self._chess_opening_label: QLabel = QLabel()
        self._engine_name_label: QLabel = QLabel()
        self._notifications_label: QLabel = QLabel()

        self._engine_analysis_label: QLabel = QLabel()
        self._engine_analysis_label.setWordWrap(True)

        self._settings_dialog: SettingsDialog = SettingsDialog()

        self.create_actions()
        self.create_menubar()
        self.create_toolbar()
        self.set_grid_layout()
        self.set_minimum_size()
        self.create_status_bar()
        self.switch_clock_timers()
        self.adjust_engine_buttons()
        self.connect_signals_to_slots()

    def create_actions(self) -> None:
        """Create actions to be used by a menubar and a toolbar."""
        self.about_action = create_action(
            name="About",
            shortcut="Ctrl+I",
            icon=svg_icon("about"),
            handler=self.show_about,
            status_tip="Show the app's description, copyright, and license.",
        )
        self.flip_action = create_action(
            name="Flip",
            handler=self.flip,
            icon=svg_icon("flip"),
            shortcut="Ctrl+Shift+F",
            status_tip="Flips the chessboard and its related widgets.",
        )
        self.load_engine_action = create_action(
            shortcut="Ctrl+E",
            name="Load engine...",
            handler=self.load_engine,
            icon=svg_icon("load-engine"),
            status_tip="Shows the file manager to load a UCI chess engine.",
        )
        self.new_game_action = create_action(
            name="New game",
            shortcut="Ctrl+Shift+N",
            icon=svg_icon("new-game"),
            handler=self.offer_new_game,
            status_tip="Offers a new game.",
        )
        self.play_move_now_action = create_action(
            name="Play move now",
            shortcut="Ctrl+Shift+P",
            handler=self.play_move_now,
            icon=svg_icon("play-move-now"),
            status_tip="Forces the loaded chess engine to play a move now.",
        )
        self.settings_action = create_action(
            name="Settings...",
            shortcut="Ctrl+Shift+S",
            icon=svg_icon("settings"),
            handler=self.show_settings_dialog,
            status_tip="Shows the Settings dialog to edit the app's settings.",
        )
        self.start_analysis_action = create_action(
            name="Start analysis",
            shortcut="Ctrl+Shift+A",
            handler=self.start_analysis,
            icon=svg_icon("start-analysis"),
            status_tip="Starts analyzing the current chessboard position.",
        )
        self.stop_analysis_action = create_action(
            name="Stop analysis",
            shortcut="Ctrl+Shift+X",
            handler=self.stop_analysis,
            icon=svg_icon("stop-analysis"),
            status_tip="Stops analyzing the current chessboard position.",
        )
        self.quit_action = create_action(
            name="Quit...",
            handler=self.quit,
            shortcut="Ctrl+Q",
            icon=svg_icon("quit"),
            status_tip="Offers to quit the app.",
        )

    def create_menubar(self) -> None:
        """Create a menubar with actions in separate menus."""

        # Menubar
        menubar = self.menuBar()

        # General menu
        general_menu = menubar.addMenu("General")

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

        # Edit menu > Settings...
        edit_menu.addAction(self.settings_action)

        # Help menu > About
        help_menu.addAction(self.about_action)

    def create_toolbar(self) -> None:
        """Create a toolbar with buttons in separate areas."""

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

    def create_status_bar(self) -> None:
        """Create a status bar to show various information."""
        self.statusBar().addWidget(self._chess_opening_label)
        self.statusBar().addPermanentWidget(self._engine_name_label)
        self._engine_name_label.setText(self._engine.name)

    def switch_clock_timers(self) -> None:
        """Activate the clock's timer for the player on turn."""
        if self._game.is_white_on_turn():
            self._black_clock.stop_timer()
            self._white_clock.start_timer()
        else:
            self._white_clock.stop_timer()
            self._black_clock.start_timer()

    def set_grid_layout(self) -> None:
        """Set a grid layout for widgets on the main window."""
        self._grid_layout: QGridLayout = QGridLayout()
        self._grid_layout.addWidget(
            self._black_clock, 0, 0, 1, 1, Qt.AlignmentFlag.AlignTop
        )
        self._grid_layout.addWidget(
            self._white_clock, 0, 0, 1, 1, Qt.AlignmentFlag.AlignBottom
        )
        self._grid_layout.addWidget(self._svg_board, 0, 1, 1, 1)
        self._grid_layout.addWidget(self._evaluation_bar, 0, 2, 1, 1)
        self._grid_layout.addWidget(self._table_view, 0, 3, 1, 2)
        self._grid_layout.addWidget(self._notifications_label, 1, 3, 1, 1)
        self._grid_layout.addWidget(self._fen_editor, 1, 1, 1, 1)
        self._grid_layout.addWidget(
            self._engine_analysis_label, 2, 1, 1, 1, Qt.AlignmentFlag.AlignTop
        )

        self._widget_container: QWidget = QWidget()
        self._widget_container.setLayout(self._grid_layout)
        self.setCentralWidget(self._widget_container)

        if setting_value("board", "orientation") == BLACK:
            self.flip_clock_alignments()

    def set_minimum_size(self) -> None:
        """Set a minimum size to be 1000 by 700 pixels."""
        self.setMinimumSize(1000, 700)

    def adjust_engine_buttons(self) -> None:
        """Adjust the state of the engine's tool bar buttons."""
        self.play_move_now_action.setEnabled(True)
        self.start_analysis_action.setEnabled(True)
        self.stop_analysis_action.setDisabled(True)

        if self._game.is_game_over():
            self.play_move_now_action.setDisabled(True)
            self.stop_analysis_action.setDisabled(True)
            self.start_analysis_action.setDisabled(True)

    def connect_signals_to_slots(self) -> None:
        self._game.move_played.connect(self.on_move_played)
        self._engine.move_played.connect(self.on_move_played)
        self._fen_editor.validated.connect(self.on_fen_validated)
        self._table_view.item_selected.connect(self.on_item_selected)
        self._engine.best_move_analyzed.connect(self.on_best_move_analyzed)
        self._engine.white_score_analyzed.connect(self.on_white_score_analyzed)
        self._black_clock.time_expired.connect(self.on_black_clock_time_expired)
        self._white_clock.time_expired.connect(self.on_white_clock_time_expired)
        self._engine.san_variation_analyzed.connect(self.on_san_variation_analyzed)

    def invoke_engine(self) -> None:
        """Invoke the loaded engine to play a move."""
        QThreadPool.globalInstance().start(self._engine.play_move)

    def invoke_analysis(self) -> None:
        """Invoke the loaded engine to start an analysis."""
        QThreadPool.globalInstance().start(self._engine.start_analysis)

    def show_maximized(self) -> None:
        """Show the main window in maximized size."""
        self.showMaximized()

    def quit(self) -> None:
        """Trigger the main window's close event."""
        self.close()

    def flip(self) -> None:
        """Flip the chessboard and its related widgets."""
        flipped_orientation: bool = not setting_value("board", "orientation")
        set_setting_value("board", "orientation", flipped_orientation)

        self.flip_clock_alignments()
        self._evaluation_bar.flip_appearance()
        self._svg_board.draw()

    def play_move_now(self) -> None:
        """Force the loaded chess engine to play a move now."""
        self.invoke_engine()

    def show_settings_dialog(self) -> None:
        """Show the Settings dialog to edit the app's settings."""
        self._settings_dialog.disable_groups_if(self._game.playing)

        if self._settings_dialog.exec() == QDialog.DialogCode.Accepted:
            self._black_clock.reset()
            self._white_clock.reset()

    def load_engine(self) -> None:
        """Show the file manager to load a UCI chess engine."""
        engine_file, _ = QFileDialog.getOpenFileName(
            self,
            "File Manager",
            Path.home().as_posix(),
            "UCI chess engine (*.exe)",
        )

        if engine_file:
            self.start_new_engine(engine_file)

    def start_new_engine(self, engine_file: str) -> None:
        """Start a new chess engine from the `engine_file`."""
        self.stop_analysis()
        self._game.arrow.clear()
        self._engine_analysis_label.clear()
        self._evaluation_bar.reset_appearance()

        self._engine.load(engine_file)
        self._engine_name_label.setText(self._engine.name)

        self._svg_board.draw()

        if self._game.is_engine_on_turn():
            self.invoke_engine()

    def show_about(self) -> None:
        """Show the app's description, copyright, and license."""
        QMessageBox.about(
            self,
            "About",
            (
                "A GUI app for playing chess against a UCI chess engine.\n\n"
                "Copyright 2024 Boštjan Mejak\n"
                "MIT License"
            ),
        )

    def flip_clock_alignments(self) -> None:
        """Flip the alignments of the top and bottom chess clocks."""
        if Qt.AlignmentFlag.AlignTop in self._grid_layout.itemAt(0).alignment():
            self._grid_layout.itemAt(0).setAlignment(Qt.AlignmentFlag.AlignBottom)
            self._grid_layout.itemAt(1).setAlignment(Qt.AlignmentFlag.AlignTop)
        else:
            self._grid_layout.itemAt(0).setAlignment(Qt.AlignmentFlag.AlignTop)
            self._grid_layout.itemAt(1).setAlignment(Qt.AlignmentFlag.AlignBottom)

        self._grid_layout.update()

    def start_analysis(self) -> None:
        """Start analyzing current chessboard position."""
        self.invoke_analysis()
        self._evaluation_bar.show()
        self.stop_analysis_action.setEnabled(True)
        self.start_analysis_action.setDisabled(True)

    def stop_analysis(self) -> None:
        """Stop analyzing current chessboard position."""
        self._engine.stop_analysis()
        self.adjust_engine_buttons()

    def show_fen(self) -> None:
        """Show FEN in FEN editor."""
        self._fen_editor.reset_background_color()
        self._fen_editor.setText(self._game.fen)

    def display_chess_opening(self) -> None:
        """Display ECO code and chess opening name."""
        fen: str = self._game.fen
        chess_openings_storage: dict[str, tuple[str, str]] = chess_openings()

        if fen in chess_openings_storage:
            eco_code, chess_opening_name = chess_openings_storage[fen]
            self._chess_opening_label.setText(f"{eco_code}: {chess_opening_name}")

    def refresh_ui(self) -> None:
        """Refresh the current state of the UI."""
        self._engine.stop_analysis()
        self._table_model.refresh_view()
        self._table_view.select_last_item()
        self._engine_analysis_label.clear()
        self._evaluation_bar.reset_appearance()

        self.show_fen()
        self.switch_clock_timers()
        self.adjust_engine_buttons()
        self.display_chess_opening()

        self._svg_board.draw()

        if self._game.is_game_over():
            self._black_clock.stop_timer()
            self._white_clock.stop_timer()
            self._notifications_label.setText(self._game.result)
            self.offer_new_game()
            return

        if self._game.is_engine_on_turn():
            self.invoke_engine()

    def offer_new_game(self) -> None:
        """Show a dialog offering to start a new game."""
        answer: QMessageBox.StandardButton = QMessageBox.question(
            self,
            "New Game",
            "Do you want to start a new game?",
        )

        if answer == answer.Yes:
            self.start_new_game()

    def start_new_game(self) -> None:
        """Start a new game by resetting everything."""
        if setting_value("board", "orientation") == BLACK:
            self.flip_clock_alignments()

        self._black_clock.reset()
        self._white_clock.reset()
        self._chess_opening_label.clear()

        self._game.set_new_game()
        self._table_model.reset()
        self._engine.stop_analysis()
        self._notifications_label.clear()
        self._engine_analysis_label.clear()
        self._evaluation_bar.reset_appearance()

        self.show_fen()
        self.switch_clock_timers()
        self.adjust_engine_buttons()

        self._svg_board.draw()

        if self._game.is_engine_on_turn():
            self.invoke_engine()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Ask whether to quit the app by closing the main window."""
        answer: QMessageBox.StandardButton = QMessageBox.question(
            self,
            "Quit App",
            "Do you want to quit the app?",
        )

        if answer == answer.Yes:
            self._engine.quit()
            event.accept()
        else:
            event.ignore()

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Select a notation item upon a mouse wheel roll."""
        is_upward_roll = event.angleDelta().y() > 0
        is_downward_roll = event.angleDelta().y() < 0

        if is_upward_roll:
            self._table_view.select_previous_item()
        elif is_downward_roll:
            self._table_view.select_next_item()

    @Slot(Move)
    def on_best_move_analyzed(self, best_move: Move) -> None:
        """Show the `best_move` from chess engine analysis."""
        self._game.set_arrow_for(best_move)
        self._svg_board.draw()

    @Slot()
    def on_black_clock_time_expired(self) -> None:
        """Notify that White won as Black's clock time has expired."""
        self._notifications_label.setText("White won on time")

    @Slot()
    def on_white_clock_time_expired(self) -> None:
        """Notify that Black won as White's clock time has expired."""
        self._notifications_label.setText("Black won on time")

    @Slot()
    def on_fen_validated(self) -> None:
        """Update chessboard position based on validated FEN."""
        self._svg_board.draw()

    @Slot(int)
    def on_item_selected(self, ply_index: int) -> None:
        """Select notation index with `ply_index`."""
        if ply_index > -1:
            self._game.set_move_with(ply_index)
        else:
            self._game.clear_arrow()
            self._game.set_root_position()
            self._chess_opening_label.clear()

        self._svg_board.draw()

    @Slot(Move)
    def on_move_played(self, move: Move) -> None:
        """Play `move` by pushing it and refreshing UI."""
        if self._game.is_legal(move):
            self._game.delete_data_after(self._table_view.ply_index)
            self._game.push(move)
            self.refresh_ui()

    @Slot(str)
    def on_san_variation_analyzed(self, san_variation: str) -> None:
        """Show `san_variation` from chess engine analysis."""
        self._engine_analysis_label.setText(san_variation)

    @Slot(Score)
    def on_white_score_analyzed(self, white_score: Score) -> None:
        """Show chessboard position evaluation from `white_score`."""
        self._evaluation_bar.animate(white_score)
