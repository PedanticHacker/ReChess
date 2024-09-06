from pathlib import Path

from chess import BLACK, Board, Move
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

from rechess.chess import chess_openings
from rechess.game import ClassicGame
from rechess.gui.dialogs import SettingsDialog
from rechess.gui.table import TableModel, TableView
from rechess.gui.widgets import (
    ChessClockWidget,
    EvaluationBarWidget,
    FenEditorWidget,
    SvgBoardWidget,
)
from rechess.types import ClockColor, Engine, Game
from rechess.uci import UciEngine
from rechess.utils import (
    create_action,
    svg_icon,
    set_setting_value,
    setting_value,
)


Bottom: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignBottom
Top: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignTop


class MainWindow(QMainWindow):
    """Main window containing all widgets."""

    def __init__(self) -> None:
        super().__init__()

        self._game: Game = ClassicGame(Board())
        self._engine: Engine = UciEngine(self._game)
        self._table_model: TableModel = TableModel(self._game.notation_items)

        self._black_clock: ChessClockWidget = ChessClockWidget(ClockColor.Black)
        self._white_clock: ChessClockWidget = ChessClockWidget(ClockColor.White)

        self._svg_board: SvgBoardWidget = SvgBoardWidget(self._game)
        self._fen_editor: FenEditorWidget = FenEditorWidget(self._game.board)
        self._table_view: TableView = TableView(self._table_model)
        self._evaluation_bar: EvaluationBarWidget = EvaluationBarWidget()

        self._engine_name_label: QLabel = QLabel()
        self._chess_opening_label: QLabel = QLabel()

        self._notifications_label: QLabel = QLabel()
        self._notifications_label.setFixedWidth(self._table_view.width())

        self._engine_analysis_label: QLabel = QLabel()
        self._engine_analysis_label.setAlignment(Top)
        self._engine_analysis_label.setWordWrap(True)

        self._settings_dialog: SettingsDialog = SettingsDialog()

        self.create_actions()
        self.create_menubar()
        self.create_toolbar()
        self.set_grid_layout()
        self.create_statusbar()
        self.set_minimum_size()
        self.switch_clock_timers()
        self.adjust_engine_buttons()
        self.connect_signals_to_slots()

    def create_actions(self) -> None:
        """Create actions to be used by menubar and toolbar."""
        self.about_action = create_action(
            name="About",
            shortcut="Ctrl+I",
            icon=svg_icon("about"),
            handler=self.show_about,
            status_tip="Shows app description, copyright, and license.",
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
            status_tip="Shows the file manager to load a chess engine.",
        )
        self.new_game_action = create_action(
            name="New game",
            shortcut="Ctrl+Shift+N",
            icon=svg_icon("new-game"),
            handler=self.offer_new_game,
            status_tip="Offers to start a new game.",
        )
        self.play_move_now_action = create_action(
            name="Play move now",
            shortcut="Ctrl+Shift+P",
            handler=self.play_move_now,
            icon=svg_icon("play-move-now"),
            status_tip="Forces the chess engine to play on the current turn.",
        )
        self.settings_action = create_action(
            name="Settings...",
            shortcut="Ctrl+Shift+S",
            icon=svg_icon("settings"),
            handler=self.show_settings_dialog,
            status_tip="Shows the Settings dialog to edit app settings.",
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
        """Create menubar with actions in separate menus."""

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
        self._grid_layout.addWidget(self._svg_board, 0, 1, 1, 1)
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
        self.statusBar().addWidget(self._chess_opening_label)
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
        """Adjust state of chess engine's toolbar buttons."""
        self.play_move_now_action.setEnabled(True)
        self.start_analysis_action.setEnabled(True)
        self.stop_analysis_action.setDisabled(True)

        if self._game.is_over():
            self.play_move_now_action.setDisabled(True)
            self.stop_analysis_action.setDisabled(True)
            self.start_analysis_action.setDisabled(True)

    def connect_signals_to_slots(self) -> None:
        """Connect component signals to corresponding slot methods."""
        self._engine.move_played.connect(self.on_move_played)
        self._engine.variation_analyzed.connect(self.on_variation_analyzed)
        self._engine.best_move_analyzed.connect(self.on_best_move_analyzed)
        self._engine.score_analyzed.connect(self.on_score_analyzed)

        self._game.move_played.connect(self.on_move_played)
        self._fen_editor.validated.connect(self.on_fen_validated)
        self._table_view.item_selected.connect(self.on_item_selected)

        self._black_clock.time_expired.connect(self.on_black_clock_time_expired)
        self._white_clock.time_expired.connect(self.on_white_clock_time_expired)

    def invoke_engine(self) -> None:
        """Invoke loaded chess engine to play move."""
        QThreadPool.globalInstance().start(self._engine.play_move)

    def invoke_analysis(self) -> None:
        """Invoke loaded chess engine to start analysis."""
        QThreadPool.globalInstance().start(self._engine.start_analysis)

    def show_maximized(self) -> None:
        """Show main window in maximized size."""
        self.showMaximized()

    def quit(self) -> None:
        """Trigger main window's close event."""
        self.close()

    def flip(self) -> None:
        """Flip chessboard and its related widgets."""
        flipped_orientation: bool = not setting_value("board", "orientation")
        set_setting_value("board", "orientation", flipped_orientation)

        self.flip_clock_alignments()
        self._evaluation_bar.flip_appearance()
        self._svg_board.draw()

    def play_move_now(self) -> None:
        """Force chess engine to play on current turn."""
        set_setting_value("engine", "is_white", self._game.turn)
        self.invoke_engine()

    def show_settings_dialog(self) -> None:
        """Show Settings dialog to edit settings and apply if saved."""
        self._settings_dialog.set_groups_disabled(self._game.is_in_progress())

        if self._settings_dialog.exec() == QDialog.DialogCode.Accepted:
            self.apply_saved_settings()

    def apply_saved_settings(self) -> None:
        """Act on settings being saved by applying them."""
        if not self._game.is_in_progress():
            self._black_clock.reset()
            self._white_clock.reset()

        if self._game.is_engine_on_turn() and not self._game.is_over():
            self.invoke_engine()

    def load_engine(self) -> None:
        """Show file manager to load chess engine."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "File Manager",
            Path.home().as_posix(),
            "Chess engine (*.exe)",
        )

        if file_path:
            self.start_new_engine(file_path)

    def start_new_engine(self, file_path: str) -> None:
        """Start new chess engine from `file_path`."""
        self.stop_analysis()
        self._game.clear_arrows()
        self._engine_analysis_label.clear()
        self._evaluation_bar.reset_appearance()

        self._engine.load(file_path)
        self._engine_name_label.setText(self._engine.name)

        self._svg_board.draw()

        if self._game.is_engine_on_turn() and not self._game.is_over():
            self.invoke_engine()

    def show_about(self) -> None:
        """Show app description, copyright, and license."""
        QMessageBox.about(
            self,
            "About",
            (
                "A GUI app for playing chess against a chess engine.\n\n"
                "Copyright 2024 Boštjan Mejak\n"
                "MIT License"
            ),
        )

    def flip_clock_alignments(self) -> None:
        """Flip alignments of top and bottom chess clocks."""
        if Top in self._grid_layout.itemAt(0).alignment():
            self._grid_layout.itemAt(0).setAlignment(Bottom)
            self._grid_layout.itemAt(1).setAlignment(Top)
        else:
            self._grid_layout.itemAt(0).setAlignment(Top)
            self._grid_layout.itemAt(1).setAlignment(Bottom)

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
        self._fen_editor.setText(self._game.board.fen())

    def display_chess_opening(self) -> None:
        """Display ECO code and chess opening name."""
        fen: str = self._game.board.fen()
        chess_openings_storage: dict[str, tuple[str, str]] = chess_openings()

        if fen in chess_openings_storage:
            eco_code, chess_opening_name = chess_openings_storage[fen]
            self._chess_opening_label.setText(
                f"{eco_code}: {chess_opening_name}"
            )

    def refresh_ui(self) -> None:
        """Refresh current state of UI."""
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

        if self._game.is_over():
            self._black_clock.stop_timer()
            self._white_clock.stop_timer()
            self._notifications_label.setText(self._game.result)
            self.offer_new_game()
            return

        if self._game.is_engine_on_turn() and not self._game.is_over():
            self.invoke_engine()

    def offer_new_game(self) -> None:
        """Show dialog offering to start new chess game."""
        answer: QMessageBox.StandardButton = QMessageBox.question(
            self,
            "New Game",
            "Do you want to start a new game?",
        )

        if answer == answer.Yes:
            self.start_new_game()

    def start_new_game(self) -> None:
        """Start new chess game by resetting everything."""
        if setting_value("board", "orientation") == BLACK:
            self.flip()

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
        """Ask whether to quit ReChess by closing main window."""
        answer: QMessageBox.StandardButton = QMessageBox.question(
            self,
            "Quit",
            "Do you want to quit ReChess?",
        )

        if answer == answer.Yes:
            self._engine.quit()
            event.accept()
        else:
            event.ignore()

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Select notation item on mouse wheel roll."""
        is_upward_roll = event.angleDelta().y() > 0
        is_downward_roll = event.angleDelta().y() < 0

        if is_upward_roll:
            self._table_view.select_previous_item()
        elif is_downward_roll:
            self._table_view.select_next_item()

    @Slot(Move)
    def on_best_move_analyzed(self, best_move: Move) -> None:
        """Show `best_move` from chess engine analysis as arrow."""
        self._game.set_arrow(best_move)
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
        """Refresh UI after FEN has been validated."""
        self.refresh_ui()

    @Slot(int)
    def on_item_selected(self, ply_index: int) -> None:
        """Set move from `ply_index`."""
        if ply_index > -1:
            self._game.set_move(ply_index)
        else:
            self._game.clear_arrows()
            self._game.set_root_position()
            self._chess_opening_label.clear()

        self.show_fen()
        self.adjust_engine_buttons()

        self._svg_board.draw()

    @Slot(Move)
    def on_move_played(self, move: Move) -> None:
        """Play `move` by pushing it and refreshing UI."""
        if self._game.is_legal(move):
            self._game.delete_data_after(self._table_view.ply_index)
            self._game.push(move)
            self.refresh_ui()

    @Slot(str)
    def on_variation_analyzed(self, variation: str) -> None:
        """Show `variation` from chess engine analysis."""
        self._engine_analysis_label.setText(variation)

    @Slot(Score)
    def on_score_analyzed(self, score: Score) -> None:
        """Show chessboard position evaluation from `score`."""
        self._evaluation_bar.animate(score)
